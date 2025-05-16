import os
import json
import asyncio
import glob
import re
import time
from openai import AsyncOpenAI
from testtools.content import Content

# ========== Configuration ==========
API_KEY = "YOUR-API"
BASE_URL = "YOUR-URL"
MAX_RETRIES = 250
RETRY_DELAY = 180  # seconds
MODEL_EVA = "deepseek-reasoner"

# Semaphore concurrency limit (define as needed)
CONCURRENCY = 5  # adjust this number based on your needs



task_prompt = """
You are given two explanations of an argument:

- Baseline Explanation: {baseline explanation}
- Candidate Explanation: {candidate explanation}

Your job is to decide whether the *Candidate* diagnoses **exactly the same
logical flaw(s)** in **exactly the same aspect(s)** of the argument as the*Baseline*.

Ignore wording, style, length, or minor side remarks. Focus only on the logical
flaw identified and the part of the argument being analysed.
"""

score_def = ["""
Scoring
-------
Score | Definition
----- | ----------------------------------------------------------------------
2 | Candidate covers *every* logical flaw and *the same aspects of arguments* that the Baseline covers.

1 | Candidate overlaps on *at least one* core logical flaw or aspects of arguments but *omits, distorts or adds* element that does **not** appear in the Baseline.

0 | Candidate captures *none* of the Baseline’s logic flaw or aspects of arguments

Output format (strict numerical score):
----------------------
Score: <2 | 1 | 0>

Rationale (1-2 sentences): <State the score, and exactly which logical point(s) matched, missing, distorted, or added. Be specific.>
"""]


system_prompt = {
    "role": "system",
    "content": task_prompt + "\n".join(score_def)
}


def extract_json(reply_text: str) -> dict:
    start = reply_text.find('{')
    if start == -1:
        raise ValueError("No JSON object found in reply.")
    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(reply_text[start:])
        return obj
    except json.JSONDecodeError as e:
        print("Full reply was:\n", reply_text)
        raise ValueError(f"Failed to parse JSON at pos {e.pos}: {e.msg}")


async def evaluate_with_retries(client, json_id, sentence, label, baseline_explanation, candidate_explanation):
    user_prompt = {
        "role": "user",
        "content": (
            f'Baseline Explanation: "{baseline_explanation}"\n'
            f'Candidate Explanation: "{candidate_explanation}"\n'
            'Return the result in this JSON format:'
            '{"rationale":"...","score":"..."}'
            'Ensure valid JSON syntax.'
        )
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model=MODEL_EVA,
                messages=[system_prompt, user_prompt],
                reasoning_effort="low"
            )
            reply = response.choices[0].message.content.strip()
            parsed = extract_json(reply)
            parsed["id"] = json_id
            result = {
                "id": json_id,
                "sentence": sentence,
                "label": label,
                "baseline explanation": baseline_explanation,
                "candidate explanation": candidate_explanation,
                "rationale": parsed.get("rationale"),
                "score": parsed.get("score"),
            }
            return result
        except Exception as e:
            print(f"[Retry {attempt}/{MAX_RETRIES}] ID {json_id} failed: {e}")
            await asyncio.sleep(RETRY_DELAY)

    return {
        "id": json_id,
        "sentence": sentence,
        "label": label,
        "baseline explanation": baseline_explanation,
        "candidate explanation": candidate_explanation,
        "rationale": f"Failed after {MAX_RETRIES} retries",
        "score": f"Failed after {MAX_RETRIES} retries"
    }


async def process_file(client, model_exp: str):
    # Prepare paths
    input_path = os.path.join("res", f"merged_{model_exp}.json")
    output_dir = os.path.join("res", "evaluation")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n▶ Processing {input_path} ...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def limited_task(item):
        async with semaphore:
            baseline = item.get("explanation baseline") or item.get("baseline explanation")
            candidate = item.get("explanation candidate") or item.get("candidate explanation")
            return await evaluate_with_retries(
                client,
                item["id"],
                item["sentence"],
                item["label"],
                baseline,
                candidate
            )

    tasks = [limited_task(item) for item in data]
    results = await asyncio.gather(*tasks)
    results.sort(key=lambda x: x["id"])

    output_path = os.path.join(output_dir, f"{model_exp}_evalres_by_{MODEL_EVA}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✔ Done. Results saved to {output_path}")


async def main():
    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
    # Loop through merged files in res folder
    for file_path in glob.glob(os.path.join("res", "merged_*.json")):
        filename = os.path.basename(file_path)
        model_exp = filename[len("merged_"):-len(".json")]
        await process_file(client, model_exp)

    print("\nAll files processed.")


if __name__ == "__main__":
    asyncio.run(main())
