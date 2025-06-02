import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.splashscreen import SplashScreen
from ui.main_window import NmapGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.normpath(os.path.join(BASE_DIR, "assets/logo_radar.png"))
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    # main_window'ı başta yaratma, dili SplashScreen'den al!
    main_window = None

    def show_main(selected_lang):
        global main_window
        main_window = NmapGUI(icon_path=ICON_PATH)
        main_window.set_language(selected_lang)
        splash.close()
        main_window.show()

    splash = SplashScreen(on_finished=show_main)
    splash.show()
    app.exec()
