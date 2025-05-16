import csv
import itertools
from collections import Counter
import statistics

def analyze_ruozhiba(csv_path):
    char_lengths = []
    word_lengths = []
    pair_counter = Counter()
    label_counter = Counter()

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            sentence = row[1].strip().strip('"')
            char_len = len(sentence)
            word_len = len(sentence.split())

            char_lengths.append(char_len)
            word_lengths.append(word_len)


            raw_labels = row[2].strip().strip('"')
            labels = [lab.strip().lower() for lab in raw_labels.split(',') if lab.strip()]

   
            label_counter.update(labels)
   
            if len(labels) > 1:
                for a, b in itertools.combinations(sorted(labels), 2):
                    pair_counter[(a, b)] += 1


    avg_char = statistics.mean(char_lengths) if char_lengths else 0
    std_char = statistics.pstdev(char_lengths) if char_lengths else 0
    avg_word = statistics.mean(word_lengths) if word_lengths else 0
    std_word = statistics.pstdev(word_lengths) if word_lengths else 0


    print(f"mean char：{avg_char:.2f}, std{std_char:.2f}")
    print(f"meanword：{avg_word:.2f} std{std_word:.2f}\n")

    for (a, b), count in pair_counter.most_common():
        print(f"- {a} & {b}: {count} times")
    if not pair_counter:
        print("(no pairs found)")
    print()

    for label, count in label_counter.most_common():
        print(f"- {label}: {count} times")

if __name__ == '__main__':
    csv_file = "ruozhiba_label_modified.csv"
    analyze_ruozhiba(csv_file)