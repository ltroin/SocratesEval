import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import FuncFormatter

mpl.rcParams['font.family'] = 'Times New Roman'
mpl.rcParams['font.size'] = 18

models = [
    "deepseek v3", "llama3.1 405b", "o3 mini", "qwen 3 ex", "qwen 3",
    "grok 2", "grok 3 mini", "grok 3 mini ex", "claude 3.7",
    "o4 mini", "gpt 4o", "claude 3.7 ex", "grok 3",
    "deepseek r1", "claude 3.5 sonnet", "gemini 2.5 pro", "gemini 2.5 pro ex"
]

f1_scores = [
    -850.253, -506.93, -355.898, -793.875, -811.122,
    -622.719, -1298.597, -1323.705, -526.909,
    -341.532, -810.217, -473.912, -1574.708,
    -521.672, -680.41, -334.864, -332.441
]

anime_soft_colors = {
    "#2e2e2e",  # deepseek v3           ← DeepSeek 系列（深灰）
    "#cccccc",  # llama3.1 405b         ← LLaMA 系列（亮灰）
    "#bfbfbf",  # o3 mini               ← GPT 系列（中亮灰）
    "#8a8a8a",  # qwen 3 ex             ← Qwen 系列（中灰）
    "#9e9e9e",  # qwen 3                ← Qwen 系列（中亮灰）
    "#595959",  # grok 2                ← Grok 系列（中偏深灰）
    "#414141",  # grok 3 mini           ← Grok 系列
    "#363636",  # grok 3 mini ex        ← Grok 系列
    "#8c8c8c",  # claude 3.7            ← Claude 系列（中灰）
    "#a6a6a6",  # o4 mini               ← GPT 系列
    "#d9d9d9",  # gpt 4o                ← GPT 系列（亮灰）
    "#7a7a7a",  # claude 3.7 ex         ← Claude 系列
    "#4d4d4d",  # grok 3                ← Grok 系列
    "#1f1f1f",  # deepseek r1           ← DeepSeek 系列（更深灰）
    "#6b6b6b",  # claude 3.5 sonnet     ← Claude 系列（更深灰）
    "#5c5c5c",  # gemini 2.5 pro        ← Gemini 系列
    "#4a4a4a",  # gemini 2.5 pro ex     ← Gemini 系列
}

# 1. 计算正高度，并把所有信息打包成列表
data = [
    (model, score, color, -score)
    for model, score, color in zip(models, f1_scores, anime_soft_colors)
]

data.sort(key=lambda x: x[3], reverse=False)

sorted_models, sorted_scores, sorted_colors, sorted_heights = zip(*data)

fig, ax = plt.subplots(figsize=(14, 5))
bars = ax.bar(
    range(len(sorted_models)),
    sorted_heights,
    color=sorted_colors
)

ax.set_xticks(range(len(sorted_models)))
ax.set_xticklabels(sorted_models, rotation=20, ha='right')
ax.set_ylabel("Fallacy Score")
ax.set_title("Fallacy Score by Model")

ax.set_ylim(0, 1700)
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{-x:.0f}"))

plt.margins(x=0.01)
plt.subplots_adjust(left=0.05, right=0.95)

offset = 80

for idx, h in enumerate(sorted_heights):
    x = idx
    y = h + offset
    ax.text(
        x, y,
        f"{-h:.3f}",
        ha='center',
        va='top',
        fontsize=14
    )
plt.grid(True, axis='y', linestyle='--', alpha=0.5)
plt.grid(True, axis='x', linestyle='--', alpha=0.5)

ax.axhline(0, color='black', linewidth=1)

plt.tight_layout()
plt.savefig("fig_fallacy.pdf", format="pdf", dpi=500)
plt.close()
