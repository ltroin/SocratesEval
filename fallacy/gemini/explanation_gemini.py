import pandas as pd
import json
import asyncio
import time
from openai import AsyncOpenAI
import re
# ========== Configuration ==========
API_KEY = "YOUR-API"
BASE_URL = "YOUR-URL"
MAX_RETRIES = 250
RETRY_DELAY = 180  # seconds
MODEL = "gemini-2.5-pro-preview-05-06"
JSON = f'explanation_{MODEL}.json'

def extract_json(reply_text):
    import json, re
    match = re.search(r'\{.*\}', reply_text, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON object found")
    json_str = match.group()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        def escape_quotes(m):
            inner = m.group(1)
            inner = inner.replace('\\"', '\\\\"')
            inner = re.sub(r'(?<!\\)"', r'\\"', inner)
            return ':"{}"{}'.format(inner, m.group(2))

        repaired = re.sub(
            r':"(.*?)"(,|\})',
            escape_quotes,
            json_str,
            flags=re.DOTALL
        )

        return json.loads(repaired)
# def extract_json(reply_text):
#     match = re.search(r'{.*}', reply_text, re.DOTALL)
#     if match:
#         return json.loads(match.group())
#     raise ValueError("No valid JSON object found")

# ========== Load CSV ==========
df = pd.read_csv("../baseline.csv")

# ========== Label Ordering for Sorting ==========
definitions_order = [
    "False dilemma", "Equivocation", "False Premise", "False Analogy", "Wrong Direction",
    "Fallacy of composition", "Begging the question", "False Cause", "Inverse Error",
    "Improper transposition", "Improper Distribution or Addition", "Contextomy",
    "Nominal Fallacy", "Accident fallacy"
]

def get_sort_index(label):
    primary = label.split(',')[0].strip()
    return definitions_order.index(primary) if primary in definitions_order else float('inf')


logical_fallacy_prompt = """
You are reading a sentence that contains flawed reasoning.
Your task is to explain, in a natural and human way, why the sentence's logic doesn't make sense.
Be brief, natural, and clear — just like how a thoughtful person would explain it to a friend.
"""
# You are a professional evaluator of logical fallacies. Your task is to critically assess each sentence in a given dataset, where each sentence is annotated with one or more logical fallacy labels.
#
# For each sentence:
#
# 1. Explain clearly and precisely why the sentence exhibits the fallacy or fallacies indicated by its `label` field.
# 2. Your explanation must refer to the formal definition of the fallacy and demonstrate how the sentence meets that definition—but you do not need to name the fallacy in your explanation.
# 3. Identify the implicit or explicit premises and conclusions, show how the reasoning deviates from valid argumentation, and point out any linguistic tricks, false comparisons, causal errors, or ambiguities used.
# 4. Keep each explanation concise—no more than three or four sentences—and grounded in real-world human reasoning and communication.
# 5. Avoid vague summaries or value judgments; focus solely on how the labelled fallacy applies.
#
# Tone: Professional, analytic, and pedagogically clear.
# Purpose: To teach the reader why the given fallacy label fits each sentence.

# You are a professional evaluator of logical fallacies. Your task is to critically assess each sentence in a given dataset, where each sentence is annotated with one or more logical fallacy labels.
#
# For each sentence:
#
# 1. Explain clearly and precisely why the sentence exhibits the specific fallacy or fallacies indicated by the `label` field.
# 2. Your explanation must refer to the formal definition of the fallacy (definitions are provided below) and demonstrate how the sentence meets that definition.
# 3. Consider both the structure of reasoning and the semantic content. Be sure to:
#    - Identify the implicit or explicit premises and conclusions in the sentence.
#    - Analyse how the reasoning deviates from valid or sound argumentation.
#    - Indicate any linguistic tricks, false comparisons, causal misattributions, or ambiguities being employed.
# 4. Explanations must reflect real-world human reasoning and communication practices, not artificially contrived or overly abstract logic.
# 5. Avoid vague or superficial summaries. Comment on the sentence as a whole, logically and contextually aware, but do not judge whether the sentence is good or bad, only how the corresponding label is used.
# 6. You must not use code, symbolic logic, or statistics in your explanation — rely only on critical thinking and qualitative judgment.
#
# Tone: Professional, analytic, and pedagogically clear.
# Purpose: To teach or demonstrate or educate the reader *why* the fallacy label applies to the sentence.


fallacy_definitions = [
    "Definitions:"
    "False dilemma: The presentation of an issue as having only two possible outcomes, either right or wrong, without recognising that additional alternatives may exist.",
    "Equivocation: The misleading use of a word or phrase that has multiple meanings, creating ambiguity and leading to confusion in interpretation or reasoning.",
    "False Premise: The establishment of an argument based on an unfounded, non-existent, or unreasonable assumption, leading to flawed reasoning or invalid conclusions.",
    "False Analogy: The assumption that if A and B share certain characteristics, then B must also possess other attributes of A, despite lacking a valid basis for this inference.",
    "Wrong Direction: The incorrect attribution of causality by reversing the cause-and-effect relationship, assuming the effect is the cause and the cause is the effect.",
    "Fallacy of composition: The mistaken assumption that what is true for a part of something must also be true for the whole, disregarding the possible differences between individual components and the entire entity.",
    "Begging the question: The use of a statement as both the premise and the conclusion, assuming the truth of what is to be proven instead of providing independent support.",
    "False Cause: The incorrect assumption that a causal relationship exists between two events solely because one follows the other, failing to account for coincidence or other influencing factors.",
    "Inverse Error: The mistaken reasoning that if A implies B, then not A must imply not B, overlooking the possibility that B may still occur due to other factors.",
    "Improper transposition: The incorrect inference that if A implies B, then B must also imply A, failing to recognise that implication is not necessarily reversible.",
    "Improper Distribution or Addition: The erroneous reasoning that individual effects can be directly summed or distributed across a group without considering their actual impact or interaction.",
    "Contextomy: The act of selectively quoting or altering a statement, advertisement, or published material in a way that distorts its original meaning, often misrepresenting the intent of the original source.",
    "Nominal Fallacy: The mistaken interpretation of a metaphorical or figurative expression as a literal statement, leading to a misunderstanding of its intended meaning.",
    "Accident fallacy: The misapplication of a general rule to a specific case where exceptions should be considered, treating the rule as absolute without regard for context or relevant circumstances."
    "Self-Contradiction: The statement that directly negates its own truth rather than circularly assuming its conclusion as a premise."
]

# ========== System Prompt ==========
system_prompt = {
    "role": "system",
    "content": logical_fallacy_prompt
}

# ========== Evaluate One Sentence with Retry ==========
async def evaluate_with_retries(client, sentence, csv_id):
    user_prompt = {
        "role": "user",
        "content": f'Sentence: "{sentence}"\n'
                   'Return the result in this JSON format:'
                   '{"sentence":"...", "explanation":"..."}'
                   'Your output should conform to the format and syntax of JSON.'
                   'Note the legality of the json file and the need to escape internal quotes.'
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=0,
                messages=[system_prompt, user_prompt]
            )
            reply = response.choices[0].message.content.strip()
            parsed = extract_json(reply)
            parsed["id"] = csv_id
            return parsed
        except Exception as e:
            print(f"[Retry {attempt}/{MAX_RETRIES}] ID {csv_id} failed: {e}")
            await asyncio.sleep(RETRY_DELAY)

    return {
        "sentence": sentence,
        "Explanation": f"Failed after {MAX_RETRIES} retries.",
        "id": csv_id
    }

# ========== Main Async Processing Function ==========
async def main():
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

    tasks = [
        evaluate_with_retries(client, row["sentence"], row["id"])
        for _, row in df.iterrows()
    ]

    results = await asyncio.gather(*tasks)

    sorted_results = sorted(results, key=lambda x: x["id"])

    with open(f"{JSON}", "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, ensure_ascii=False, indent=2)

    print(f"All sentences scored and saved to {JSON}")

# ========== Execute ==========
if __name__ == "__main__":
    asyncio.run(main())
