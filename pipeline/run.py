import argparse, importlib, sys
from rich import print

STAGES = ["s0_parse", "s1_stats", "s2_firsts", "s3_candidates",
          "s4_cluster", "s_nlp", "s_chapters", "s_chapters_emit_mdx",
          "s5_curate", "s6_intros"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", help="run a single stage (e.g. s0_parse)")
    p.add_argument("--from", dest="start", help="run from this stage onward")
    p.add_argument("--force", action="store_true", help="ignore cache")
    args = p.parse_args()

    selected = [args.stage] if args.stage else (
        STAGES[STAGES.index(args.start):] if args.start else STAGES)

    for s in selected:
        print(f"[bold cyan]→ {s}")
        mod = importlib.import_module(f"stages.{s}")
        mod.run(force=args.force)
    print("[bold green]done")

if __name__ == "__main__":
    sys.exit(main())
