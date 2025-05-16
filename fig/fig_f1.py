import matplotlib.pyplot as plt
import matplotlib as mpl

# Set global font style
mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 16

# Model names and F1 scores
models = [
    "deepseek v3", "llama3.1 405b", "o3 mini", "qwen 3 ex", "qwen 3",
    "grok 2", "grok 3 mini", "grok 3 mini ex", "claude 3.7",
    "o4 mini", "gpt 4o", "claude 3.7 ex", "grok 3",
    "deepseek r1", "claude 3.5 sonnet", "gemini 2.5 pro", "gemini 2.5 pro ex"
]

f1_scores = [
    0.926, 0.907, 0.903, 0.899, 0.895,
    0.896, 0.894, 0.894, 0.888,
    0.890, 0.855, 0.862, 0.844,
    0.843, 0.821, 0.739, 0.733
]

# Soft anime-style colors (non-repetitive, colorblind friendly)
anime_soft_colors = [
    "#2e2e2e",  # deepseek v3
    "#cccccc",  # llama3.1 405b
    "#bfbfbf",  # o3 mini
    "#8a8a8a",  # qwen 3 ex
    "#9e9e9e",  # qwen 3
    "#595959",  # grok 2
    "#414141",  # grok 3 mini
    "#363636",  # grok 3 mini ex
    "#8c8c8c",  # claude 3.7
    "#a6a6a6",  # o4 mini
    "#d9d9d9",  # gpt
    "#7a7a7a",  # claude 3.7 ex
    "#4d4d4d",  # grok 3
    "#1f1f1f",  # deepseek r1
    "#6b6b6b",  # claude 3.5 sonnet
    "#5c5c5c",  # gemini 2.5 pro
    "#4a4a4a",  # gemini 2.5 pro ex
]

data = list(zip(f1_scores, models, anime_soft_colors))
data.sort(key=lambda x: x[0], reverse=True)  # x[0] is score

sorted_scores, sorted_models, sorted_colors = zip(*data)

plt.figure(figsize=(14, 5))
bars = []
for model, score, color in zip(sorted_models, sorted_scores, sorted_colors):
    bars.append(plt.bar(model, score, color=color))

plt.xticks(rotation=45, ha='right')
plt.ylabel("F1 Score")
plt.title("F1 Score by Model")

plt.margins(x=0.01)
plt.subplots_adjust(left=0.05, right=0.95)

plt.grid(True, axis='y', linestyle='--', alpha=0.5)
plt.grid(True, axis='x', linestyle='--', alpha=0.5)

plt.ylim(0.7, 0.95)

for bar, score in zip(bars, sorted_scores):
    x = bar[0].get_x() + bar[0].get_width() / 2
    y = bar[0].get_height()
    plt.text(x, y + 0.003, f"{score:.3f}", ha='center', va='bottom', fontsize=14)

plt.tight_layout()
plt.savefig("fig_f1.pdf", format="pdf", dpi=500)
plt.close()