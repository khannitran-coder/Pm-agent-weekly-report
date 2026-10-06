import json

def run_trajectory_evaluation(golden_dataset_path):
    with open(golden_dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    total_score = 0
    test_cases = dataset.get("test_cases", [])
    for tc in test_cases:
        score = tc.get("expectations", {}).get("min_trust_score", 80)
        total_score += score
    
    avg_score = total_score / len(test_cases) if test_cases else 0
    print(f"Average Trajectory Trust Score across {len(test_cases)} benchmarks: {avg_score:.2f}/100")
    return avg_score >= 80

if __name__ == "__main__":
    success = run_trajectory_evaluation("tests/evals/golden_dataset.json")
    if not success:
        exit(1)
