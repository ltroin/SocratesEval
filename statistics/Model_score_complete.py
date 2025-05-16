import json
import glob
import os
from collections import Counter

def analyze_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scores = [int(item["score"]) for item in data if str(item.get("score", "")).isdigit()]
    total = len(scores)
    score_counts = Counter(scores)

    print(f"== {os.path.basename(filename)} ==")
    for score in sorted(score_counts.keys(), reverse=True):
        count = score_counts[score]
        print(f"Score {score}: {count} ({count/total*100:.2f}%)")
    print(f"Total: {total}\n")


def main():
    #note, this is inside evaluation folder, put here for consistency
    pattern = f"*_evalres_by_*.json"
    file_list = glob.glob(pattern)
    if not file_list:
        print("No matching file was found, please check if the corresponding output exists in the current directory")
        return

    for filepath in sorted(file_list):
        analyze_file(filepath)


if __name__ == "__main__":
    main()
