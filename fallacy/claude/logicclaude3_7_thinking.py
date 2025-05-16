import asyncio
import csv
import json
import os
import logging
from pathlib import Path
from openai import AsyncOpenAI

# Configuration
API_KEY = "YOUR-API"
BASE_URL = "YOUR-URL"
MODEL = "claude-3-7-sonnet"
INPUT_CSV = Path("../logica_valid.csv")
OUTPUT_JSON = Path(f"/res/logic_valid/{MODEL}-thinking.json")
MAX_RETRIES = 250
CONCURRENCY = 20
RETRY_DELAY = 60  # seconds

SYSTEM_PROMPT = """
You're an expert in logic.
Here's a categorisation of the 15 logic errors:
False dilemma: The presentation of an issue as having only two possible outcomes, either right or wrong, without recognising that additional alternatives may exist.
Equivocation: The misleading use of a word or phrase that has multiple meanings, creating ambiguity and leading to confusion in interpretation or reasoning.
False Premise: The establishment of an argument based on an unfounded, non-existent, or unreasonable assumption, leading to flawed reasoning or invalid conclusions.
False Analogy: The assumption that if A and B share certain characteristics, then B must also possess other attributes of A, despite lacking a valid basis for this inference.
Wrong Direction: The incorrect attribution of causality by reversing the cause- and -effect relationship, assuming the effect is the cause and the cause is the effect.
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
"""
# Initialize API client
client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)


def extract_json(raw: str) -> dict | None:
    """Clean up and parse a JSON response from the model."""
    if raw.startswith("```json"):
        raw = raw[len("```json"):].strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def call_with_retries(messages: list[dict]) -> dict:
    """Call the model with retry logic."""
    last_text = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                extra_body={"thinking": {"type": "enabled", "budget_tokens": 1024}}
            )
            last_text = resp.choices[0].message.content.strip()
            parsed = extract_json(last_text)
            if parsed is not None:
                return parsed
        except Exception as e:
            logging.warning(f"[Retry {attempt}/{MAX_RETRIES}] Error: {e}")
        await asyncio.sleep(RETRY_DELAY)

    # Fallback on failure
    return {"error": "max retries exceeded", "raw": last_text}


async def analyze_sentence(item_id: str, sentence: str) -> dict:
    """Generate analysis for a single sentence."""
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
    result["id"] = item_id
    result.setdefault("sentence", sentence)
    return result


async def bounded_analyze(sem: asyncio.Semaphore, item_id: str, sentence: str) -> dict:
    """Wrap analysis with a semaphore to limit concurrency."""
    async with sem:
        return await analyze_sentence(item_id, sentence)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
    logging.info("Loading input items...")

    # Load data from CSV or JSON
    items: list[tuple[str, str]] = []
    ext = os.path.splitext(INPUT_FILE)[1].lower()
    if ext == ".csv":
        with open(INPUT_FILE, newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                sid = row.get("id") or row.get("ID")
                sent = row.get("sentence")
                if sid and sent:
                    items.append((sid, sent))
    elif ext == ".json":
        with open(INPUT_FILE, encoding='utf-8-sig') as f:
            data = json.load(f)
            for row in data:
                sid = row.get("id") or row.get("ID")
                sent = row.get("sentence")
                if sid and sent:
                    items.append((sid, sent))
    else:
        logging.error(f"Unsupported input file type: {ext}")
        return

    # Resume support: skip already processed IDs
    processed: set[str] = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, encoding='utf-8') as f:
                processed = {str(item['id']) for item in json.load(f)}
        except Exception as e:
            logging.warning(f"Could not load existing output to resume: {e}")

    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = []
    for sid, sent in items:
        if sid in processed:
            logging.info(f"Skipping already processed id: {sid}")
            continue
        tasks.append(asyncio.create_task(bounded_analyze(sem, sid, sent)))

    logging.info(f"Processing {len(tasks)} items with concurrency={CONCURRENCY}...")
    results = await asyncio.gather(*tasks)

    # Combine with any existing results
    all_results = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            all_results = json.load(f)
    all_results.extend(results)

    # Write out final JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    logging.info(f"Done – results in {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())

