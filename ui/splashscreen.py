from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QGraphicsOpacityEffect, QFrame, QSizePolicy
)
from PySide6.QtGui import QFont, QPixmap
import os

LANGUAGES = [
    ("English", "en"),
    ("Türkçe", "tr"),
    ("Español", "es"),
    ("Deutsch", "de"),
    ("Français", "fr"),
]

TRANSLATIONS = {
    "en": {
        "select_language": "Select Language",
        "loading": "Loading..."
    },
    "tr": {
        "select_language": "Dil Seç",
        "loading": "Yükleniyor..."
    },
    "es": {
        "select_language": "Seleccionar idioma",
        "loading": "Cargando..."
    },
    "de": {
        "select_language": "Sprache auswählen",
        "loading": "Wird geladen..."
    },
    "fr": {
        "select_language": "Choisir la langue",
        "loading": "Chargement..."
    }
}

class SplashScreen(QWidget):
    def __init__(self, on_finished=None):
        super().__init__()
        self.setWindowTitle("AlwaysOnGuard Nmap UI")
        self.setFixedSize(480, 340)
        self.setStyleSheet("background-color: #101820;")
        self.on_finished = on_finished
        self.current_lang = "en"

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.init_language_buttons()

    def init_language_buttons(self):
        self.menu_frame = QFrame()
        self.menu_frame.setStyleSheet("""
            QFrame {
                background: #181f29;
                border-radius: 18px;
                border: 2px solid #23e7ff;
            }
        """)
        menu_layout = QVBoxLayout(self.menu_frame)
        menu_layout.setContentsMargins(32, 28, 32, 28)
        menu_layout.setSpacing(20)

        self.title = QLabel()
        self.title.setFont(QFont("Arial", 16, QFont.Bold))
        self.title.setStyleSheet("color: #23e7ff; letter-spacing:1px;")
        self.title.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(self.title)

        self.language_buttons = []
        for lang_name, lang_code in LANGUAGES:
            lang_btn = QPushButton(lang_name)
            lang_btn.setFixedHeight(42)
            lang_btn.setFont(QFont("Arial", 13, QFont.Bold))
            lang_btn.setStyleSheet("""
                QPushButton {
                    background: #16202c;
                    border: 2px solid #23e7ff;
                    border-radius: 10px;
                    color: #23e7ff;
                    font-size: 15px;
                    margin-top: 2px;
                }
                QPushButton:hover {
                    background: #23e7ff;
                    color: #181f29;
                }
            """)
            # Düzgün bağlamak için default parametre
            lang_btn.clicked.connect(lambda checked=False, code=lang_code: self.select_language(code))
            self.language_buttons.append(lang_btn)
            menu_layout.addWidget(lang_btn)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.menu_frame, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()
        self.set_language("en")

    def set_language(self, lang_code):
        self.current_lang = lang_code
        self.title.setText(TRANSLATIONS[lang_code]["select_language"])

    def select_language(self, lang_code):
        self.current_lang = lang_code
        self.go_to_loading()

    def go_to_loading(self):
        # Temizle
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.show_loading_screen()

    def show_loading_screen(self):
        loading_layout = QVBoxLayout()
        loading_layout.setContentsMargins(0, 0, 0, 0)
        loading_layout.setSpacing(0)
        loading_layout.setAlignment(Qt.AlignCenter)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        LOGO_PATH = os.path.normpath(os.path.join(BASE_DIR, "../assets/logo_full.png"))
        self.logo_label = QLabel(self)
        self.logo_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        logo_size = 300
        if os.path.exists(LOGO_PATH):
            pixmap = QPixmap(LOGO_PATH)
            pixmap = pixmap.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("margin-bottom: 12px;")
        loading_layout.addStretch(2)
        loading_layout.addWidget(self.logo_label, alignment=Qt.AlignHCenter)

        self.loading_label = QLabel(TRANSLATIONS[self.current_lang]["loading"], self)
        self.loading_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #23e7ff; margin-top: 10px; margin-bottom: 10px;")
        loading_layout.addWidget(self.loading_label, alignment=Qt.AlignHCenter)
        loading_layout.addStretch(3)

        QWidget().setLayout(self.main_layout)
        self.setLayout(loading_layout)

        # Animasyon
        self.logo_opacity = QGraphicsOpacityEffect(self.logo_label)
        self.logo_label.setGraphicsEffect(self.logo_opacity)
        self.logo_opacity.setOpacity(0.0)
        self.logo_anim = QPropertyAnimation(self.logo_opacity, b"opacity")
        self.logo_anim.setDuration(800)
        self.logo_anim.setStartValue(0.0)
        self.logo_anim.setEndValue(1.0)
        self.logo_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.text_opacity = QGraphicsOpacityEffect(self.loading_label)
        self.loading_label.setGraphicsEffect(self.text_opacity)
        self.text_opacity.setOpacity(0.0)
        self.text_anim = QPropertyAnimation(self.text_opacity, b"opacity")
        self.text_anim.setDuration(800)
        self.text_anim.setStartValue(0.0)
        self.text_anim.setEndValue(1.0)
        self.text_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.logo_anim.start()
        self.text_anim.start()

        QTimer.singleShot(5000, self.finish_splash)

    def finish_splash(self):
        if self.on_finished:
            self.on_finished(self.current_lang)