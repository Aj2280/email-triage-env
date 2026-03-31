import os
import argparse

def run_mock_inference(base_url):
    print(f"MOCK: Running inference on {base_url}")
    # Simulate scores for all 3 tasks
    scores = {
        "task_easy": 1.0,
        "task_medium": 0.8,
        "task_hard": 0.5
    }
    return scores

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    
    results = run_mock_inference(args.base_url)
    print("Mock results:", results)
