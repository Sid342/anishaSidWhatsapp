import json
from lib.paths import CACHE

LEDGER = CACHE / "cost_ledger.jsonl"
HARD_CAP_USD = 1.00

PRICE = {
    "claude-haiku-4-5-20251001":        {"in": 1.00 / 1_000_000, "out": 5.00 / 1_000_000},
    "claude-haiku-4-5-20251001:cached": {"in": 0.10 / 1_000_000, "out": 5.00 / 1_000_000},
    "claude-sonnet-4-6":                {"in": 3.00 / 1_000_000, "out": 15.00 / 1_000_000},
}


def log(stage: str, model: str, in_tok: int, out_tok: int, cached_in_tok: int = 0):
    p = PRICE[model]
    cost = ((in_tok - cached_in_tok) * p["in"] +
            cached_in_tok * PRICE.get(model + ":cached", p)["in"] +
            out_tok * p["out"])
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps({"stage": stage, "model": model,
                            "in": in_tok, "out": out_tok, "cached": cached_in_tok,
                            "cost_usd": cost}) + "\n")
    total = sum(json.loads(l)["cost_usd"] for l in LEDGER.read_text().splitlines())
    if total > HARD_CAP_USD:
        raise RuntimeError(f"hard cap ${HARD_CAP_USD} exceeded: now ${total:.4f}")
    return cost, total
