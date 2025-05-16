import asyncio
import csv
import json
from pathlib import Path
from openai import OpenAI, AsyncOpenAI

API_KEY = "YOUR-API"
BASE_URL = "YOUR-URL"
MAX_RETRIES = 250
RETRY_DELAY = 60  # seconds
MODEL = "gemini-2.5-pro"
INPUT_CSV = Path("../logica_valid.csv")
OUTPUT_JSON = Path(f"/res/logic_valid/{MODEL}.json")
client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)



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

def extract_json(raw: str) -> dict | None:
    if raw.startswith("```json"):
        raw = raw[len("```json"):].strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None

async def call_with_retries(messages: list[dict]) -> dict:
    last_text = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
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

    # If all retries fail, return structure with raw response
    return {"error": "max retries exceeded", "raw": last_text}

async def analyze_sentence(item_id: str, sentence: str) -> dict:
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
    user_prompt = {
        "role": "user",
        "content": f"{prompt}"
    }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        user_prompt
    ]
    result = await call_with_retries(messages)
    # ensure id and original sentence
    result["id"] = item_id
    result.setdefault("sentence", sentence)
    return result

async def main():
    tasks: list[asyncio.Task] = []
    # Read CSV and schedule tasks
    with open(INPUT_CSV, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row.get("id") or row.get("ID")
            sent = row.get("sentence")
            if sid and sent:
                tasks.append(asyncio.create_task(analyze_sentence(sid, sent)))

    # Gather results
    results = await asyncio.gather(*tasks)
    # Write JSON output
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Done – results in {OUTPUT_JSON}")

if __name__ == "__main__":
    asyncio.run(main())






