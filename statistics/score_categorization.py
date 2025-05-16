import csv
import re
import json  # Import json module to write JSON output

def clean_value(value):
    """Remove surrounding double quotes if present and strip whitespace."""
    if value.startswith("\"\"") and value.endswith("\"\""):
        value = value[1:-1].strip()
    value = value.replace("’", "'").replace("`", "'")
    return value

def convert_inner_quotes(text):
    """Convert inner double quotes to single quotes, keeping outer quotes unchanged."""
    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", text)

temp = []

csv_fallacy_map = {}

with open("ruozhiba_label_modified.csv", 'r', encoding='utf-8') as csvfile:
# with open("generated_ruozhiba.csv", 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:                
        sentence = clean_value(row[1].strip())
        sentence = convert_inner_quotes(sentence)  # Apply the transformation
        fallacy_type = row[2].strip().strip('"')
        # sentence = clean_value(row[0].strip())
        # sentence = convert_inner_quotes(sentence)
        # fallacy_type = row[1].strip().strip('"')

        fallacy_list = [f.strip() for f in fallacy_type.split(',') if f.strip()]
        
        csv_fallacy_map[sentence] = fallacy_type
        
        temp.append(sentence)

# Save temp list as a JSON file
with open("list_ruozhiba.json", "w", encoding="utf-8") as f:
    json.dump(temp, f, ensure_ascii=False, indent=4)
# print(len(csv_fallacy_map))

def format_sentence(sentence):

    if sentence.startswith("\'") and sentence.endswith("\'"):
        sentence = sentence[1:-1].strip()
    sentence = sentence.replace("’", "'").replace("`", "'")

    return re.sub(r'(?<!^)"(.*?)(?<!^)"', r"'\1'", sentence)



diff_list = list(csv_fallacy_map.keys())

num_count = {}
def calculate_score(entry, csv_fallacy_map):
    score = 0.0
    logic_error = entry.get('logic error', '').lower()
    fallacies = entry.get('logic fallacies', [])
    
    # Convert string fallacies to list
    if isinstance(fallacies, str):
        fallacies = [f.strip().lower() for f in fallacies.split(',')]
    else:
        # print(entry.get('sentence'))
        fallacies = [f.lower() for f in fallacies]
    
    sentence = format_sentence(entry['sentence'])
    if sentence in diff_list:
            diff_list.remove(sentence)
    if logic_error == 'yes':
        # Get correct fallacy from CSV mapping
        correct_fallacy = csv_fallacy_map.get(sentence, '').lower()
        
        if not correct_fallacy:
            print(sentence)
            # pass
        # print(corre)
        # print(correct_fallacy)
        # print(fallacies)

        num_count[filename] = num_count.get(filename,0) + len(fallacies)

        for i, fallacy in enumerate(fallacies):
            # print(fallacy)
            weight = 1 / (i + 1)
            if fallacy in correct_fallacy:
                score += weight
            else:
                score -= weight
                
    elif logic_error == 'no':
        # Apply descending penalty series
        for i in range(13):
            score -= 1 / (i + 1)
            
    return round(score, 3)

results = {}
# Process JSON data

files=[
    "claude-3-7-sonnet-latest-thinking.json",
    "claude-3-7-sonnet-latest.json",
    "llama3.1-405b.json",
    "gemini-2.5-pro-preview-05-06-thinking.json",
    "qwen-plus-thinking.json",
    "gemini-2.5-pro-preview-05-06.json",
    "qwen-plus.json",
    "grok-3-beta.json",
    "deepseek-chat.json",
    "deepseek-reasoner.json",
    "claude-3-5-sonnet-latest.json",
    "grok-3-mini-beta.json",
    "grok-3-mini-beta-thinking.json",
    "grok-2.json",
    "o4-mini.json",
    "gpt-4o.json",
    "o3-mini.json"
]
for filename in files:
    # filename = filename.replace(".json", "_ruozhiba_since_original.json")
    # filename = filename.replace(".json", "_2_2.json")
    with open(filename, 'r', encoding='utf-8')  as f:
        data = json.load(f)

    final_score = 0
    for entry in data:
        score = calculate_score(entry, csv_fallacy_map)
        final_score += score

    results[filename] = round(final_score,3)

print(results)

print(diff_list)




print(num_count)