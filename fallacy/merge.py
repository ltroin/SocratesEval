import os
import json
import pandas as pd

# TODO: Set this to the path of your baseline JSON file (e.g. 'baseline.json' in your project root)
BASELINE_FILE = 'baseline.json'

# Start searching for explanation_{model}.json files from the current working directory
INPUT_DIR = os.getcwd()

# Save all merged outputs under the 'res' folder in the current working directory
OUTPUT_DIR = os.path.join(os.getcwd(), 'res')

def merge_and_save(baseline_file: str, other_file: str, model_name: str, output_dir: str):
    # Load baseline annotations
    with open(baseline_file, 'r', encoding='utf-8') as f:
        baseline = json.load(f)
    # Load model explanations
    with open(other_file, 'r', encoding='utf-8') as f:
        other = json.load(f)

    # Map each id to its corresponding entry in the model's explanations
    id_to_other = {item['id']: item for item in other}

    # Merge by matching ids
    merged = []
    for item in baseline:
        idx = item['id']
        if idx in id_to_other:
            merged.append({
                'id': idx,
                'sentence': item.get('sentence'),
                'label': item.get('label'),
                'explanation_baseline': item.get('explanation'),
                'explanation_candidate': id_to_other[idx].get('explanation')
            })

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write merged data to JSON
    json_out = os.path.join(output_dir, f'merged_{model_name}.json')
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=4)

    # Also save as CSV for convenience
    csv_out = os.path.join(output_dir, f'merged_{model_name}.csv')
    pd.DataFrame(merged).to_csv(csv_out, index=False, encoding='utf-8-sig')

    print(f'Done: {json_out} and {csv_out}')

def main():
    # Recursively walk through all subdirectories
    for root, _, files in os.walk(INPUT_DIR):
        for file in files:
            if file.startswith('explanation_') and file.endswith('.json'):
                other_file = os.path.join(root, file)
                # Extract model name from filename: explanation_{model}.json
                model_name = file[len('explanation_'):-len('.json')]
                merge_and_save(BASELINE_FILE, other_file, model_name, OUTPUT_DIR)

if __name__ == '__main__':
    main()
