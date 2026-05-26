import json, numpy as np
from rich import print
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from lib.paths import CACHE
from lib.cache import stamp, fresh, mark

IN  = CACHE / "quote_candidates.jsonl"
OUT = CACHE / "ranked_candidates.jsonl"
K   = 500


def run(force: bool = False):
    s = stamp("s4", [IN])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]"); return
    cands = [json.loads(l) for l in IN.read_text().splitlines()]
    texts = [c["text"] for c in cands]
    print(f"  [dim]embedding {len(texts):,} texts[/dim]")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embs = model.encode(texts, batch_size=128, show_progress_bar=True, convert_to_numpy=True)
    k = min(K, len(texts) // 5)
    km = KMeans(n_clusters=k, n_init=4, random_state=42).fit(embs)
    centers = km.cluster_centers_
    labels = km.labels_
    dists = np.linalg.norm(embs - centers[labels], axis=1)
    by_cluster: dict[int, list] = {}
    for i, (c, d) in enumerate(zip(labels, dists)):
        by_cluster.setdefault(int(c), []).append((float(d), i))
    picked = []
    for c, arr in by_cluster.items():
        arr.sort()
        for _, idx in arr[:3]:
            r = dict(cands[idx]); r["cluster"] = c
            picked.append(r)
    with OUT.open("w") as f:
        for r in picked:
            f.write(json.dumps(r) + "\n")
    mark(s)
    print(f"  [green]{len(picked):,} ranked candidates from {k} clusters[/green]")
