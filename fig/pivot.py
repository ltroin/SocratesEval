import pandas as pd

# DataFrame
df = pd.DataFrame([
    # GPT Series
    {'Model': 'gpt 4o', 'Evaluator': 'DeepSeek R1', 'Score2': 63.33},
    {'Model': 'gpt 4o', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 57.10},
    {'Model': 'gpt 4o', 'Evaluator': 'GPT 4o', 'Score2': 69.15},
    {'Model': 'gpt 4o', 'Evaluator': 'o4 mini', 'Score2': 70.17},
    {'Model': 'gpt 4o', 'Evaluator': 'Qwen 3 Ex', 'Score2': 53.01},

    {'Model': 'o3 mini', 'Evaluator': 'DeepSeek R1', 'Score2': 56.49},
    {'Model': 'o3 mini', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 51.48},
    {'Model': 'o3 mini', 'Evaluator': 'GPT 4o', 'Score2': 67.42},
    {'Model': 'o3 mini', 'Evaluator': 'o4 mini', 'Score2': 69.97},
    {'Model': 'o3 mini', 'Evaluator': 'Qwen 3 Ex', 'Score2': 51.38},

    {'Model': 'o4 mini', 'Evaluator': 'DeepSeek R1', 'Score2': 66.80},
    {'Model': 'o4 mini', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 61.90},
    {'Model': 'o4 mini', 'Evaluator': 'GPT 4o', 'Score2': 68.74},
    {'Model': 'o4 mini', 'Evaluator': 'o4 mini', 'Score2': 72.22},
    {'Model': 'o4 mini', 'Evaluator': 'Qwen 3 Ex', 'Score2': 52.20},

    # Claude Series
    {'Model': 'claude 3.5 sonnet', 'Evaluator': 'DeepSeek R1', 'Score2': 55.26},
    {'Model': 'claude 3.5 sonnet', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 42.29},
    {'Model': 'claude 3.5 sonnet', 'Evaluator': 'GPT 4o', 'Score2': 56.38},
    {'Model': 'claude 3.5 sonnet', 'Evaluator': 'o4 mini', 'Score2': 59.96},
    {'Model': 'claude 3.5 sonnet', 'Evaluator': 'Qwen 3 Ex', 'Score2': 36.06},

    {'Model': 'claude 3.7 sonnet thinking', 'Evaluator': 'DeepSeek R1', 'Score2': 81.10},
    {'Model': 'claude 3.7 sonnet thinking', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 67.21},
    {'Model': 'claude 3.7 sonnet thinking', 'Evaluator': 'GPT 4o', 'Score2': 78.96},
    {'Model': 'claude 3.7 sonnet thinking', 'Evaluator': 'o4 mini', 'Score2': 75.38},
    {'Model': 'claude 3.7 sonnet thinking', 'Evaluator': 'Qwen 3 Ex', 'Score2': 67.93},

    {'Model': 'claude 3.7 sonnet', 'Evaluator': 'DeepSeek R1', 'Score2': 80.59},
    {'Model': 'claude 3.7 sonnet', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 69.15},
    {'Model': 'claude 3.7 sonnet', 'Evaluator': 'GPT 4o', 'Score2': 78.45},
    {'Model': 'claude 3.7 sonnet', 'Evaluator': 'o4 mini', 'Score2': 76.10},
    {'Model': 'claude 3.7 sonnet', 'Evaluator': 'Qwen 3 Ex', 'Score2': 69.87},

    # DeepSeek Series
    {'Model': 'deepseek v3', 'Evaluator': 'DeepSeek R1', 'Score2': 72.22},
    {'Model': 'deepseek v3', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 59.24},
    {'Model': 'deepseek v3', 'Evaluator': 'GPT 4o', 'Score2': 72.83},
    {'Model': 'deepseek v3', 'Evaluator': 'o4 mini', 'Score2': 71.40},
    {'Model': 'deepseek v3', 'Evaluator': 'Qwen 3 Ex', 'Score2': 57.30},

    {'Model': 'deepseek r1', 'Evaluator': 'DeepSeek R1', 'Score2': 78.45},
    {'Model': 'deepseek r1', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 62.92},
    {'Model': 'deepseek r1', 'Evaluator': 'GPT 4o', 'Score2': 76.92},
    {'Model': 'deepseek r1', 'Evaluator': 'o4 mini', 'Score2': 69.56},
    {'Model': 'deepseek r1', 'Evaluator': 'Qwen 3 Ex', 'Score2': 65.47},

    # Gemini Series
    {'Model': 'gemini 2.5 pro thinking', 'Evaluator': 'DeepSeek R1', 'Score2': 76.30},
    {'Model': 'gemini 2.5 pro thinking', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 67.82},
    {'Model': 'gemini 2.5 pro thinking', 'Evaluator': 'GPT 4o', 'Score2': 73.14},
    {'Model': 'gemini 2.5 pro thinking', 'Evaluator': 'o4 mini', 'Score2': 77.83},
    {'Model': 'gemini 2.5 pro thinking', 'Evaluator': 'Qwen 3 Ex', 'Score2': 53.42},

    {'Model': 'gemini 2.5 pro', 'Evaluator': 'DeepSeek R1', 'Score2': 76.51},
    {'Model': 'gemini 2.5 pro', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 69.25},
    {'Model': 'gemini 2.5 pro', 'Evaluator': 'GPT 4o', 'Score2': 71.81},
    {'Model': 'gemini 2.5 pro', 'Evaluator': 'o4 mini', 'Score2': 77.94},
    {'Model': 'gemini 2.5 pro', 'Evaluator': 'Qwen 3 Ex', 'Score2': 51.69},

    # Grok Series
    {'Model': 'grok 2', 'Evaluator': 'DeepSeek R1', 'Score2': 67.42},
    {'Model': 'grok 2', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 53.63},
    {'Model': 'grok 2', 'Evaluator': 'GPT 4o', 'Score2': 65.17},
    {'Model': 'grok 2', 'Evaluator': 'o4 mini', 'Score2': 68.03},
    {'Model': 'grok 2', 'Evaluator': 'Qwen 3 Ex', 'Score2': 44.74},

    {'Model': 'grok 3 mini thinking', 'Evaluator': 'DeepSeek R1', 'Score2': 68.85},
    {'Model': 'grok 3 mini thinking', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 59.35},
    {'Model': 'grok 3 mini thinking', 'Evaluator': 'GPT 4o', 'Score2': 67.31},
    {'Model': 'grok 3 mini thinking', 'Evaluator': 'o4 mini', 'Score2': 70.79},
    {'Model': 'grok 3 mini thinking', 'Evaluator': 'Qwen 3 Ex', 'Score2': 48.21},

    {'Model': 'grok 3 mini', 'Evaluator': 'DeepSeek R1', 'Score2': 69.05},
    {'Model': 'grok 3 mini', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 59.55},
    {'Model': 'grok 3 mini', 'Evaluator': 'GPT 4o', 'Score2': 67.01},
    {'Model': 'grok 3 mini', 'Evaluator': 'o4 mini', 'Score2': 70.79},
    {'Model': 'grok 3 mini', 'Evaluator': 'Qwen 3 Ex', 'Score2': 46.88},

    {'Model': 'grok 3', 'Evaluator': 'DeepSeek R1', 'Score2': 75.89},
    {'Model': 'grok 3', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 65.07},
    {'Model': 'grok 3', 'Evaluator': 'GPT 4o', 'Score2': 78.96},
    {'Model': 'grok 3', 'Evaluator': 'o4 mini', 'Score2': 75.89},
    {'Model': 'grok 3', 'Evaluator': 'Qwen 3 Ex', 'Score2': 56.59},

    # LLaMA Series
    {'Model': 'llama 3.1 405b', 'Evaluator': 'DeepSeek R1', 'Score2': 68.85},
    {'Model': 'llama 3.1 405b', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 57.20},
    {'Model': 'llama 3.1 405b', 'Evaluator': 'GPT 4o', 'Score2': 66.50},
    {'Model': 'llama 3.1 405b', 'Evaluator': 'o4 mini', 'Score2': 67.72},
    {'Model': 'llama 3.1 405b', 'Evaluator': 'Qwen 3 Ex', 'Score2': 49.13},

    # Qwen Series
    {'Model': 'qwen 3 thinking', 'Evaluator': 'DeepSeek R1', 'Score2': 63.33},
    {'Model': 'qwen 3 thinking', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 51.17},
    {'Model': 'qwen 3 thinking', 'Evaluator': 'GPT 4o', 'Score2': 63.33},
    {'Model': 'qwen 3 thinking', 'Evaluator': 'o4 mini', 'Score2': 64.25},
    {'Model': 'qwen 3 thinking', 'Evaluator': 'Qwen 3 Ex', 'Score2': 44.74},

    {'Model': 'qwen 3', 'Evaluator': 'DeepSeek R1', 'Score2': 64.25},
    {'Model': 'qwen 3', 'Evaluator': 'Gemini 2.5 Pro Ex', 'Score2': 50.87},
    {'Model': 'qwen 3', 'Evaluator': 'GPT 4o', 'Score2': 63.53},
    {'Model': 'qwen 3', 'Evaluator': 'o4 mini', 'Score2': 65.27},
    {'Model': 'qwen 3', 'Evaluator': 'Qwen 3 Ex', 'Score2': 43.82},
])

pivot = df.pivot(index='Model', columns='Evaluator', values='Score2')

average_scores = pivot.mean(axis=1).round(3)

min_score = average_scores.min()
max_score = average_scores.max()
normalized_scores = ((average_scores - min_score) / (max_score - min_score)).round(3)

result_df = pd.DataFrame({
    'Model': average_scores.index,
    'Average Score2': average_scores.values,
    'Normalized Score': normalized_scores.values
})

print(result_df)