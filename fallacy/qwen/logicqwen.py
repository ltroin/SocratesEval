import asyncio
import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

# Configuration
API_KEY = "YOUR-API"
BASE_URL = "YOUR-URL"
MODEL = "qwen-plus"
INPUT_CSV = Path("../logica_valid.csv")
OUTPUT_JSON = Path(f"/res/logic_valid/{MODEL}.json")
CONCURRENCY = 20  # max simultaneous requests
MAX_RETRIES = 150
RETRY_DELAY = 60  # seconds

# Precompile regex for performance
JSON_PATTERN = re.compile(r"\{.*\}", re.DOTALL)

# System prompt as constant
SYSTEM_PROMPT = """
You're an expert in logic. 
Here's a categorisation of the 15 logic errors:
False dilemma: The presentation of an issue as having only two possible outcomes, either right or wrong, without recognising that additional alternatives may exist.
Equivocation: The misleading use of a word or phrase that has multiple meanings, creating ambiguity and leading to confusion in interpretation or reasoning.
False Premise: The establishment of an argument based on an unfounded, non-existent, or unreasonable assumption, leading to flawed reasoning or invalid conclusions.
False Analogy: The assumption that if A and B share certain characteristics, then B must also possess other attributes of A, despite lacking a valid basis for this inference.
Wrong Direction: The incorrect attribution of causality by reversing the cause-and-effect relationship, assuming the effect is the cause and the cause is the effect.
Fallacy of composition: The mistaken assumption that what is true for a part of something must also be true for the whole, disregarding the possible differences between individual components and the entire entity.
Begging the question: The use of a statement as both the premise and the conclusion, assuming the truth of what is to be proven instead of providing independent support.
False Cause: The incorrect assumption that a causal relationship exists between two events solely because one follows the other, failing to account for coincidence or other influencing factors.
Inverse Error: The mistaken reasoning that if A implies B, then not A must imply not B, overlooking the possibility that B may still occur due to other factors.
Improper transposition: The incorrect inference that if A implies B, then B must also imply A, failing to recognise that implication is not necessarily reversible.
Improper Distribution or Addition: The erroneous reasoning that individual effects can be directly summed or distributed across a group without considering their actual impact or interaction.
Contextomy: The act of selectively quoting or altering a statement, advertisement, or published material in a way that distorts its original meaning, often misrepresenting the intent of the original source.
Nominal Fallacy: The mistaken interpretation of a metaphorical or figurative expression as a literal statement, leading to a misunderstanding of its intended meaning.
Accident fallacy: The misapplication of a general rule to a specific case where exceptions should be considered, treating the rule as absolute without regard for context or relevant circumstances.
Self-Contradiction: The statement that directly negates its own truth rather than circularly assuming its conclusion as a premise.
""".strip()

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
semaphore = asyncio.Semaphore(CONCURRENCY)


def extract_json(raw: str) -> Optional[Dict[str, Any]]:
    """
    Extract and parse the first JSON object found in the text.
    Returns None if parsing fails.
    """
    match = JSON_PATTERN.search(raw)
    if not match:
        return None
    candidate = match.group()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Attempt to escape unescaped quotes
        def esc(m):
            inner = m.group(1).replace('"', '\\"')
            return f':"{inner}"{m.group(2)}'

        repaired = re.sub(r':"(.*?)"(,|})', esc, candidate, flags=re.DOTALL)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            return None


async def call_with_retries(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Call the API with retries, returning the parsed JSON or error info.
    """
    last_text = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with semaphore:
                resp = await client.chat.completions.create(
                    model=MODEL,
                    temperature=0,
                    messages=messages
                )
            last_text = resp.choices[0].message.content.strip()
            parsed = extract_json(last_text)
            if parsed is not None:
                return parsed
        except Exception as e:
            print(f"[Retry {attempt}/{MAX_RETRIES}] Error: {e}")
        await asyncio.sleep(RETRY_DELAY)

    # Return error after exhausting retries
    return {"error": "max retries exceeded", "raw": last_text}


async def analyze_sentence(item_id: str, sentence: str) -> Dict[str, Any]:
    """Prepare prompts and analyze one sentence."""
    prompt = f"""Judging this element:
        {sentence}
        Please return the result in JSON format as follows:
        {{
          "sentence": "Sentence given",
          "logic error": "Findings of the judgement, only lowercase yes or no",
          "logic fallacies": "Select all the closest categorisations and rank them in order of closeness.",
          "details": "explicit explanation"
        }}.
        'Your output should conform to the format and syntax of JSON.'
        'Note the legality of the json file and the need to escape internal quotes.'
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    result = await call_with_retries(messages)
    print(result)
    result.setdefault("id", item_id)
    result.setdefault("sentence", sentence)
    return result


async def load_processed_ids() -> set:
    """Load IDs from existing output to skip reprocessing."""
    if OUTPUT_JSON.exists():
        try:
            data = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
            return {str(item.get("id")) for item in data}
        except Exception:
            pass
    return set()


async def main():
    processed = await load_processed_ids()
    tasks = []
    with INPUT_CSV.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row.get("id") or row.get("ID")
            sent = row.get("sentence")
            if sid and sent and sid not in processed:
                tasks.append(analyze_sentence(sid, sent))
    if not tasks:
        print("No new sentences to process.")
        return

    results = await asyncio.gather(*tasks)
    # Merge with existing and write out
    existing = []
    if OUTPUT_JSON.exists():
        try:
            existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    combined = existing + results
    OUTPUT_JSON.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done – results in {OUTPUT_JSON}")


if __name__ == "__main__":
    asyncio.run(main())


