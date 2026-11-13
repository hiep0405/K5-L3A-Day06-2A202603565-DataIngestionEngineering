"""Orchestrate the Day 06 Data Ingestion Engineering Pipeline."""
from pathlib import Path
import json
import time
import shutil
from .ingestion import load_pdf
from .chunking import fixed_size, by_paragraph
from .embeddings import MyEmbedder
from .store import ChromaVectorStore
from .evaluation import evaluate_query, summarize


def main() -> None:
    root_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = root_dir / "data"
    results_dir = root_dir / "results"
    starter_results_dir = Path(__file__).resolve().parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    starter_results_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = data_dir / "bo_luat_lao_dong_2019_clean.pdf"
    benchmark_path = root_dir / "benchmark" / "questions.json"
    
    print("=" * 60)
    print("DAY 06 · DATA INGESTION ENGINEERING PIPELINE")
    print("=" * 60)
    
    # 1. Ingestion
    print(f"\n[1/5] Loading corpus from: {pdf_path.name}")
    start_ingest = time.time()
    pages = load_pdf(pdf_path, document_id="bo-luat-lao-dong-2019", source=pdf_path.name)
    ingest_time = round(time.time() - start_ingest, 2)
    print(f"Loaded {len(pages)} physical pages in {ingest_time}s.")
    
    # 2. Chunking
    print("\n[2/5] Generating chunks for Strategies A, B, and C...")
    # Strategy A: Fixed-size 500 chars, overlap 50 chars
    chunks_a = []
    for p in pages:
        chunks_a.extend(fixed_size(p, size=500, overlap=50))
        
    # Strategy B & C: Structure-aware by paragraph/article, max_size 600
    chunks_b = []
    for p in pages:
        chunks_b.extend(by_paragraph(p, max_size=600))
        
    chunks_c = chunks_b  # C uses identical chunks to B to strictly isolate metadata filter effect
    
    lens_a = [len(c.text) for c in chunks_a]
    lens_b = [len(c.text) for c in chunks_b]
    
    print(f"Strategy A (Fixed 500/50): {len(chunks_a)} chunks | Avg length: {sum(lens_a)/len(lens_a):.1f} chars (Min: {min(lens_a)}, Max: {max(lens_a)})")
    print(f"Strategy B & C (Structure): {len(chunks_b)} chunks | Avg length: {sum(lens_b)/len(lens_b):.1f} chars (Min: {min(lens_b)}, Max: {max(lens_b)})")
    
    # 3. Embedding Model
    print("\n[3/5] Initializing local semantic embedding model...")
    embedder = MyEmbedder("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    print(f"Model: {embedder.model_name} | Dimensions: {embedder.dimensions}")
    
    # Compute embeddings
    print("Embedding Strategy A chunks...")
    t0 = time.time()
    vectors_a = embedder.embed_documents([c.text for c in chunks_a])
    emb_time_a = round(time.time() - t0, 2)
    print(f"Embedded {len(vectors_a)} chunks for A in {emb_time_a}s.")
    
    print("Embedding Strategy B & C chunks...")
    t0 = time.time()
    vectors_b = embedder.embed_documents([c.text for c in chunks_b])
    emb_time_b = round(time.time() - t0, 2)
    print(f"Embedded {len(vectors_b)} chunks for B & C in {emb_time_b}s.")
    
    # 4. Storage & Indexing
    print("\n[4/5] Storing and indexing in persistent ChromaDB...")
    store = ChromaVectorStore(persist_directory=str(root_dir / "chroma_db"), dimensions=embedder.dimensions)
    store.create_schema()
    
    store.upsert("A", chunks_a, vectors_a)
    store.upsert("B", chunks_b, vectors_b)
    store.upsert("C", chunks_c, vectors_b)
    print("All collections (A, B, C) indexed successfully.")
    
    # 5. Benchmark Retrieval & Evaluation
    print("\n[5/5] Running Benchmark on 20 questions (15 dev / 5 test)...")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        questions = json.load(f)
        
    print(f"Loaded {len(questions)} questions from {benchmark_path.name}.")
    
    strategies = [
        {"name": "A", "use_filter": False, "desc": "Fixed-size 500/50, No filter"},
        {"name": "B", "use_filter": False, "desc": "Structure-aware paragraph/article, No filter"},
        {"name": "C", "use_filter": True,  "desc": "Structure-aware + Metadata chapter filter"}
    ]
    
    all_summaries = {}
    
    for strat in strategies:
        strat_name = strat["name"]
        use_filter = strat["use_filter"]
        traces = []
        
        t_start = time.time()
        for q in questions:
            q_vec = embedder.embed_query(q["question"])
            filter_arg = q.get("filter") if use_filter else None
            hits = store.search(strat_name, q_vec, top_k=3, filters=filter_arg)
            trace = evaluate_query(q, hits)
            traces.append(trace)
            
        elapsed_retrieval = round(time.time() - t_start, 2)
        summary = summarize(traces)
        summary["time_seconds"] = elapsed_retrieval
        summary["chunk_count"] = len(chunks_a) if strat_name == "A" else len(chunks_b)
        summary["cost_usd"] = 0.0
        all_summaries[strat_name] = summary
        
        # Save traces
        trace_file = results_dir / f"traces_strategy_{strat_name.lower()}.json"
        with open(trace_file, "w", encoding="utf-8") as f:
            json.dump(traces, f, ensure_ascii=False, indent=2)
        shutil.copy(trace_file, starter_results_dir / f"traces_strategy_{strat_name.lower()}.json")
        
        dev_s = summary["dev"]
        test_s = summary["test"]
        print(f"\n--- Strategy {strat_name} ({strat['desc']}) ---")
        print(f"  Dev Split  : Hit@1 = {dev_s['hit1']}/{dev_s['total']} ({dev_s['hit1_rate']*100:.1f}%) | Hit@3 = {dev_s['hit3']}/{dev_s['total']} ({dev_s['hit3_rate']*100:.1f}%)")
        print(f"  Test Split : Hit@1 = {test_s['hit1']}/{test_s['total']} ({test_s['hit1_rate']*100:.1f}%) | Hit@3 = {test_s['hit3']}/{test_s['total']} ({test_s['hit3_rate']*100:.1f}%)")
        print(f"  Time: {elapsed_retrieval}s | Cost: $0.0")

    # Save summary
    summary_file = results_dir / "benchmark_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, ensure_ascii=False, indent=2)
    shutil.copy(summary_file, starter_results_dir / "benchmark_summary.json")

    # Update experiment_log.csv
    exp_log_path = root_dir / "artifacts" / "experiment_log.csv"
    with open(exp_log_path, "w", encoding="utf-8") as f:
        f.write("strategy,chunking,chunk_size,overlap,metadata,filter,vectorizer,hypothesis,dev_hit1,dev_hit3,test_hit1,test_hit3,notes\n")
        f.write(f"A,fixed_size,500,50,\"source,page,chapter\",none,sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2,Fixed window baseline,{all_summaries['A']['dev']['hit1_rate']},{all_summaries['A']['dev']['hit3_rate']},{all_summaries['A']['test']['hit1_rate']},{all_summaries['A']['test']['hit3_rate']},Baseline fixed chunking without metadata filter\n")
        f.write(f"B,by_paragraph,600,0,\"source,page,chapter\",none,sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2,Structure chunking preserves complete provisions,{all_summaries['B']['dev']['hit1_rate']},{all_summaries['B']['dev']['hit3_rate']},{all_summaries['B']['test']['hit1_rate']},{all_summaries['B']['test']['hit3_rate']},Improved coherence and boundary alignment\n")
        f.write(f"C,by_paragraph,600,0,\"source,page,chapter\",chapter_filter,sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2,Metadata filter narrows search space and removes cross-chapter noise,{all_summaries['C']['dev']['hit1_rate']},{all_summaries['C']['dev']['hit3_rate']},{all_summaries['C']['test']['hit1_rate']},{all_summaries['C']['test']['hit3_rate']},Eliminates false positives across different legal chapters\n")
        
    print("\nExperiment log updated at artifacts/experiment_log.csv.")
    print("Results and traces saved to results/ directory.")
    print("=" * 60)
    print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
