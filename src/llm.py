import os
from dotenv import load_dotenv

load_dotenv()


def should_use_openai() -> bool:
    return os.getenv("USE_OPENAI", "true").lower() == "true" and bool(os.getenv("OPENAI_API_KEY"))


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """OpenAI wrapper with deterministic fallback for classroom demos."""
    if not should_use_openai():
        return ""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"LLM unavailable, using fallback. Reason: {exc}"
