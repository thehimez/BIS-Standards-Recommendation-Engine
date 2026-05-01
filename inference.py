from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rag_pipeline import BISRAGPipeline 


def run(input_path: str, output_path: str, top_k: int = 5) -> None:
    with open(input_path) as f:
        items = json.load(f)
    if not isinstance(items, list):
        raise ValueError("Input JSON must be a list of {id, query} objects")

    print(f"Loaded {len(items)} queries from {input_path}")

    pipeline = BISRAGPipeline()
    t0 = time.time()
    pipeline.load()
    print(f"Pipeline ready in {time.time() - t0:.2f}s")

    results = []
    total_latency = 0.0
    for it in items:
        qid = it.get("id")
        query = it.get("query", "")
        retrieved, latency = pipeline.predict_with_latency(query, top_k=top_k)
        total_latency += latency
        out = {
            "id": qid,
            "query": query,
            "retrieved_standards": retrieved,
            "latency_seconds": round(latency, 4),
        }
        
        if "expected_standards" in it:
            out["expected_standards"] = it["expected_standards"]
        results.append(out)
        print(
            f"  {qid:<8} {latency:5.3f}s  → {', '.join(retrieved[:3])}"
            + ("..." if len(retrieved) > 3 else "")
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    n = max(1, len(items))
    print()
    print(f"Wrote {len(results)} results → {output_path}")
    print(f"Average latency: {total_latency / n:.3f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="BIS Standards RAG inference")
    parser.add_argument("--input", required=True, help="Input JSON file path")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument("--top-k", type=int, default=5, help="Standards per query")
    args = parser.parse_args()
    run(args.input, args.output, top_k=args.top_k)


if __name__ == "__main__":
    main()
