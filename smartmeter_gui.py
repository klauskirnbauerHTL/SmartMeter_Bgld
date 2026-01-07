"""
Smart Meter Netz Burgenland - GUI Anwendung
Grafische Oberfläche zum Konfigurieren und Starten des Downloaders
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox, QTextEdit,
    QGroupBox, QGridLayout, QMessageBox, QCheckBox, QDoubleSpinBox,
    QTabWidget, QFileDialog
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon
import logging

# Import des Downloaders
try:
    from smartmeter_downloader import SmartMeterDownloader
except ImportError:
    SmartMeterDownloader = None

try:
    from smartmeter_selenium import SmartMeterSeleniumDownloader
except ImportError:
    SmartMeterSeleniumDownloader = None


class DownloadThread(QThread):
    """Thread für den Download, damit die GUI nicht einfriert"""
    
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, username, password, days_back, data_type, use_selenium=True, headless=True):
        super().__init__()
        self.username = username
        self.password = password
        self.days_back = days_back
        self.data_type = data_type
        self.use_selenium = use_selenium
        self.headless = headless
        
    def run(self):
        """Führt den Download aus"""
        try:
            # Logger umleiten, damit Ausgabe in der GUI erscheint
            class GUILogHandler(logging.Handler):
                def __init__(self, signal):
                    super().__init__()
                    self.signal = signal
                    
                def emit(self, record):
                    msg = self.format(record)
                    self.signal.emit(msg)
            
            logger = logging.getLogger(__name__)
            logger.handlers.clear()
            handler = GUILogHandler(self.log_signal)
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            if self.use_selenium:
                # Selenium-Download (funktioniert!)
                self.log_signal.emit("🌐 Verwende Selenium-Methode (Browser-basiert)")
                if self.headless:
                    self.log_signal.emit("ℹ️ Browser läuft im Hintergrund (headless)")
                else:
                    self.log_signal.emit("ℹ️ Browser wird sichtbar geöffnet")
                
                downloader = SmartMeterSeleniumDownloader(self.username, self.password, headless=self.headless)
                
                # Logger für Selenium setzen
                selenium_logger = logging.getLogger('smartmeter_selenium')
                selenium_logger.handlers.clear()
                selenium_logger.addHandler(handler)
                selenium_logger.setLevel(logging.INFO)
                
                # Login
                if downloader.login():
                    self.log_signal.emit("✅ Login erfolgreich")
                    
                    # CSV Download
                    csv_file = downloader.download_csv(days_back=self.days_back)
                    
                    if csv_file:
                        self.log_signal.emit(f"✅ CSV heruntergeladen: {csv_file}")
                        
                        # Analysiere die CSV
                        try:
                            from smartmeter_downloader import SmartMeterDownloader
                            temp_downloader = SmartMeterDownloader("", "")
                            results = temp_downloader.analyze_csv(csv_file)
                            self.log_signal.emit("✅ Analyse abgeschlossen")
                        except Exception as e:
                            self.log_signal.emit(f"⚠️ Analyse fehlgeschlagen: {str(e)}")
                        
                        downloader.close()
                        self.finished_signal.emit(True)
                    else:
                        self.log_signal.emit("⚠️ Kein CSV heruntergeladen")
                        downloader.close()
                        self.finished_signal.emit(False)
                else:
                    self.log_signal.emit("❌ Login fehlgeschlagen")
                    downloader.close()
                    self.finished_signal.emit(False)
            else:
                # API-Download (experimentell)
                self.log_signal.emit("🔌 Verwende API-Methode (experimentell)")
                
                # Downloader erstellen
                downloader = SmartMeterDownloader(self.username, self.password)
                
                # Logger auch für den Downloader setzen
                downloader_logger = logging.getLogger('smartmeter_downloader')
                downloader_logger.handlers.clear()
                downloader_logger.addHandler(handler)
                downloader_logger.setLevel(logging.INFO)
                
                # Download durchführen
                success = downloader.run_once(days_back=self.days_back, data_type=self.data_type)
                self.finished_signal.emit(success)
            
        except Exception as e:
            self.log_signal.emit(f"FEHLER: {str(e)}")
            self.finished_signal.emit(False)


class SmartMeterGUI(QMainWindow):
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        super().__init__()
        self.config_file = Path("config.json")
        self.download_thread = None
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setWindowTitle("Smart Meter Netz Burgenland - Downloader")
        self.setMinimumSize(800, 700)
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tabs erstellen
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Tab 1: Einstellungen
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "⚙️ Einstellungen")
        
        # Tab 2: Download & Auswertung
        download_tab = self.create_download_tab()
        tabs.addTab(download_tab, "📥 Download")
        
        # Tab 3: Über
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "ℹ️ Info")
        
    def create_settings_tab(self):
        """Erstellt den Einstellungs-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Titel
        title = QLabel("Konfiguration")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Login-Daten Gruppe
        login_group = QGroupBox("Login-Daten (smartmeter.netzburgenland.at)")
        login_layout = QGridLayout()
        
        login_layout.addWidget(QLabel("Benutzername (E-Mail):"), 0, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("deine.email@example.com")
        login_layout.addWidget(self.username_input, 0, 1)
        
        login_layout.addWidget(QLabel("Passwort:"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Dein Passwort")
        login_layout.addWidget(self.password_input, 1, 1)
        
        self.show_password_cb = QCheckBox("Passwort anzeigen")
        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)
        login_layout.addWidget(self.show_password_cb, 2, 1)
        
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # Download-Einstellungen Gruppe
        download_group = QGroupBox("Download-Einstellungen")
        download_layout = QGridLayout()
        
        download_layout.addWidget(QLabel("Zeitraum (Tage zurück):"), 0, 0)
        self.days_back_spinbox = QSpinBox()
        self.days_back_spinbox.setMinimum(1)
        self.days_back_spinbox.setMaximum(365)
        self.days_back_spinbox.setValue(7)
        self.days_back_spinbox.setSuffix(" Tage")
        download_layout.addWidget(self.days_back_spinbox, 0, 1)
        
        download_layout.addWidget(QLabel("Datenauflösung:"), 1, 0)
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["15min", "hourly", "daily", "monthly"])
        self.data_type_combo.setCurrentText("15min")
        download_layout.addWidget(self.data_type_combo, 1, 1)
        
        download_layout.addWidget(QLabel("Download-Methode:"), 2, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Selenium (Browser)", "API (schneller, experimentell)"])
        self.method_combo.setCurrentIndex(0)
        download_layout.addWidget(self.method_combo, 2, 1)
        
        self.headless_cb = QCheckBox("Browser im Hintergrund ausführen (headless)")
        self.headless_cb.setChecked(True)
        self.headless_cb.setToolTip("Wenn aktiviert, läuft der Browser unsichtbar im Hintergrund")
        download_layout.addWidget(self.headless_cb, 3, 0, 1, 2)
        
        download_layout.addWidget(QLabel("Strompreis (€/kWh):"), 4, 0)
        self.price_spinbox = QDoubleSpinBox()
        self.price_spinbox.setMinimum(0.0)
        self.price_spinbox.setMaximum(1.0)
        self.price_spinbox.setValue(0.30)
        self.price_spinbox.setSingleStep(0.01)
        self.price_spinbox.setDecimals(2)
        self.price_spinbox.setPrefix("€ ")
        download_layout.addWidget(self.price_spinbox, 4, 1)
        
        download_group.setLayout(download_layout)
        layout.addWidget(download_group)
        
        # Periodischer Download Gruppe
        periodic_group = QGroupBox("Periodischer Download")
        periodic_layout = QGridLayout()
        
        self.periodic_enabled_cb = QCheckBox("Automatischer periodischer Download aktiviert")
        periodic_layout.addWidget(self.periodic_enabled_cb, 0, 0, 1, 2)
        
        periodic_layout.addWidget(QLabel("Intervall:"), 1, 0)
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(168)  # Max 1 Woche
        self.interval_spinbox.setValue(24)
        self.interval_spinbox.setSuffix(" Stunden")
        periodic_layout.addWidget(self.interval_spinbox, 1, 1)
        
        periodic_group.setLayout(periodic_layout)
        layout.addWidget(periodic_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Einstellungen speichern")
        save_btn.clicked.connect(self.save_config)
        save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        button_layout.addWidget(save_btn)
        
        test_btn = QPushButton("🔍 Verbindung testen")
        test_btn.clicked.connect(self.test_connection)
        test_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; }")
        button_layout.addWidget(test_btn)
        
        layout.addLayout(button_layout)
        
        # Spacer
        layout.addStretch()
        
        return widget
    
    def create_download_tab(self):
        """Erstellt den Download-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Titel
        title = QLabel("Download & Auswertung")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Info
        info_label = QLabel(
            "Hier kannst du den Download manuell starten. "
            "Die Daten werden heruntergeladen und automatisch ausgewertet."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Download-Button
        self.download_btn = QPushButton("📥 Download jetzt starten")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setStyleSheet(
            "QPushButton { background-color: #FF9800; color: white; padding: 15px; "
            "font-size: 14px; font-weight: bold; }"
        )
        layout.addWidget(self.download_btn)
        
        # Log-Ausgabe
        log_label = QLabel("📋 Log-Ausgabe:")
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4; font-family: 'Courier New';")
        layout.addWidget(self.log_output)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Log löschen")
        clear_btn.clicked.connect(self.log_output.clear)
        button_layout.addWidget(clear_btn)
        
        open_folder_btn = QPushButton("📁 Downloads-Ordner öffnen")
        open_folder_btn.clicked.connect(self.open_downloads_folder)
        button_layout.addWidget(open_folder_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_about_tab(self):
        """Erstellt den Info-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Titel
        title = QLabel("Smart Meter Netz Burgenland - Downloader")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version = QLabel("Version 1.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: gray; margin-bottom: 20px;")
        layout.addWidget(version)
        
        # Beschreibung
        description = QLabel(
            "<h3>Über diese Anwendung</h3>"
            "<p>Diese Anwendung ermöglicht es dir, deine Stromverbrauchsdaten "
            "vom Smart Meter Portal der Netz Burgenland automatisch herunterzuladen "
            "und auszuwerten.</p>"
            "<h4>Features:</h4>"
            "<ul>"
            "<li>✅ Automatischer Login auf smartmeter.netzburgenland.at</li>"
            "<li>✅ Download von Verbrauchsdaten in verschiedenen Auflösungen</li>"
            "<li>✅ Automatische Datenauswertung mit Statistiken</li>"
            "<li>✅ Kostenschätzung basierend auf deinem Strompreis</li>"
            "<li>✅ Periodischer automatischer Download</li>"
            "<li>✅ Export als CSV und JSON</li>"
            "</ul>"
            "<h4>Datenauflösungen:</h4>"
            "<ul>"
            "<li><b>15min:</b> 15-Minuten-Werte (sehr detailliert)</li>"
            "<li><b>hourly:</b> Stündliche Werte</li>"
            "<li><b>daily:</b> Tägliche Werte</li>"
            "<li><b>monthly:</b> Monatliche Werte</li>"
            "</ul>"
            "<h4>Hinweise:</h4>"
            "<ul>"
            "<li>⚠️ Smart Meter Daten sind oft mit 1-2 Tagen Verzögerung verfügbar</li>"
            "<li>⚠️ Bitte verwende angemessene Download-Intervalle</li>"
            "<li>⚠️ Deine Zugangsdaten werden lokal gespeichert</li>"
            "</ul>"
            "<hr>"
            "<p style='text-align: center; color: gray;'>"
            "© 2026 | Erstellt für HTL Pinkafeld"
            "</p>"
        )
        description.setWordWrap(True)
        description.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(description)
        
        # Spacer
        layout.addStretch()
        
        return widget
    
    def toggle_password_visibility(self, state):
        """Schaltet Passwort-Sichtbarkeit um"""
        if state == Qt.CheckState.Checked.value:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def save_config(self):
        """Speichert die Konfiguration"""
        config = {
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "days_back": self.days_back_spinbox.value(),
            "data_type": self.data_type_combo.currentText(),
            "download_method": self.method_combo.currentText(),
            "headless": self.headless_cb.isChecked(),
            "price_per_kwh": self.price_spinbox.value(),
            "periodic_enabled": self.periodic_enabled_cb.isChecked(),
            "interval_hours": self.interval_spinbox.value()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "Erfolg",
                "Einstellungen wurden erfolgreich gespeichert!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Speichern: {str(e)}"
            )
    
    def load_config(self):
        """Lädt die Konfiguration"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.username_input.setText(config.get("username", ""))
            self.password_input.setText(config.get("password", ""))
            self.days_back_spinbox.setValue(config.get("days_back", 7))
            self.data_type_combo.setCurrentText(config.get("data_type", "15min"))
            self.method_combo.setCurrentText(config.get("download_method", "Selenium (Browser)"))
            self.headless_cb.setChecked(config.get("headless", True))
            self.price_spinbox.setValue(config.get("price_per_kwh", 0.30))
            self.periodic_enabled_cb.setChecked(config.get("periodic_enabled", False))
            self.interval_spinbox.setValue(config.get("interval_hours", 24))
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Warnung",
                f"Fehler beim Laden der Konfiguration: {str(e)}"
            )
    
    def test_connection(self):
        """Testet die Verbindung zum Smart Meter Portal"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(
                self,
                "Fehlende Daten",
                "Bitte gib Benutzername und Passwort ein!"
            )
            return
        
        method = self.method_combo.currentText()
        
        if "Selenium" in method:
            # Test mit Selenium (funktioniert!)
            if SmartMeterSeleniumDownloader is None:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    "Selenium ist nicht installiert!\n"
                    "Installiere es mit: pip install selenium"
                )
                return
            
            try:
                self.log_output.append("🔍 Teste Verbindung mit Selenium...\n")
                
                # Verwende headless aus Checkbox
                use_headless = self.headless_cb.isChecked()
                if use_headless:
                    self.log_output.append("ℹ️ Browser läuft im Hintergrund\n")
                else:
                    self.log_output.append("ℹ️ Browser öffnet sich gleich...\n")
                
                # Wichtig: Erstelle Downloader in try-block
                downloader = None
                try:
                    downloader = SmartMeterSeleniumDownloader(username, password, headless=use_headless)
                    
                    if downloader.login():
                        self.log_output.append("✅ Verbindung erfolgreich!\n")
                        QMessageBox.information(
                            self,
                            "Erfolg",
                            "Verbindung zum Smart Meter Portal erfolgreich!\n"
                            "Du kannst jetzt Daten herunterladen."
                        )
                    else:
                        self.log_output.append("❌ Verbindung fehlgeschlagen!\n")
                        QMessageBox.warning(
                            self,
                            "Verbindungsfehler",
                            "Login fehlgeschlagen!\n"
                            "Bitte überprüfe deine Zugangsdaten."
                        )
                finally:
                    # Stelle sicher, dass Browser geschlossen wird
                    if downloader:
                        try:
                            downloader.close()
                        except:
                            pass
                            
            except Exception as e:
                self.log_output.append(f"❌ Fehler: {str(e)}\n")
                import traceback
                self.log_output.append(f"Details: {traceback.format_exc()}\n")
                QMessageBox.critical(
                    self,
                    "Fehler",
                    f"Fehler beim Verbindungstest:\n{str(e)}\n\n"
                    "Prüfe das Log für Details."
                )
        else:
            # Test mit API (experimentell)
            if SmartMeterDownloader is None:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    "Der SmartMeterDownloader konnte nicht geladen werden!"
                )
                return
            
            try:
                self.log_output.append("🔍 Teste Verbindung mit API...\n")
                downloader = SmartMeterDownloader(username, password)
                
                if downloader.login():
                    self.log_output.append("✅ Verbindung erfolgreich!\n")
                    QMessageBox.information(
                        self,
                        "Erfolg",
                        "Verbindung zum Smart Meter Portal erfolgreich!"
                    )
                else:
                    self.log_output.append("❌ Verbindung fehlgeschlagen!\n")
                    QMessageBox.warning(
                        self,
                        "Verbindungsfehler",
                        "Login fehlgeschlagen!\n"
                        "Versuche die Selenium-Methode."
                    )
            except Exception as e:
                self.log_output.append(f"❌ Fehler: {str(e)}\n")
                QMessageBox.critical(
                    self,
                    "Fehler",
                    f"Fehler beim Verbindungstest:\n{str(e)}"
                )
    
    def start_download(self):
        """Startet den Download"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(
                self,
                "Fehlende Daten",
                "Bitte gib Benutzername und Passwort ein!"
            )
            return
        
        method = self.method_combo.currentText()
        use_selenium = "Selenium" in method
        
        if use_selenium and SmartMeterSeleniumDownloader is None:
            QMessageBox.critical(
                self,
                "Fehler",
                "Selenium ist nicht installiert!\n"
                "Installiere es mit: pip install selenium"
            )
            return
        
        if not use_selenium and SmartMeterDownloader is None:
            QMessageBox.critical(
                self,
                "Fehler",
                "Der SmartMeterDownloader konnte nicht geladen werden!"
            )
            return
        
        if self.download_thread and self.download_thread.isRunning():
            QMessageBox.warning(
                self,
                "Download läuft",
                "Es läuft bereits ein Download!"
            )
            return
        
        # Download-Button deaktivieren
        self.download_btn.setEnabled(False)
        self.download_btn.setText("⏳ Download läuft...")
        
        # Log löschen
        self.log_output.clear()
        
        # Thread starten
        self.download_thread = DownloadThread(
            username,
            password,
            self.days_back_spinbox.value(),
            self.data_type_combo.currentText(),
            use_selenium=use_selenium,
            headless=self.headless_cb.isChecked()
        )
        self.download_thread.log_signal.connect(self.append_log)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()
    
    def append_log(self, text):
        """Fügt Text zum Log hinzu"""
        self.log_output.append(text)
        # Automatisch nach unten scrollen
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def download_finished(self, success):
        """Wird aufgerufen wenn der Download beendet ist"""
        self.download_btn.setEnabled(True)
        self.download_btn.setText("📥 Download jetzt starten")
        
        if success:
            QMessageBox.information(
                self,
                "Erfolg",
                "Download und Auswertung erfolgreich abgeschlossen!\n"
                "Die Dateien findest du im 'downloads' Ordner."
            )
        else:
            QMessageBox.warning(
                self,
                "Fehler",
                "Download ist fehlgeschlagen!\n"
                "Bitte überprüfe das Log für Details."
            )
    
    def open_downloads_folder(self):
        """Öffnet den Downloads-Ordner"""
        downloads_dir = Path("downloads")
        if not downloads_dir.exists():
            downloads_dir.mkdir()
        
        # Öffne im Dateimanager
        import subprocess
        import platform
        
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(downloads_dir)])
        elif platform.system() == "Windows":
            subprocess.run(["explorer", str(downloads_dir)])
        else:  # Linux
            subprocess.run(["xdg-open", str(downloads_dir)])


def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    
    # Stil setzen
    app.setStyle("Fusion")
    
    # Hauptfenster erstellen
    window = SmartMeterGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
