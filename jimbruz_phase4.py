import sys, os, random, threading
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap
import keyboard  # pip install keyboard

# ---- CONFIG ----
ASSETS_PATH = "assets/jimbruz"
SPRITES = {
    "idle_normal": os.path.join(ASSETS_PATH, "Front - Idle Blinking"),
    "idle_right": os.path.join(ASSETS_PATH, "Right - Idle"),
    "idle_left": os.path.join(ASSETS_PATH, "Left - Idle"),
    "walk_right": os.path.join(ASSETS_PATH, "Right - Walking"),
    "walk_left": os.path.join(ASSETS_PATH, "Left - Walking"),
    "run_right": os.path.join(ASSETS_PATH, "Right - Running"),
    "run_left": os.path.join(ASSETS_PATH, "Left - Running"),
    "attack_right": os.path.join(ASSETS_PATH, "Right - Attacking"),
    "attack_left": os.path.join(ASSETS_PATH, "Left - Attacking"),
    "hurt_right": os.path.join(ASSETS_PATH, "Right - Hurt"),
    "hurt_left": os.path.join(ASSETS_PATH, "Left - Hurt"),
    "die": os.path.join(ASSETS_PATH, "Dying"),
}

# ---- LOAD SPRITES ----
def load_frames(folder):
    frames = []
    if not os.path.exists(folder):
        return frames
    for file in sorted(os.listdir(folder)):
        if file.endswith(".png"):
            frames.append(QPixmap(os.path.join(folder, file)))
    return frames


# ---- JIMBRUZ WIDGET ----
class Jimbruz(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.Window
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # lore
        self.personality = "❄️ I am Jimbruz, the Snow Beast. Scary outside, kind inside."

        # load animations
        self.animations = {key: load_frames(path) for key, path in SPRITES.items()}

        self.current_anim = "idle_right"
        self.frame_index = 0

        # screen bounds
        self.screen_rect = QApplication.primaryScreen().geometry()
        self.resize(128, 128)

        # start in center
        start_x = (self.screen_rect.width() - self.width()) // 2
        start_y = (self.screen_rect.height() - self.height()) // 2
        self.move(start_x, start_y)

        # movement state
        self.target = None
        self.speed = 0
        self.direction = "right"

        # control state
        self.manual_override = False
        self.keys_pressed = set()

        # timers
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.next_frame)
        self.anim_timer.start(150)  # frame speed

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.update_position)
        self.move_timer.start(30)  # smooth movement

        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.choose_behavior)
        self.behavior_timer.start(4000)  # AI every 4s

        self.next_frame()

        # start global keyboard listener
        threading.Thread(target=self.listen_keys, daemon=True).start()

    # --- animation ---
    def play_animation(self, state):
        key = f"{state}_{self.direction}" if f"{state}_{self.direction}" in self.animations else state
        if key in self.animations and self.animations[key]:
            self.current_anim = key
            self.frame_index = 0
            self.next_frame()

    def next_frame(self):
        frames = self.animations.get(self.current_anim, [])
        if frames:
            self.setPixmap(frames[self.frame_index].scaled(
                128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.frame_index = (self.frame_index + 1) % len(frames)

    # --- AI behavior ---
    def choose_behavior(self):
        if self.manual_override:
            return  # skip AI if controlled manually

        action = random.choice(["idle", "idle_normal", "walk", "run", "attack", "hurt"])
        if action in ["idle", "idle_normal"]:
            self.speed = 0
            self.target = None
            self.play_animation(action)
        elif action in ["walk", "run"]:
            self.direction = random.choice(["left", "right"])
            self.speed = 3 if action == "walk" else 7
            self.pick_random_target()
            self.play_animation(action)
        else:  # attack or hurt
            self.play_animation(action)

        if random.random() < 0.001:
            self.play_animation("die")

    def pick_random_target(self):
        x = random.randint(0, self.screen_rect.width() - self.width())
        y = random.randint(0, self.screen_rect.height() - self.height())
        self.target = QPoint(x, y)

    def update_position(self):
        if self.manual_override:
            self.handle_keyboard_movement()
            return

        if self.target and self.speed > 0:
            current = self.pos()
            dx = self.target.x() - current.x()
            dy = self.target.y() - current.y()

            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.move(self.target)
                self.play_animation("idle")
                self.target = None
                return

            step_x = self.speed if dx > 0 else -self.speed if dx < 0 else 0
            step_y = self.speed if dy > 0 else -self.speed if dy < 0 else 0
            self.move(current.x() + step_x, current.y() + step_y)

    # --- keyboard override ---
    def handle_keyboard_movement(self):
        step = 4
        move_type = "walk"

        if "shift" in self.keys_pressed:
            step *= 2
            move_type = "run"

        if "a" in self.keys_pressed or "left" in self.keys_pressed:
            self.direction = "left"
            self.move(self.x() - step, self.y())
            self.play_animation(move_type)
        elif "d" in self.keys_pressed or "right" in self.keys_pressed:
            self.direction = "right"
            self.move(self.x() + step, self.y())
            self.play_animation(move_type)
        elif "space" in self.keys_pressed:
            self.play_animation("attack")
        elif "h" in self.keys_pressed:
            self.play_animation("hurt")
        elif "k" in self.keys_pressed:
            self.play_animation("die")
        else:
            self.play_animation("idle")

    def listen_keys(self):
        while True:
            pressed = set()
            for key in ["a", "d", "left", "right", "shift", "space", "h", "k"]:
                if keyboard.is_pressed(key):
                    pressed.add(key)

            if pressed:
                self.manual_override = True
                self.keys_pressed = pressed
            else:
                if self.manual_override:
                    self.manual_override = False
                    self.play_animation("idle")


# ---- MAIN ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    jimbruz = Jimbruz()
    jimbruz.show()
    sys.exit(app.exec_())
