import json

with open("results/traces_strategy_a.json", "r", encoding="utf-8") as f:
    traces_a = json.load(f)
with open("results/traces_strategy_b.json", "r", encoding="utf-8") as f:
    traces_b = json.load(f)
with open("results/traces_strategy_c.json", "r", encoding="utf-8") as f:
    traces_c = json.load(f)

print("=== 5 TEST QUESTIONS AUDIT ===")
test_ids = ["q16", "q17", "q18", "q19", "q20"]

for qid in test_ids:
    ta = next(t for t in traces_a if t["question_id"] == qid)
    tb = next(t for t in traces_b if t["question_id"] == qid)
    tc = next(t for t in traces_c if t["question_id"] == qid)
    
    print(f"\n--- {qid}: {ta['question']} (Gold Page {ta['gold_page']}) ---")
    print(f"Strat A Hit1={ta['hit_1']}, Hit3={ta['hit_3']} | Top1 Page: {ta['hits'][0]['page']} (Score: {ta['hits'][0]['score']})")
    print(f"Strat B Hit1={tb['hit_1']}, Hit3={tb['hit_3']} | Top1 Page: {tb['hits'][0]['page']} (Score: {tb['hits'][0]['score']})")
    print(f"Strat C Hit1={tc['hit_1']}, Hit3={tc['hit_3']} | Top1 Page: {tc['hits'][0]['page']} (Score: {tc['hits'][0]['score']})")
    if qid == "q16":
        print(f"  Q16 Filter Applied in C: {tc['filter_applied']}")
        print(f"  Q16 Top 3 Pages in B: {[h['page'] for h in tb['hits']]}")
        print(f"  Q16 Top 3 Pages in C: {[h['page'] for h in tc['hits']]}")
        print(f"  Q16 Top 3 Chapters in C: {[h['metadata'].get('chapter') for h in tc['hits']]}")

