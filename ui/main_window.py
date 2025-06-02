import os
import subprocess
import re
import json
import socket
import requests
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit,
    QComboBox, QFileDialog, QMessageBox, QFrame, QApplication, QListWidget, QListWidgetItem,
    QTabWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QToolButton
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QTextCursor

LANGUAGES = [
    ("English", "en"),
    ("Türkçe", "tr"),
    ("Deutsch", "de"),
    ("Español", "es"),
    ("Français", "fr"),
]

SCAN_HISTORY_FILE = "scan_history.json"

DARK_STYLE = """
QWidget {background: #161a21; color: #fff; font-family: 'Segoe UI', 'Arial', sans-serif;}
QLineEdit {background: rgba(30,34,45,0.9); color: #baf7ff; border: 1.5px solid #303a46; border-radius: 13px; padding: 10px 18px; font-size: 17px;}
QLineEdit:focus {border: 2px solid #23e7ff; background: #19202a;}
QComboBox {background: #18202a; color: #23e7ff; border-radius: 11px; border: 1.2px solid #25303a; padding: 8px 18px; font-size: 15px;}
QComboBox QAbstractItemView {background: #222a36; color: #23e7ff; selection-background-color: #21badd;}
QPushButton {border-radius: 13px;}
QTextEdit {background: rgba(15,22,28,0.88); color: #fff; font-family: 'Fira Mono', 'Consolas', monospace; font-size: 15px; border-radius: 13px; border: 1.2px solid #24344a; padding: 16px 19px;}
QTableWidget {background: #131923; color: #baf7ff; border-radius: 13px;}
QHeaderView::section {background: #19202a; color: #21badd;}
QTabBar::tab {background: #18202a; color: #23e7ff; border-radius: 10px; padding: 8px 18px; font-size: 15px; margin: 2px;}
QTabBar::tab:selected {background: #23e7ff; color: #161a21;}
QTabBar::tab:hover {background: #1bd2ff; color: #222;}
QPushButton {padding: 10px 22px; font-size: 15px; font-weight: 600;}
"""

LIGHT_STYLE = """
QWidget {background: #f4f8fb; color: #181c25; font-family: 'Segoe UI', 'Arial', sans-serif;}
QLineEdit {background: #fff; color: #181c25; border: 1.5px solid #aac0d6; border-radius: 13px; padding: 10px 18px; font-size: 17px;}
QLineEdit:focus {border: 2px solid #57bfff; background: #e6f4ff;}
QComboBox {background: #e0eaf5; color: #2272aa; border-radius: 11px; border: 1.2px solid #b1cbe7; padding: 8px 18px; font-size: 15px;}
QComboBox QAbstractItemView {background: #f2fbff; color: #2272aa; selection-background-color: #b1eaff;}
QPushButton {border-radius: 13px;}
QTextEdit {background: #fff; color: #222; font-family: 'Fira Mono', 'Consolas', monospace; font-size: 15px; border-radius: 13px; border: 1.2px solid #bcdaf5; padding: 16px 19px;}
QTableWidget {background: #f9fdff; color: #222; border-radius: 13px;}
QHeaderView::section {background: #e9f5ff; color: #2272aa;}
QTabBar::tab {background: #e0eaf5; color: #2272aa; border-radius: 10px; padding: 8px 18px; font-size: 15px; margin: 2px;}
QTabBar::tab:selected {background: #57bfff; color: #f4f8fb;}
QTabBar::tab:hover {background: #b1eaff; color: #181c25;}
QPushButton {padding: 10px 22px; font-size: 15px; font-weight: 600;}
"""

TRANSLATIONS = {
    "en": {
        "title": "AlwaysOnGuard Nmap UI",
        "scan": "Start Scan 🚀",
        "save": "Save Output",
        "exit": "Exit",
        "target_placeholder": "Target IP, domain or range...",
        "profile": "Scan Profile:",
        "command": "🔧 Command:",
        "no_target": "Please enter a target.",
        "scan_running": "🟦 Scanning...",
        "save_warning": "There is no output to save.",
        "save_success": "Output saved successfully.",
        "closing": "Closing the program...",
        "warning": "Warning",
        "success": "Success",
        "history": "Scan History",
        "clear_history": "Clear History",
        "tab_nmap_output": "Nmap Output",
        "tab_ports_hosts": "Ports/Hosts",
        "tab_host_details": "Host Details",
        "tab_scans": "Scans",
        "status_label": "Status",
        "command_label": "Command",
        "scan_delete": "Delete Scan",
        "scan_deleted": "Scan deleted.",
        "geoip_btn": "GeoIP/WHOIS Lookup",
        "geoip_title": "GeoIP & WHOIS Information",
        "geoip_error": "GeoIP/WHOIS lookup failed.",
        "geoip_label": "GeoIP/WHOIS:",
        "scan_profiles": [
            "Intense scan",
            "Intense scan plus UDP",
            "Intense scan, all TCP ports",
            "Intense scan, no ping",
            "Ping scan",
            "Quick scan",
            "Quick scan plus",
            "Quick traceroute",
            "Regular scan",
            "Slow comprehensive scan"
        ]
    },
    "tr": {
        "title": "AlwaysOnGuard Nmap Arayüzü",
        "scan": "Taramayı Başlat 🚀",
        "save": "Çıktıyı Kaydet",
        "exit": "Çıkış",
        "target_placeholder": "Hedef IP, alan adı veya aralık...",
        "profile": "Tarama Profili:",
        "command": "🔧 Komut:",
        "no_target": "Lütfen bir hedef girin.",
        "scan_running": "🟦 Taranıyor...",
        "save_warning": "Kaydedilecek bir çıktı yok.",
        "save_success": "Sonuç başarıyla kaydedildi.",
        "closing": "Program kapatılıyor...",
        "warning": "Uyarı",
        "success": "Başarılı",
        "history": "Tarama Geçmişi",
        "clear_history": "Geçmişi Temizle",
        "tab_nmap_output": "Nmap Çıktısı",
        "tab_ports_hosts": "Portlar/Host",
        "tab_host_details": "Host Detayları",
        "tab_scans": "Taramalar",
        "status_label": "Durum",
        "command_label": "Komut",
        "scan_delete": "Taramayı Sil",
        "scan_deleted": "Tarama silindi.",
        "geoip_btn": "GeoIP/WHOIS Sorgula",
        "geoip_title": "GeoIP & WHOIS Bilgisi",
        "geoip_error": "GeoIP/WHOIS sorgusu başarısız oldu.",
        "geoip_label": "GeoIP/WHOIS:",
        "scan_profiles": [
            "Yoğun tarama",
            "Yoğun tarama + UDP",
            "Yoğun tarama, tüm TCP portları",
            "Yoğun tarama, ping yok",
            "Ping taraması",
            "Hızlı tarama",
            "Hızlı tarama plus",
            "Hızlı traceroute",
            "Normal tarama",
            "Yavaş kapsamlı tarama"
        ]
    },
    "de": {
        "title": "AlwaysOnGuard Nmap Oberfläche",
        "scan": "Scan starten 🚀",
        "save": "Ausgabe speichern",
        "exit": "Beenden",
        "target_placeholder": "Ziel-IP, Domain oder Bereich...",
        "profile": "Scan-Profil:",
        "command": "🔧 Befehl:",
        "no_target": "Bitte ein Ziel eingeben.",
        "scan_running": "🟦 Scanne...",
        "save_warning": "Kein Ergebnis zum Speichern.",
        "save_success": "Ausgabe erfolgreich gespeichert.",
        "closing": "Programm wird beendet...",
        "warning": "Warnung",
        "success": "Erfolg",
        "history": "Scan-Verlauf",
        "clear_history": "Verlauf löschen",
        "tab_nmap_output": "Nmap Ausgabe",
        "tab_ports_hosts": "Ports/Hosts",
        "tab_host_details": "Host Details",
        "tab_scans": "Scans",
        "status_label": "Status",
        "command_label": "Befehl",
        "scan_delete": "Scan löschen",
        "scan_deleted": "Scan gelöscht.",
        "geoip_btn": "GeoIP/WHOIS Abfrage",
        "geoip_title": "GeoIP & WHOIS Information",
        "geoip_error": "GeoIP/WHOIS-Abfrage fehlgeschlagen.",
        "geoip_label": "GeoIP/WHOIS:",
        "scan_profiles": [
            "Intensiver Scan",
            "Intensiver Scan plus UDP",
            "Intensiver Scan, alle TCP-Ports",
            "Intensiver Scan, kein Ping",
            "Ping-Scan",
            "Schneller Scan",
            "Schneller Scan plus",
            "Schnelles Traceroute",
            "Regulärer Scan",
            "Langsamer umfassender Scan"
        ]
    },
    "es": {
        "title": "AlwaysOnGuard Nmap Interfaz",
        "scan": "Iniciar Escaneo 🚀",
        "save": "Guardar Salida",
        "exit": "Salir",
        "target_placeholder": "IP objetivo, dominio o rango...",
        "profile": "Perfil de Escaneo:",
        "command": "🔧 Comando:",
        "no_target": "Por favor, ingrese un objetivo.",
        "scan_running": "🟦 Escaneando...",
        "save_warning": "No hay salida para guardar.",
        "save_success": "Salida guardada exitosamente.",
        "closing": "Cerrando el programa...",
        "warning": "Advertencia",
        "success": "Éxito",
        "history": "Historial de Escaneos",
        "clear_history": "Borrar Historial",
        "tab_nmap_output": "Salida Nmap",
        "tab_ports_hosts": "Puertos/Hosts",
        "tab_host_details": "Detalles del Host",
        "tab_scans": "Escaneos",
        "status_label": "Estado",
        "command_label": "Comando",
        "scan_delete": "Eliminar Scan",
        "scan_deleted": "Scan eliminado.",
        "geoip_btn": "Consultar GeoIP/WHOIS",
        "geoip_title": "GeoIP & Información WHOIS",
        "geoip_error": "La consulta GeoIP/WHOIS falló.",
        "geoip_label": "GeoIP/WHOIS:",
        "scan_profiles": [
            "Escaneo intenso",
            "Escaneo intenso más UDP",
            "Escaneo intenso, todos los puertos TCP",
            "Escaneo intenso, sin ping",
            "Escaneo de ping",
            "Escaneo rápido",
            "Escaneo rápido plus",
            "Traceroute rápido",
            "Escaneo regular",
            "Escaneo lento y completo"
        ]
    },
    "fr": {
        "title": "AlwaysOnGuard Nmap UI",
        "scan": "Démarrer l'analyse 🚀",
        "save": "Enregistrer la sortie",
        "exit": "Quitter",
        "target_placeholder": "IP cible, domaine ou plage...",
        "profile": "Profil d'analyse :",
        "command": "🔧 Commande :",
        "no_target": "Veuillez entrer une cible.",
        "scan_running": "🟦 Analyse en cours...",
        "save_warning": "Aucune sortie à enregistrer.",
        "save_success": "Sortie enregistrée avec succès.",
        "closing": "Fermeture du programme...",
        "warning": "Avertissement",
        "success": "Succès",
        "history": "Historique d'analyse",
        "clear_history": "Effacer l'historique",
        "tab_nmap_output": "Sortie Nmap",
        "tab_ports_hosts": "Ports/Hôtes",
        "tab_host_details": "Détails du Hôte",
        "tab_scans": "Scans",
        "status_label": "Statut",
        "command_label": "Commande",
        "scan_delete": "Supprimer le Scan",
        "scan_deleted": "Scan supprimé.",
        "geoip_btn": "Recherche GeoIP/WHOIS",
        "geoip_title": "Informations GeoIP & WHOIS",
        "geoip_error": "La recherche GeoIP/WHOIS a échoué.",
        "geoip_label": "GeoIP/WHOIS :",
        "scan_profiles": [
            "Analyse intense",
            "Analyse intense plus UDP",
            "Analyse intense, tous les ports TCP",
            "Analyse intense, sans ping",
            "Analyse de ping",
            "Analyse rapide",
            "Analyse rapide plus",
            "Traceroute rapide",
            "Analyse normale",
            "Analyse complète lente"
        ]
    }
}
# ... (Yukarıdaki kodun devamı)

COPY_TEXTS = {
    "en": {"copy": "Copy", "copied": "Copied!"},
    "tr": {"copy": "Kopyala", "copied": "Kopyalandı!"},
    "de": {"copy": "Kopieren", "copied": "Kopiert!"},
    "es": {"copy": "Copiar", "copied": "¡Copiado!"},
    "fr": {"copy": "Copier", "copied": "Copié !"}
}

VULN_KNOWN = {
    # (Yukarıda olduğu gibi, her dil için port açıklamaları)
    # ...
}

NMAP_PROFILE_PARAMS = [
    "-T4 -A -v",
    "-sS -sU -T4 -A -v",
    "-p 1-65535 -T4 -A -v",
    "-T4 -A -v -Pn",
    "-sn",
    "-T4 -F",
    "-T4 -F --version-light",
    "-sn --traceroute",
    "",
    "-sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script=default"
]

class GlassFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
        QFrame {
            background: rgba(24, 28, 38, 0.82);
            border-radius: 22px;
            border: 1.5px solid #222;
            box-shadow: 0 4px 32px 0 rgba(10,30,70,0.16);
        }
        """)

class NmapWorker(QThread):
    output_received = Signal(str)
    scan_finished = Signal(str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self._stop = False

    def run(self):
        process = subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        full_output = ""
        for line in process.stdout:
            if self._stop:
                process.terminate()
                break
            full_output += line
            self.output_received.emit(line)
        process.wait()
        self.scan_finished.emit(full_output)

    def stop(self):
        self._stop = True

class NmapGUI(QWidget):
    def __init__(self, icon_path=None):
        super().__init__()
        self.current_lang = "en"
        self.setWindowTitle(TRANSLATIONS["en"]["title"])
        self.resize(1200, 650)
        self.dark_mode = True
        self.apply_theme()

        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.scan_history = []
        self.worker = None
        self.load_history_from_file()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(18)

        history_panel = QVBoxLayout()
        history_panel.setSpacing(8)

        self.history_title = QLabel()
        self.history_title.setAlignment(Qt.AlignCenter)
        history_panel.addWidget(self.history_title)

        self.history_list = QListWidget()
        self.history_list.setMinimumWidth(250)
        self.history_list.setMaximumWidth(370)
        self.history_list.setStyleSheet("""
            QListWidget {
                background: #19202a;
                color: #1bd2ff;
                border-radius: 13px;
                font-size: 15px;
                padding: 8px 5px;
            }
            QListWidget::item:selected {
                background: #23e7ff44;
                color: #fff;
            }
        """)
        self.history_list.itemClicked.connect(self.load_history_item)
        history_panel.addWidget(self.history_list, 1)

        self.clear_history_btn = QPushButton()
        self.clear_history_btn.setStyleSheet(
            "QPushButton {background: #ffdd57; color: #222; border-radius: 13px; font-weight: bold;} QPushButton:hover{background: #ffe799;}")
        self.clear_history_btn.clicked.connect(self.clear_history)
        history_panel.addWidget(self.clear_history_btn)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        header = QHBoxLayout()
        logo = QLabel("🛡️")
        logo.setStyleSheet("font-size: 44px; margin-right: 8px;")
        header.addWidget(logo, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        title = QLabel()
        title.setTextFormat(Qt.RichText)
        title.setStyleSheet("""
            QLabel {
                color: #23e7ff;
                font-size: 30px;
                font-weight: bold;
                letter-spacing: 1.5px;
            }
        """)
        self.title_label = title
        header.addWidget(self.title_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        header.addStretch()

        self.theme_button = QPushButton("Dark Theme")
        self.theme_button.setMinimumWidth(100)
        self.theme_button.setMaximumWidth(180)
        self.theme_button.setToolTip("Toggle Dark/Light Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setStyleSheet(
            "QPushButton {background: #121620; color: #ffdd57; border-radius: 13px; font-size: 15px; font-weight: bold; padding: 6px 14px;} QPushButton:hover{background: #163642;}")
        header.addWidget(self.theme_button)

        self.language_combo = QComboBox()
        for name, code in LANGUAGES:
            self.language_combo.addItem(name, code)
        self.language_combo.setCurrentIndex(0)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        header.addWidget(self.language_combo)
        right_panel.addLayout(header)

        glass = GlassFrame()
        glass_layout = QVBoxLayout(glass)
        glass_layout.setContentsMargins(32, 28, 32, 28)
        glass_layout.setSpacing(13)

        row1 = QHBoxLayout()
        row1.setSpacing(15)
        self.target_input = QLineEdit()
        self.target_input.setMinimumWidth(225)
        row1.addWidget(QLabel("🎯", self))
        row1.addWidget(self.target_input, 3)

        self.profile_label = QLabel()
        row1.addWidget(self.profile_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self.update_command)
        row1.addWidget(self.profile_combo, 2)
        glass_layout.addLayout(row1)

        geoip_row = QHBoxLayout()
        self.geoip_btn = QPushButton()
        self.geoip_btn.setStyleSheet(
            "QPushButton {background: #1bd2ff; color: #222; border-radius: 13px; font-weight: bold;} QPushButton:hover{background: #23e7ff;}")
        self.geoip_btn.setText(self.tr_text("geoip_btn"))
        self.geoip_btn.clicked.connect(self.do_geoip_lookup)
        geoip_row.addWidget(self.geoip_btn)
        self.geoip_label = QLabel()
        geoip_row.addWidget(self.geoip_label)
        glass_layout.addLayout(geoip_row)

        cmd_row = QHBoxLayout()
        self.command_label = QLabel()
        cmd_row.addWidget(self.command_label)
        self.command_edit = QLineEdit()
        self.command_edit.textChanged.connect(self.user_command_changed)
        cmd_row.addWidget(self.command_edit, 1)
        self.copy_command_btn = QToolButton()
        self.copy_command_btn.setText(COPY_TEXTS[self.current_lang]["copy"])
        self.copy_command_btn.setToolTip(COPY_TEXTS[self.current_lang]["copy"])
        self.copy_command_btn.clicked.connect(self.copy_cli_command)
        cmd_row.addWidget(self.copy_command_btn)
        glass_layout.addLayout(cmd_row)

        btn_row = QHBoxLayout()
        self.scan_button = QPushButton()
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_button.setStyleSheet(
            "QPushButton {background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #21badd, stop:1 #23e7ff); color: #111a22; border-radius: 14px; padding: 11px 38px; font-size: 17px; font-weight: bold; letter-spacing:1px;} QPushButton:hover {background: #1bd2ff;}")
        btn_row.addWidget(self.scan_button)
        self.save_button = QPushButton()
        self.save_button.clicked.connect(self.save_output)
        self.save_button.setStyleSheet(
            "QPushButton {background: transparent; border: 1.2px solid #21badd; color: #21d6ff; border-radius: 13px; font-size: 15px; font-weight: 600;} QPushButton:hover {background: #212e36; color: #fff;}")
        btn_row.addWidget(self.save_button)
        btn_row.addStretch()
        self.exit_button = QPushButton()
        self.exit_button.clicked.connect(self.close_app)
        self.exit_button.setStyleSheet(
            "QPushButton {background: #222c37; color: #ff5978; border-radius: 13px; font-size: 15px; font-weight: 600; border: 1.2px solid #ff5978;} QPushButton:hover {background: #ff5978; color: #fff;}")
        btn_row.addWidget(self.exit_button, alignment=Qt.AlignRight | Qt.AlignBottom)
        glass_layout.addLayout(btn_row)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {background: #18202a; color: #23e7ff; border-radius: 10px; padding: 8px 18px; font-size: 15px; margin: 2px;}
            QTabBar::tab:selected {background: #23e7ff; color: #161a21;}
            QTabBar::tab:hover {background: #1bd2ff; color: #222;}
        """)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.ports_table = QTableWidget()
        self.ports_table.setColumnCount(6)
        self.ports_table.setHorizontalHeaderLabels(['Port', 'Protocol', 'State', 'Service', 'Version', '⚠️'])
        self.ports_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ports_table.cellClicked.connect(self.show_vuln_tooltip)
        self.host_details = QTextEdit()
        self.host_details.setReadOnly(True)

        self.scans_tab = QWidget()
        scans_layout = QVBoxLayout(self.scans_tab)
        self.scans_list = QListWidget()
        scans_layout.addWidget(self.scans_list)
        self.status_label = QLabel()
        scans_layout.addWidget(self.status_label)
        self.command_label = QLabel()
        scans_layout.addWidget(self.command_label)
        self.delete_scan_btn = QPushButton()
        self.delete_scan_btn.setStyleSheet(
            "QPushButton {background: #ffdd57; color: #222; border-radius: 13px; font-weight: bold;} QPushButton:hover{background: #ffe799;}")
        self.delete_scan_btn.clicked.connect(self.delete_selected_scan)
        scans_layout.addWidget(self.delete_scan_btn)

        self.tabs.addTab(self.output_text, "")
        self.tabs.addTab(self.ports_table, "")
        self.tabs.addTab(self.host_details, "")
        self.tabs.addTab(self.scans_tab, "")

        glass_layout.addWidget(self.tabs)
        right_panel.addWidget(glass, 1)

        self.closing_label = QLabel()
        self.closing_label.setAlignment(Qt.AlignCenter)
        self.closing_label.setVisible(False)
        right_panel.addStretch()
        right_panel.addWidget(self.closing_label, alignment=Qt.AlignHCenter | Qt.AlignBottom)

        main_layout.addLayout(history_panel, 3)
        main_layout.addLayout(right_panel, 7)
        self.setLayout(main_layout)

        self._set_styles()
        self.current_profile_index = 0
        self.set_language("en")
        self.scans_list.itemSelectionChanged.connect(self.update_scan_details)
        self.refresh_history_lists()

    def copy_cli_command(self):
        params = self.command_edit.text().strip().split()
        target = self.target_input.text().strip()
        cmd = "nmap " + " ".join(params) + (" " + target if target else "")
        QApplication.clipboard().setText(cmd)
        lang = self.current_lang
        self.copy_command_btn.setText(COPY_TEXTS[lang]["copied"])
        QTimer.singleShot(900, lambda: self.copy_command_btn.setText(COPY_TEXTS[lang]["copy"]))

    def get_vuln_info(self, port_proto):
        lang = self.current_lang
        return VULN_KNOWN.get(lang, {}).get(port_proto, "")

    def show_vuln_tooltip(self, row, col):
        if col != 5:
            return
        port_item = self.ports_table.item(row, 0)
        proto_item = self.ports_table.item(row, 1)
        if not port_item or not proto_item:
            return
        port_proto = f"{port_item.text()}/{proto_item.text()}"
        info = self.get_vuln_info(port_proto)
        if info:
            QMessageBox.information(self, f"Vuln Info {port_proto}", info)
        else:
            QMessageBox.information(self, f"Vuln Info {port_proto}", {
                "en": "No known public summary for this port/service.",
                "tr": "Bu port/hizmet için bilinen bir özet yok.",
                "de": "Keine bekannte öffentliche Zusammenfassung für diesen Port/Dienst.",
                "es": "No hay resumen público conocido para este puerto/servicio.",
                "fr": "Aucun résumé public connu pour ce port/service."
            }[self.current_lang])

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet(DARK_STYLE)
            if hasattr(self, "theme_button"):
                self.theme_button.setText("Dark Theme")
        else:
            self.setStyleSheet(LIGHT_STYLE)
            if hasattr(self, "theme_button"):
                self.theme_button.setText("Light Theme")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def save_history_to_file(self):
        try:
            with open(SCAN_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.scan_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("History save error:", e)

    def load_history_from_file(self):
        if os.path.exists(SCAN_HISTORY_FILE):
            try:
                with open(SCAN_HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.scan_history = json.load(f)
            except Exception as e:
                print("History load error:", e)
                self.scan_history = []
        else:
            self.scan_history = []

    def refresh_history_lists(self):
        self.history_list.clear()
        self.scans_list.clear()
        for scan in self.scan_history:
            txt = f"[{scan['timestamp']}] {scan['target']}"
            self.history_list.addItem(txt)
            self.scans_list.addItem(txt)

    def _set_styles(self):
        self.history_list.setStyleSheet("""
            QListWidget {
                background: #19202a;
                color: #1bd2ff;
                border-radius: 13px;
                font-size: 15px;
                padding: 8px 5px;
            }
            QListWidget::item:selected {
                background: #23e7ff44;
                color: #fff;
            }
        """)
        self.host_details.setStyleSheet("""
            QTextEdit {margin-top: 8px; letter-spacing: 0.5px;}
        """)
        self.closing_label.setStyleSheet("""
            QLabel {color: #fff; background: rgba(40, 40, 40, 0.7); border-radius: 8px; font-size: 13px; padding: 6px 22px;}
        """)

    def set_language(self, lang_code):
        t = TRANSLATIONS[lang_code]
        self.current_lang = lang_code
        self.geoip_btn.setText(t["geoip_btn"])
        self.geoip_label.setText(f"{t['geoip_label']}")
        self.setWindowTitle(t["title"])
        self.title_label.setText(
            t["title"] + "<br><span style='font-size:18px;font-weight:400;color:#9ce7f7;'>Nmap Advanced UI</span>"
            if lang_code == "en"
            else t["title"] + "<br><span style='font-size:18px;font-weight:400;color:#9ce7f7;'>Nmap Gelişmiş Arayüz</span>"
        )
        self.scan_button.setText(t["scan"])
        self.save_button.setText(t["save"])
        self.exit_button.setText(t["exit"])
        self.target_input.setPlaceholderText(t["target_placeholder"])
        self.profile_label.setText(t["profile"])
        self.command_label.setText(t["command"])
        self.closing_label.setText(t["closing"])
        self.history_title.setText(t["history"])
        self.clear_history_btn.setText(t["clear_history"])
        self.tabs.setTabText(0, t["tab_nmap_output"])
        self.tabs.setTabText(1, t["tab_ports_hosts"])
        self.tabs.setTabText(2, t["tab_host_details"])
        self.tabs.setTabText(3, t["tab_scans"])
        self.delete_scan_btn.setText(t["scan_delete"])
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for name in t["scan_profiles"]:
            self.profile_combo.addItem(name)
        self.profile_combo.setCurrentIndex(self.current_profile_index)
        self.profile_combo.blockSignals(False)
        self.update_command()
        # Copy butonu güncelle
        self.copy_command_btn.setText(COPY_TEXTS[self.current_lang]["copy"])
        self.copy_command_btn.setToolTip(COPY_TEXTS[self.current_lang]["copy"])

    def on_language_changed(self, index):
        lang_code = self.language_combo.itemData(index)
        self.set_language(lang_code)

    def update_command(self):
        self.current_profile_index = self.profile_combo.currentIndex()
        if 0 <= self.current_profile_index < len(NMAP_PROFILE_PARAMS):
            params = NMAP_PROFILE_PARAMS[self.current_profile_index]
            self.command_edit.setText(params.strip())

    def user_command_changed(self):
        pass

    def tr_text(self, key):
        return TRANSLATIONS[self.current_lang][key]

    def start_scan(self):
        target = self.target_input.text().strip()
        if not target:
            self.output_text.setText(self.tr_text("no_target"))
            return
        params = self.command_edit.text().strip().split()
        cmd = ["nmap"] + params + [target]
        self.output_text.clear()
        self.output_text.setText(f'{self.tr_text("scan_running")}\n\n{self.tr_text("command")} <b>{" ".join(cmd)}</b>\n')
        self.output_text.repaint()
        self.tabs.setCurrentIndex(0)

        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.worker = NmapWorker(cmd)
        self.worker.output_received.connect(self.append_output)
        self.worker.scan_finished.connect(self.save_scan_result)
        self.worker.start()

    def append_output(self, line):
        self.output_text.moveCursor(QTextCursor.End)
        self.output_text.insertPlainText(line)
        self.output_text.moveCursor(QTextCursor.End)

    def save_scan_result(self, full_output):
        target = self.target_input.text().strip()
        params = self.command_edit.text().strip().split()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        scan_record = {
            "target": target,
            "params": params,
            "output": full_output,
            "timestamp": now,
        }
        self.scan_history.append(scan_record)
        self.save_history_to_file()
        self.refresh_history_lists()
        self.parse_ports_and_hosts(full_output)
        self.tabs.setCurrentIndex(1)

    def parse_ports_and_hosts(self, output):
        self.ports_table.setRowCount(0)
        port_regex = re.compile(r"^(\d+)\/(\w+)\s+(\w+)\s+([\w\-]+)\s*(.*)$")
        for line in output.splitlines():
            match = port_regex.match(line.strip())
            if match:
                row = self.ports_table.rowCount()
                self.ports_table.insertRow(row)
                for col in range(5):
                    val = match.group(col+1) if match.group(col+1) else ""
                    self.ports_table.setItem(row, col, QTableWidgetItem(val.strip()))
                port_proto = f"{match.group(1)}/{match.group(2)}"
                vuln = self.get_vuln_info(port_proto)
                vuln_btn = QTableWidgetItem("ℹ️" if vuln else "")
                vuln_btn.setTextAlignment(Qt.AlignCenter)
                self.ports_table.setItem(row, 5, vuln_btn)
        host_lines = []
        for line in output.splitlines():
            lstrip = line.strip()
            if lstrip.lower().startswith("os details:") or "mac address" in lstrip.lower() or "hostname:" in lstrip.lower() or lstrip.lower().startswith("device type:"):
                host_lines.append(lstrip)
        self.host_details.setText("\n".join(host_lines))

    def update_scan_details(self):
        idx = self.scans_list.currentRow()
        t = TRANSLATIONS[self.current_lang]
        if 0 <= idx < len(self.scan_history):
            scan = self.scan_history[idx]
            self.status_label.setText(f"{t['status_label']}: Tamamlandı")
            self.command_label.setText(f"{t['command_label']}: nmap {' '.join(scan['params'])} {scan['target']}")
        else:
            self.status_label.setText("")
            self.command_label.setText("")

    def delete_selected_scan(self):
        idx = self.scans_list.currentRow()
        if idx >= 0:
            self.scans_list.takeItem(idx)
            if 0 <= idx < len(self.scan_history):
                del self.scan_history[idx]
            self.save_history_to_file()
            self.refresh_history_lists()
            self.status_label.clear()
            self.command_label.clear()
            QMessageBox.information(self, self.tr_text("success"), self.tr_text("scan_deleted"))

    def load_history_item(self, item):
        index = self.history_list.row(item)
        if 0 <= index < len(self.scan_history):
            output = self.scan_history[index]["output"]
            self.output_text.setText(output)
            self.parse_ports_and_hosts(output)

    def clear_history(self):
        self.scan_history.clear()
        self.save_history_to_file()
        self.refresh_history_lists()

    def save_output(self):
        text = self.output_text.toPlainText()
        if not text:
            QMessageBox.warning(self, self.tr_text("warning"), self.tr_text("save_warning"))
            return
        filename, _ = QFileDialog.getSaveFileName(self, self.tr_text("save"), "nmap_output.txt", "Text File (*.txt)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(self, self.tr_text("success"), self.tr_text("save_success"))

    def close_app(self):
        self.closing_label.setVisible(True)
        QTimer.singleShot(5000, QApplication.quit)

    def do_geoip_lookup(self):
        t = TRANSLATIONS[self.current_lang]
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, t["warning"], t["no_target"])
            return

        ip = self._resolve_ip(target)
        if not ip:
            QMessageBox.warning(self, t["warning"], t["geoip_error"])
            return

        geoip_info = self._get_geoip(ip)
        whois_info = self._get_whois(ip)

        info = f"<b>IP:</b> {ip}<br>"
        if geoip_info:
            info += "<b>GeoIP:</b><br>"
            for k, v in geoip_info.items():
                info += f"{k}: {v}<br>"
        if whois_info:
            info += "<b>WHOIS:</b><br><pre style='font-size:13px;color:#2196f3;background:#222;'>{}</pre>".format(whois_info[:2000].replace('<', '&lt;'))
        else:
            info += f"<b>WHOIS:</b><br>{t['geoip_error']}"
        QMessageBox.information(self, t["geoip_title"], info)

    def _resolve_ip(self, target):
        try:
            ip = socket.gethostbyname(target)
            return ip
        except Exception:
            return None

    def _get_geoip(self, ip):
        try:
            resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "Country": data.get("country_name", ""),
                    "City": data.get("city", ""),
                    "Region": data.get("region", ""),
                    "Org": data.get("org", ""),
                    "ASN": data.get("asn", ""),
                    "Latitude": data.get("latitude", ""),
                    "Longitude": data.get("longitude", "")
                }
        except Exception:
            pass
        return None

    def _get_whois(self, ip):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(6)
            s.connect(("whois.iana.org", 43))
            s.send((ip + "\r\n").encode())
            response = b""
            while True:
                d = s.recv(4096)
                if not d:
                    break
                response += d
            s.close()
            for line in response.decode(errors="ignore").splitlines():
                if "refer:" in line:
                    whois_server = line.split(":", 1)[1].strip()
                    break
            else:
                whois_server = "whois.arin.net"
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(6)
            s.connect((whois_server, 43))
            s.send((ip + "\r\n").encode())
            response = b""
            while True:
                d = s.recv(4096)
                if not d:
                    break
                response += d
            s.close()
            whois_txt = response.decode(errors="ignore")
            return whois_txt
        except Exception:
            return None
