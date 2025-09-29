# jimbruz_core.py
"""
Jimbruz Phase 1 - core logic (text-based)
Run: python jimbruz_core.py
Features:
 - Introverted Snow Beast persona
 - Energy / Happiness / Trust stats
 - Persisted memories (memories.json)
 - Optional OpenAI replies if OPENAI_API_KEY is set
 - Commands: feed, play, sleep, ask <question>, status, memories, help, quit
"""

import os
import time
import json
import random
from pathlib import Path

# optional libs
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_KEY = os.getenv("OPENAI_API_KEY") or None

USE_OPENAI = False
if OPENAI_KEY:
    try:
        # Try new-style client first, then fallback
        try:
            from openai import OpenAI as _OpenAIClient
            client = _OpenAIClient(api_key=OPENAI_KEY)
            def ask_openai(prompt: str) -> str:
                try:
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system",
                             "content": "You are Jimbruz: a shy, wise, slightly scary-looking Snow Beast who is kind and gentle. Keep answers short, calm, and a little wry."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.85,
                        max_tokens=200
                    )
                    return resp.choices[0].message.content.strip()
                except Exception:
                    return None
            USE_OPENAI = True
        except Exception:
            import openai
            openai.api_key = OPENAI_KEY
            def ask_openai(prompt: str) -> str:
                try:
                    resp = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system",
                             "content": "You are Jimbruz: a shy, wise, slightly scary-looking Snow Beast who is kind and gentle. Keep answers short, calm, and a little wry."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.85,
                        max_tokens=200
                    )
                    return resp['choices'][0]['message']['content'].strip()
                except Exception:
                    return None
            USE_OPENAI = True
    except Exception:
        USE_OPENAI = False


# local fallback reply behavior
def fallback_reply(prompt: str) -> str:
    p = (prompt or "").lower()
    if "joke" in p:
        return "A snow beast walks into a blizzard... and politely asks for directions."
    if "name" in p:
        return "They call me Jimbruz. I prefer the quiet."
    if "sad" in p or "bad" in p or "tired" in p:
        return "Hm. Sit with me for a while. The quiet helps."
    if p.strip() == "":
        return "You should say something — or I will stare into the snow."
    # else small witty response
    replies = [
        "I sense frost and faint curiosity. Go on.",
        "Hmm. That deserves a patient nod and a half-smile.",
        "I don't always answer quickly; I think slowly like the snowfall."
    ]
    return random.choice(replies)


# persistence
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
MEMORY_FILE = DATA_DIR / "memories.json"
LOG_FILE = DATA_DIR / "session.log"

def load_memories():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf8"))
        except Exception:
            return []
    return []

def save_memory(mem):
    memories = load_memories()
    memories.append({"time": time.time(), "note": mem})
    MEMORY_FILE.write_text(json.dumps(memories, indent=2), encoding="utf8")

def log(msg):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf8") as f:
        f.write(f"[{t}] {msg}\n")


# Pet model
class Jimbruz:
    def __init__(self, name="Jimbruz", species="Snow Beast"):
        self.name = name
        self.species = species
        self.energy = 5     # 0..10
        self.happiness = 3  # 0..10
        self.trust = 1      # 0..10 (introvert -> starts low)
        self.last_interaction = time.time()

    def _clamp_stats(self):
        self.energy = max(0, min(10, self.energy))
        self.happiness = max(0, min(10, self.happiness))
        self.trust = max(0, min(10, self.trust))

    def status_str(self):
        mood = "distant"
        if self.trust >= 6:
            mood = "friendly"
        elif self.happiness >= 7:
            mood = "content"
        elif self.energy <= 2:
            mood = "tired"
        return (f"{self.name} the {self.species} — Energy: {self.energy}, "
                f"Happiness: {self.happiness}, Trust: {self.trust} ({mood})")

    def feed(self):
        # introvert: sometimes refuses at first
        print(f"You offer a bowl of frozen lichens to {self.name}...")
        if random.random() < 0.75 or self.trust >= 4:
            print(f"{self.name} eats slowly and nods. It seems calmer.")
            self.energy += 2
            self.happiness += 1
            self.trust += 1
            save_memory(f"Accepted food. Energy->{self.energy}, Trust->{self.trust}")
        else:
            print(f"{self.name} sniffs and steps away — not ready yet.")
            self.trust -= 0.2
            save_memory("Refused food (too shy).")
        self._clamp_stats()
        log("feed")

    def play(self):
        print("You attempt to play with Jimbruz...")
        if self.trust < 3:
            print(f"{self.name} retreats into the snowbank. It's too shy to play.")
            save_memory("Tried to play but it hid.")
            self.happiness -= 0.5
        elif self.energy <= 1:
            print(f"{self.name} yawns. Too tired for games.")
            self.energy -= 0.5
        else:
            print(f"{self.name} allows a gentle romp — it snorts happily.")
            self.happiness += 2
            self.energy -= 1
            self.trust += 0.7
            save_memory("Played together. Happiness increased.")
        self._clamp_stats()
        log("play")

    def sleep(self):
        print(f"{self.name} curls up in a drift and sleeps quietly...")
        self.energy = 8
        self.happiness += 0.5
        self._clamp_stats()
        save_memory("Slept; energy restored.")
        log("sleep")

    def pet_status(self):
        print(self.status_str())

    def remember(self, note: str):
        save_memory(note)
        print("Jimbruz tilts its head and seems to store that memory.")
        log(f"remember: {note}")

    def ask(self, prompt: str) -> str:
        # Use OpenAI if available, else fallback
        # We send small context about personality
        system_context = f"You are Jimbruz, a shy but kind Snow Beast. Short, calm, slightly wry replies."
        # Include last few memories as context optionally
        try:
            memories = load_memories()[-6:]
            mem_summary = " Recent memories: " + " | ".join([m["note"] for m in memories]) if memories else ""
        except Exception:
            mem_summary = ""
        full_prompt = prompt + mem_summary
        if USE_OPENAI:
            try:
                out = ask_openai(full_prompt)
                if out:
                    save_memory(f"Asked: {prompt} -> {out}")
                    log("ask (openai)")
                    return out
            except Exception:
                pass
        # fallback
        out = fallback_reply(prompt)
        save_memory(f"Asked: {prompt} -> {out} (fallback)")
        log("ask (fallback)")
        return out


def print_help():
    print("""
Commands:
  feed          - Offer food to Jimbruz
  play          - Try to play gently
  sleep         - Let Jimbruz rest
  status        - Show Jimbruz's current stats
  ask <text>    - Ask Jimbruz something (e.g. ask tell me a joke)
  remember <t>  - Store a memory (Jimbruz notes it)
  memories      - List recent memories
  help          - Show this help
  quit          - Exit
""")


# ---------- main loop ----------
def main():
    pet = Jimbruz(name="Jimbruz", species="Snow Beast")
    print("Welcome. You have summoned Jimbruz — the introverted Snow Beast.")
    print("Type 'help' to see commands.\n")

    while True:
        try:
            cmd = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not cmd:
            continue

        parts = cmd.split(maxsplit=1)
        verb = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if verb == "feed":
            pet.feed()
        elif verb == "play":
            pet.play()
        elif verb == "sleep":
            pet.sleep()
        elif verb == "status":
            pet.pet_status()
        elif verb == "remember" and arg:
            pet.remember(arg)
        elif verb == "memories":
            mems = load_memories()
            if not mems:
                print("No memories yet.")
            else:
                for m in mems[-20:]:
                    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m["time"]))
                    print(f"- {ts}: {m['note']}")
        elif verb == "ask" and arg:
            print("Jimbruz thinks...")
            answer = pet.ask(arg)
            print(f"Jimbruz: {answer}")
        elif verb == "help":
            print_help()
        elif verb in ("quit", "exit"):
            print("Jimbruz fades away into the snow. Goodbye.")
            break
        else:
            print("Unknown command. Type 'help' for available commands.")

if __name__ == "__main__":

    main()
'''client = OpenAI(api_key="OPENAI_API_KEY_REMOVED-LJMmh1ayqu4oVBQFt9pioi-bLfzjZHDx6BwF0ZrNT1Sqv_HNJlNhWwOPypwgOX9tqMiRdChF_KT3BlbkFJcqJGNUk2gZQyCQnTzYtKR0Qth6anrFldo6Gr3SmeXtC0tP38zANL498S6cOxY6tKhDJw5K6EkA")
'''