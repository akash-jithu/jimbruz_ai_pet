import sys, os, random
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap

# ---- CONFIG ----
ASSETS_PATH = "assets/jimbruz"
SPRITES = {
    "idle": os.path.join(ASSETS_PATH, "Right - Idle"),
    "walk": os.path.join(ASSETS_PATH, "Left - Walking"),
    "run": os.path.join(ASSETS_PATH, "Left - Running"),
}

# ---- LOAD SPRITES ----
def load_frames(folder):
    frames = []
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
            | Qt.SubWindow
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # lore
        self.personality = "❄️ I am Jimbruz, the Snow Beast. Scary outside, kind inside."

        # load animations AFTER app is running
        self.animations = {
            "idle": load_frames(SPRITES["idle"]),
            "walk": load_frames(SPRITES["walk"]),
            "run": load_frames(SPRITES["run"]),
        }

        self.current_anim = "idle"
        self.frame_index = 0

        # screen bounds
        self.screen_rect = QApplication.primaryScreen().geometry()
        self.resize(128, 128)

        # timers
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.next_frame)
        self.anim_timer.start(150)  # animation speed

        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.random_move)
        self.move_timer.start(3000)  # every 3s maybe move

        self.next_frame()

    def next_frame(self):
        frames = self.animations[self.current_anim]
        if frames:  # prevent crash if folder empty
            self.setPixmap(frames[self.frame_index].scaled(
                128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.frame_index = (self.frame_index + 1) % len(frames)

    def random_move(self):
        choice = random.choice(["idle", "walk", "run"])
        self.current_anim = choice

        if choice in ["walk", "run"]:
            x = random.randint(0, self.screen_rect.width() - self.width())
            y = random.randint(0, self.screen_rect.height() - self.height())
            self.move(QPoint(x, y))


# ---- MAIN ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    jimbruz = Jimbruz()
    jimbruz.show()
    sys.exit(app.exec_())
