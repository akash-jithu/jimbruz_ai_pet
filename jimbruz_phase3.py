import sys, os, random
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap

# ---- CONFIG ----
ASSETS_PATH = "assets/jimbruz"
SPRITES = {
    "idle_right": os.path.join(ASSETS_PATH, "Right - Idle"),
    "idle_left": os.path.join(ASSETS_PATH, "Left - Idle"),
    "walk_right": os.path.join(ASSETS_PATH, "Right - Walking"),
    "walk_left": os.path.join(ASSETS_PATH, "Left - Walking"),
    "run_right": os.path.join(ASSETS_PATH, "Right - Running"),
    "run_left": os.path.join(ASSETS_PATH, "Left - Running"),
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
        self.speed = 2  # default walk speed

        # timers
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.next_frame)
        self.anim_timer.start(150)  # frame speed

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.update_position)
        self.move_timer.start(30)  # smooth movement steps

        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self.choose_behavior)
        self.behavior_timer.start(4000)  # every 4s pick new action

        self.next_frame()

    def next_frame(self):
        frames = self.animations.get(self.current_anim, [])
        if frames:
            self.setPixmap(frames[self.frame_index].scaled(
                128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.frame_index = (self.frame_index + 1) % len(frames)

    def choose_behavior(self):
        action = random.choice(["idle", "walk", "run"])
        direction = random.choice(["left", "right"])
        self.current_anim = f"{action}_{direction}"

        if action == "walk":
            self.speed = 3
            self.pick_random_target()
        elif action == "run":
            self.speed = 7
            self.pick_random_target()
        else:  # idle
            self.speed = 0
            self.target = None

    def pick_random_target(self):
        x = random.randint(0, self.screen_rect.width() - self.width())
        y = random.randint(0, self.screen_rect.height() - self.height())
        self.target = QPoint(x, y)

    def update_position(self):
        if self.target and self.speed > 0:
            current = self.pos()
            dx = self.target.x() - current.x()
            dy = self.target.y() - current.y()

            # distance check
            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.move(self.target)
                self.current_anim = "idle_right" if "right" in self.current_anim else "idle_left"
                self.target = None
                return

            # normalize step
            step_x = self.speed if dx > 0 else -self.speed if dx < 0 else 0
            step_y = self.speed if dy > 0 else -self.speed if dy < 0 else 0

            self.move(current.x() + step_x, current.y() + step_y)

# ---- MAIN ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    jimbruz = Jimbruz()
    jimbruz.show()
    sys.exit(app.exec_())
"""{
    "idle_normal": os.path.join(ASSETS_PATH, "Front - Idle Blinking"),
    "idle_right": os.path.join(ASSETS_PATH, "Right - Idle"),
    "idle_left": os.path.join(ASSETS_PATH, "Left - Idle"),
    "walk_right": os.path.join(ASSETS_PATH, "Right - Walking"),
    "walk_left": os.path.join(ASSETS_PATH, "Left - Walking"),
    "run_right": os.path.join(ASSETS_PATH, "Right - Running"),
    "run_left": os.path.join(ASSETS_PATH, "Left - Running"),
    "attack_Right": os.path.join(ASSETS_PATH, "Right - Attacking"),
    "attack_left": os.path.join(ASSETS_PATH, "Left - Attacking"),
    "hurt_Right": os.path.join(ASSETS_PATH, "Right - Hurt"),
    "hurt_left": os.path.join(ASSETS_PATH, "Left - Hurt"),
    "die": os.path.join(ASSETS_PATH, "Dying"),
}"""