# BIS Standards Recommendation Engine

A production-ready RAG pipeline recommending relevant BIS standards for building materials.

## Quick Start
```bash
pip install -r requirements.txt
python inference.py --input data/public_test_set.json --output results.json
python eval_script.py --results results.json
```

## Results
- Hit Rate @3: 100% (Target: >80%)
- MRR @5: 0.7833 (Target: >0.7)
- Avg Latency: 0.03s (Target: <5s)
