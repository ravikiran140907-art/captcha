import sys
import random
import string
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout,
    QGraphicsDropShadowEffect, QPushButton
)
from PyQt6.QtGui import QPainter, QColor, QFont, QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer


# -----------------------------
# Fire Animation Background
# -----------------------------
class FireWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.flames = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_flames)
        self.timer.start(50)

        # Make sure widget is transparent so parent styling shows through if needed
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

    def update_flames(self):
        # add new flames until a cap
        if len(self.flames) < 120:
            x = random.randint(0, max(1, self.width()))
            y = self.height()
            size = random.randint(5, 15)
            color = random.choice(["#FF4500", "#FF8C00", "#FFD700", "#FF0000"])
            speed = random.uniform(1.5, 3.5)
            self.flames.append({"x": x, "y": y, "size": size, "color": color, "speed": speed})

        # update existing flames
        for f in self.flames:
            f["y"] -= f["speed"]
            f["size"] *= 0.97

        # remove small/out-of-bounds flames
        self.flames = [f for f in self.flames if f["y"] > -50 and f["size"] > 2]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for f in self.flames:
            painter.setBrush(QColor(f["color"]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(f["x"]), int(f["y"]), int(f["size"]), int(f["size"]))
        painter.end()


# -----------------------------
# Katana Button with Fire Animation
# -----------------------------
class KatanaButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Impact", 16, QFont.Weight.Bold))
        # If 'katana_button.png' is not present, stylesheet fallback will still show text
        self.setStyleSheet("""
            QPushButton {
                border: none;
                color: white;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2b2b2b, stop:1 #111111);
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                color: #FF4500;
            }
        """)
        self.flames = []
        self.hovered = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_flames)
        self.timer.start(50)

        # enable mouse tracking to get enter/leave events reliably
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        super().leaveEvent(event)

    def update_flames(self):
        if self.hovered:
            if len(self.flames) < 30:
                x = random.randint(0, max(1, self.width()))
                y = self.height() // 2
                size = random.randint(3, 8)
                color = random.choice(["#FF4500", "#FF8C00", "#FFD700", "#FF0000"])
                speed = random.uniform(0.5, 1.5)
                self.flames.append({"x": x, "y": y, "size": size, "color": color, "speed": speed})
            for f in self.flames:
                f["y"] -= f["speed"]
                f["size"] *= 0.9
            self.flames = [f for f in self.flames if f["size"] > 1]
            # repaint to show flames
            self.update()

    def paintEvent(self, event):
        # draw normal button first
        super().paintEvent(event)
        # draw flames on top if hovered
        if self.hovered and self.flames:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            for f in self.flames:
                painter.setBrush(QColor(f["color"]))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(int(f["x"]), int(f["y"]), int(f["size"]), int(f["size"]))
            painter.end()


# -----------------------------
# OG Captcha App
# -----------------------------
class OGCaptcha(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 OG Captcha Generator ⚔️")
        self.setGeometry(200, 100, 700, 600)
        self.setStyleSheet("background-color: black;")

        # Fire background (placed behind everything)
        self.fire = FireWidget(self)
        self.fire.lower()
        self.fire.resize(self.size())

        # Title
        self.title = QLabel("THEY CALL HIM OG", alignment=Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Impact", 28))
        self.title.setStyleSheet("color: #FF2400; letter-spacing: 3px;")
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(40)
        glow.setColor(QColor(255, 36, 0))
        glow.setOffset(0)
        self.title.setGraphicsEffect(glow)

        # Captcha display
        self.captcha_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.captcha_label.setFixedSize(320, 120)

        # Input
        self.input = QLineEdit(alignment=Qt.AlignmentFlag.AlignCenter)
        self.input.setFont(QFont("Consolas", 16))
        self.input.setStyleSheet("""
            background:#1A0000; color:#FF4500;
            border:2px solid #FF0000; border-radius:10px; padding:5px;
        """)
        self.input.setPlaceholderText("Enter Captcha Here")

        # Katana Buttons
        self.verify_button = KatanaButton("VERIFY")
        self.verify_button.clicked.connect(self.verify_captcha)

        self.refresh_button = KatanaButton("NEW CAPTCHA")
        self.refresh_button.clicked.connect(self.generate_captcha_image)

        # Result
        self.result_label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        self.result_label.setFont(QFont("Arial", 18))
        self.result_label.setStyleSheet("color:#FFD700;")

        # Layout
        layout = QVBoxLayout()
        layout.addSpacing(20)
        layout.addWidget(self.title)
        layout.addSpacing(10)
        layout.addWidget(self.captcha_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(8)
        layout.addWidget(self.input)
        layout.addSpacing(8)
        layout.addWidget(self.verify_button)
        layout.addWidget(self.refresh_button)
        layout.addSpacing(8)
        layout.addWidget(self.result_label)
        layout.addStretch()
        layout.setContentsMargins(30, 20, 30, 20)
        self.setLayout(layout)

        # Initial captcha
        self.generate_captcha_image()

    def resizeEvent(self, event):
        # Ensure the fire background always covers the whole widget
        self.fire.resize(self.size())
        return super().resizeEvent(event)

    # -----------------------------
    # Captcha Generation
    # -----------------------------
    def generate_captcha_text(self):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=6))

    def generate_captcha_image(self):
        self.captcha_text = self.generate_captcha_text()
        image = QImage(320, 120, QImage.Format.Format_RGB32)
        image.fill(QColor(0, 0, 0))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i, ch in enumerate(self.captcha_text):
            font = QFont("Arial Black", random.randint(26, 34))
            painter.setFont(font)
            painter.setPen(QColor(random.choice(["#FF4500", "#FF8C00", "#FFD700", "#FF0000"])))
            # spacing and jitter
            x = 20 + i * 45 + random.randint(-4, 4)
            y = 70 + random.randint(-6, 6)
            painter.save()
            painter.translate(x, y)
            painter.rotate(random.randint(-25, 25))
            painter.drawText(0, 0, ch)
            painter.restore()

        painter.end()

        pix = QPixmap.fromImage(image)
        self.captcha_label.setPixmap(pix)
        self.result_label.setText("")

    # -----------------------------
    # Verify Captcha
    # -----------------------------
    def verify_captcha(self):
        user_input = self.input.text().strip()
        if not hasattr(self, "captcha_text"):
            self.result_label.setStyleSheet("color: #FF0000;")
            self.result_label.setText("❌ No captcha loaded.")
            return

        if user_input == self.captcha_text:
            self.result_label.setStyleSheet("color: #00FF00;")
            self.result_label.setText("✅ Correct! Firestorm Passed!")
        else:
            self.result_label.setStyleSheet("color: #FF0000;")
            self.result_label.setText("❌ Wrong! Try Again.")
            QTimer.singleShot(1000, self.generate_captcha_image)
        self.input.clear()


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OGCaptcha()
    window.show()
    sys.exit(app.exec())
