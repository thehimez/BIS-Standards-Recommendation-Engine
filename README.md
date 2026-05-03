# 🏗️ BIS Standards Recommendation Engine

<p align="center">
  <b>AI-powered system to instantly recommend BIS standards from natural language queries</b><br/>
  Built for <b>Bureau of Indian Standards × Sigma Squad AI Hackathon</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Accuracy-100%25%20Hit%40%203-brightgreen"/>
  <img src="https://img.shields.io/badge/MRR%405-0.78-blue"/>
  <img src="https://img.shields.io/badge/Latency-30ms-orange"/>
  <img src="https://img.shields.io/badge/CPU-Only-success"/>
  <img src="https://img.shields.io/badge/Status-Production%20Ready-black"/>
</p>

---

## 🚀 Run This Project (2-Min Setup)

### ⚠️ Requirements

* Python **3.11 or higher** (recommended)
* pip installed

---

### 1. Clone Repository

```bash
git clone https://github.com/thehimez/BIS-Standards-Recommendation-Engine.git
cd BIS-Standards-Recommendation-Engine
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Run the Web App

```bash
streamlit run app.py
```

---

### 4. Open in Browser

http://localhost:8501

---

## ⚡ Notes

* First run may take ~10–15 seconds (model warmup)
* Runs fully on CPU (no GPU required)
* No external APIs used

---

## 🌐 Live Demo

https://bisstandardrecomender.streamlit.app/

---

## 🎯 What This Project Does

Finding the correct BIS standard can take **2–6 weeks**.

This system reduces it to **milliseconds**.

👉 Input:
"33 Grade Ordinary Portland Cement"

👉 Output:
Top relevant BIS standards (IS 269:1989 + others) with rationale

---

## 🧠 How It Works

### Hybrid Retrieval Engine

* BM25 (keyword precision)
* TF-IDF (term importance)
* SBERT embeddings (semantic understanding)
* Keyword boost (IS number matching)

### Smart Chunking

* 556 standards extracted from BIS SP 21
* Each chunk = one complete standard

### Fast Retrieval

* FAISS + BM25 indexing
* ~30ms response time

---

## 📊 Performance

| Metric      | Result |
| ----------- | ------ |
| Hit Rate @3 | 100%   |
| MRR @5      | 0.783  |
| Avg Latency | ~30 ms |

---

## 🛠️ Tech Stack

* Python
* Streamlit
* FAISS
* Sentence Transformers (SBERT)
* BM25 (rank_bm25)
* scikit-learn
* PyMuPDF

---

## 📁 Project Structure

```
bis-rag/
├── app.py
├── inference.py
├── eval_script.py
├── requirements.txt
├── src/
├── data/
└── .cache/
```

---

## ▶️ Run Evaluation (Optional)

```bash
python inference.py --input data/public_test_set.json --output results.json
python eval_script.py --results results.json
```

---

## 💡 Why This Matters

* Eliminates weeks of compliance research
* Reduces dependency on consultants
* Scalable to 19,000+ BIS standards
* Enables self-serve compliance for MSMEs

---

## 🏆 Hackathon Context

* Problem: BIS standard discovery
* Constraint: <5 sec latency
* Achieved: ~30 ms ⚡

---

## 👤 Author

Himesh Bhowmik
Built end-to-end during hackathon

---

## ⭐ If you found this useful, consider starring the repo!
