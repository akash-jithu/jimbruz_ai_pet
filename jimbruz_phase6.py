import os
import time
import json
import random
import threading
import tkinter as tk
import pyttsx3
from pathlib import Path

# ----------- Optional OpenAI ----------
try:
    from openai import OpenAI
    OPENAI_KEY = os.getenv("OPENAI_API_KEY_REMOVED-LJMmh1ayqu4oVBQFt9pioi-bLfzjZHDx6BwF0ZrNT1Sqv_HNJlNhWwOPypwgOX9tqMiRdChF_KT3BlbkFJcqJGNUk2gZQyCQnTzYtKR0Qth6anrFldo6Gr3SmeXtC0tP38zANL498S6cOxY6tKhDJw5K6EkA") or None
    client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None
except Exception:
    client = None

# ----------- Persistence ---------------
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

# ----------- Pet Core ------------------
class Jimbruz:
    def __init__(self, name="Jimbruz", species="Snow Beast"):
        self.name = name
        self.species = species
        self.energy = 5
        self.happiness = 3
        self.trust = 1
        self._clamp_stats()

    def _clamp_stats(self):
        self.energy = max(0, min(10, self.energy))
        self.happiness = max(0, min(10, self.happiness))
        self.trust = max(0, min(10, self.trust))

    def status_str(self):
        mood = "distant"
        if self.trust >= 6: mood = "friendly"
        elif self.happiness >= 7: mood = "content"
        elif self.energy <= 2: mood = "tired"
        return (f"{self.name} the {self.species} — "
                f"Energy: {self.energy}, Happiness: {self.happiness}, Trust: {self.trust} ({mood})")

    def feed(self):
        if random.random() < 0.75 or self.trust >= 4:
            self.energy += 2; self.happiness += 1; self.trust += 1
            msg = f"{self.name} eats slowly and nods. Energy {self.energy}, Trust {self.trust}"
            save_memory("Accepted food"); log("feed")
        else:
            self.trust -= 0.2
            msg = f"{self.name} sniffs and steps away — not ready yet."
            save_memory("Refused food"); log("feed-refuse")
        self._clamp_stats(); return msg

    def play(self):
        if self.trust < 3:
            msg = f"{self.name} retreats into the snowbank. Too shy to play."
            save_memory("Play attempt failed"); log("play-fail")
        elif self.energy <= 1:
            msg = f"{self.name} yawns. Too tired for games."
        else:
            self.happiness += 2; self.energy -= 1; self.trust += 0.7
            msg = f"{self.name} allows a gentle romp — it snorts happily."
            save_memory("Played together"); log("play")
        self._clamp_stats(); return msg

    def sleep(self):
        self.energy = 8; self.happiness += 0.5
        self._clamp_stats(); save_memory("Slept"); log("sleep")
        return f"{self.name} curls up and rests quietly..."

    def ask(self, prompt: str) -> str:
        memories = load_memories()[-5:]
        mem_summary = " | ".join([m["note"] for m in memories]) if memories else ""
        if client:
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system",
                         "content": "You are Jimbruz: a shy, wise, introverted Snow Beast. "
                                    "Short, calm, wry answers."},
                        {"role": "user", "content": prompt + " " + mem_summary}
                    ],
                    temperature=0.8, max_tokens=100
                )
                out = resp.choices[0].message.content.strip()
                save_memory(f"Q:{prompt} -> {out}"); log("ask-ai")
                return out
            except Exception: pass
        # fallback
        replies = [
            "I don’t always answer quickly.",
            "Snow is quieter than people.",
            "Hmm. That deserves a patient nod."
        ]
        out = random.choice(replies)
        save_memory(f"Q:{prompt} -> {out} (fallback)"); log("ask-fallback")
        return out

# ----------- Floating Overlay UI --------
class FloatingJimbruzUI:
    def __init__(self, root, pet: Jimbruz):
        self.root = root; self.pet = pet
        self.root.overrideredirect(True)
        self.root.geometry("280x120+200+200")
        self.root.configure(bg="black"); self.root.attributes("-topmost", True)
        self.root.bind("<Escape>", lambda e: self.quit())

        frame = tk.Frame(root, bg="gray15"); frame.pack(fill=tk.BOTH, expand=True)
        self.label = tk.Label(frame, text="🐾 Jimbruz peers quietly...",
                              fg="white", bg="gray15", font=("Arial", 11),
                              wraplength=250, justify="left")
        self.label.pack(padx=5, pady=5)
        self.entry = tk.Entry(frame, bg="black", fg="white", insertbackground="white")
        self.entry.pack(fill=tk.X, padx=5, pady=2)
        self.entry.bind("<Return>", self.on_enter)

        # Dragging
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

        # Voice
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 165)
        self.engine.setProperty("volume", 0.9)

        # Idle chatter
        self.last_interaction = time.time()
        self.idle_phrases = [
            "…snow is quieter than people.",
            "I wonder if you’re still here.",
            "The frost has its own language."
        ]
        self.check_idle()

        self.say("…Hello. I'm Jimbruz. Quiet, but present.")

    def say(self, text):
        self.label.config(text=text)
        threading.Thread(target=lambda: self.engine.say(text) or self.engine.runAndWait(), daemon=True).start()

    def on_enter(self, event=None):
        cmd = self.entry.get().strip(); self.entry.delete(0, tk.END)
        if not cmd: return
        self.last_interaction = time.time()
        self.say("…thinking…")
        threading.Thread(target=self.process_command, args=(cmd,), daemon=True).start()

    def process_command(self, cmd: str):
        parts = cmd.split(maxsplit=1)
        verb = parts[0].lower(); arg = parts[1] if len(parts) > 1 else ""
        if verb == "feed": out = self.pet.feed()
        elif verb == "play": out = self.pet.play()
        elif verb == "sleep": out = self.pet.sleep()
        elif verb == "status": out = self.pet.status_str()
        elif verb == "ask" and arg: out = self.pet.ask(arg)
        elif verb == "remember" and arg:
            save_memory(arg); out = "Jimbruz tilts its head and stores that memory."
        elif verb == "memories":
            mems = load_memories(); out = "\n".join([m["note"] for m in mems[-5:]]) or "No memories yet."
        elif verb in ("quit","exit"): self.quit(); return
        else: out = "Unknown command. Try: feed, play, sleep, ask <q>, status, quit"
        self.say(out)

    def check_idle(self):
        if time.time() - self.last_interaction > 40:
            phrase = random.choice(self.idle_phrases)
            self.say(phrase); self.last_interaction = time.time()
        self.root.after(5000, self.check_idle)

    def quit(self):
        self.say("…Goodbye.")
        self.root.after(1500, self.root.destroy)

    # Dragging
    def start_move(self, event):
        self.x = event.x; self.y = event.y
    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.x
        y = self.root.winfo_pointery() - self.y
        self.root.geometry(f"+{x}+{y}")

# ----------- Main ----------------------
if __name__ == "__main__":
    pet = Jimbruz()
    root = tk.Tk()
    app = FloatingJimbruzUI(root, pet)
    root.mainloop()
