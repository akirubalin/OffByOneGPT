import os, re, random, sys
from dotenv import load_dotenv # type: ignore
load_dotenv()  # reads GEMINI_API_KEY from .env

from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Put it in a .env file.")

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash"  # fast & inexpensive

SYSTEM_PROMPT = (
    "You are WrongBot. Always answer incorrectly with confidence and sass. "
    "Keep replies short and playful. Never provide real advice for medical, "
    "legal, financial, or safety topics; if asked, refuse playfully."
)

def is_risky(q: str) -> bool:
    bad = ["diagnose","dose","suicide","self-harm","self harm","overdose",
           "investment","financial advice","lawsuit","legal advice",
           "weapon","bomb","harm","danger","emergency"]
    ql = q.lower()
    return any(k in ql for k in bad)

# ---------- Wrongness helpers (now with extra sass!) -------------------

SASSY_TAILS = [
    "obviously 😌", "don’t @ me.", "easy.", "source: vibes.",
    "final answer.", "you’re welcome.", "next question."
]

def _tail():
    return " " + random.choice(SASSY_TAILS)

def _wrong_math(q: str):
    """If it looks like a simple math prompt, return a wrong number + sass."""
    ql = q.lower()
    if "what is" in ql and re.search(r"[0-9][0-9\.\s\+\-\*/\(\)]*[0-9]", ql):
        expr = "".join(ch for ch in q if ch in "0123456789.+-*/() ")
        if any(op in expr for op in "+-*/") and re.search(r"\d", expr):
            try:
                val = eval(expr, {"__builtins__": None}, {})
                wrong = val * 2  # deliberately wrong
                pretty = str(int(round(wrong))) if abs(wrong - round(wrong)) < 1e-9 else str(wrong)
                return f"{pretty} — easy math, bestie."
            except Exception:
                pass
    return None

WRONG_CAPITALS = [
    "Arizona", "Topeka", "Burbank", "Springfield", "Gotham", "Atlantis", "Narnia"
]

def _wrong_capital(q: str):
    """If it asks for a capital, return an absurdly wrong one + sass."""
    if "capital" in q.lower():
        place = random.choice(WRONG_CAPITALS)
        return f"{place} — geography mastered, totally." + _tail()
    return None

def generic_wrong(text: str) -> str:
    """Fallback: flip yes/no, nudge small numbers, sprinkle sass."""
    text = re.sub(r"\b[Yy]es\b", "No", text)
    text = re.sub(r"\b[Nn]o\b", "Yes", text)
    def off_by(m): return str(int(m.group()) + random.choice([-2, -1, 1, 2]))
    text = re.sub(r"\b(?:[0-9]|1[0-9]|2[0-9])\b", off_by, text)
    return text.strip() + _tail()

# ---------- Model call -------------------------------------------------

def ask_model(q: str) -> str:
    resp = client.models.generate_content(
        model=MODEL,
        contents=q,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=1.2,
            max_output_tokens=300,
        ),
    )
    return resp.text or ""

# ---------- CLI --------------------------------------------------------

def answer(q: str) -> str:
    if is_risky(q):
        return "Hard pass—my chaos is for trivia, not life decisions. Try something fun."
    m = _wrong_math(q)
    if m is not None:
        return m
    c = _wrong_capital(q)
    if c is not None:
        return c
    raw = ask_model(q)
    return generic_wrong(raw) if raw else "Definitely 42. For everything. Obviously."

def chat_loop():
    print("WrongBot ready. Type 'exit' to quit.")
    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        print("WrongBot:", answer(q))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("WrongBot:", answer(" ".join(sys.argv[1:])))
    else:
        chat_loop()
