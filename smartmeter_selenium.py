"""
Smart Meter Netz Burgenland - Selenium Browser-basierter Downloader
Verwendet einen echten Browser um mit dem Portal zu interagieren
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
import json

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartMeterSeleniumDownloader:
    """Browser-basierter Downloader für Smart Meter Daten"""
    
    def __init__(self, username, password, headless=False):
        """
        Initialisiert den Downloader
        
        Args:
            username: Benutzername (E-Mail)
            password: Passwort
            headless: Browser im Hintergrund ausführen (True) oder sichtbar (False)
        """
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        
    def _setup_driver(self):
        """Richtet den Chrome WebDriver ein"""
        logger.info("Richte Browser ein...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Download-Einstellungen
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("✓ Browser gestartet")
            return True
        except Exception as e:
            logger.error(f"✗ Fehler beim Starten des Browsers: {e}")
            logger.error("Stelle sicher, dass Chrome und ChromeDriver installiert sind:")
            logger.error("  macOS: brew install chromedriver")
            return False
    
    def login(self):
        """
        Meldet sich auf dem Smart Meter Portal an
        
        Returns:
            bool: True wenn Login erfolgreich, sonst False
        """
        try:
            if not self.driver:
                if not self._setup_driver():
                    return False
            
            logger.info("Öffne Smart Meter Portal...")
            self.driver.get("https://smartmeter.netzburgenland.at/enview/enView.Portal/")
            
            # Warte bis Seite geladen ist
            time.sleep(3)
            
            logger.info("Suche Login-Formular...")
            
            # Verschiedene mögliche Selektoren für Login-Felder ausprobieren
            username_selectors = [
                "input[type='email']",
                "input[name='username']",
                "input[name='userName']",
                "input[name='email']",
                "input[id*='username' i]",
                "input[id*='email' i]",
                "input[placeholder*='mail' i]",
                "input[placeholder*='Benutzer' i]"
            ]
            
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[id*='password' i]",
                "input[placeholder*='Passwort' i]"
            ]
            
            username_field = None
            password_field = None
            
            # Versuche Username-Feld zu finden
            for selector in username_selectors:
                try:
                    username_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"  ✓ Username-Feld gefunden: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                logger.error("✗ Username-Feld nicht gefunden")
                self._save_debug_screenshot("login_page")
                return False
            
            # Versuche Password-Feld zu finden
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"  ✓ Password-Feld gefunden: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                logger.error("✗ Password-Feld nicht gefunden")
                self._save_debug_screenshot("login_page")
                return False
            
            # Gib Zugangsdaten ein
            logger.info("Gebe Zugangsdaten ein...")
            username_field.clear()
            username_field.send_keys(self.username)
            time.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(0.5)
            
            # Suche und klicke Login-Button
            login_button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[class*='login' i]",
                "button[id*='login' i]",
                "button:contains('Anmelden')",
                "button:contains('Login')",
                "a[class*='login' i]"
            ]
            
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"  ✓ Login-Button gefunden: {selector}")
                    break
                except:
                    continue
            
            if not login_button:
                # Versuche Enter zu drücken
                logger.info("  Kein Login-Button gefunden, drücke Enter...")
                from selenium.webdriver.common.keys import Keys
                password_field.send_keys(Keys.RETURN)
            else:
                logger.info("Klicke Login-Button...")
                login_button.click()
            
            # Warte auf erfolgreichen Login
            logger.info("Warte auf Login-Bestätigung...")
            time.sleep(5)
            
            # Prüfe auf Fehlermeldungen ZUERST
            error_found = False
            try:
                error_indicators = [
                    "//div[contains(@class, 'error')]",
                    "//span[contains(@class, 'error')]",
                    "//div[contains(@class, 'alert')]",
                    "//p[contains(@class, 'error')]",
                    "//*[contains(text(), 'ungültig')]",
                    "//*[contains(text(), 'falsch')]",
                    "//*[contains(text(), 'incorrect')]",
                    "//*[contains(text(), 'invalid')]",
                    "//mat-error",
                    "//div[@role='alert']"
                ]
                
                for xpath in error_indicators:
                    try:
                        errors = self.driver.find_elements(By.XPATH, xpath)
                        for error in errors:
                            if error.is_displayed() and error.text.strip():
                                logger.error(f"❌ Fehlermeldung gefunden: {error.text}")
                                error_found = True
                    except:
                        continue
            except:
                pass
            
            if error_found:
                self._save_debug_screenshot("login_error_message")
                logger.error("✗ Login mit Fehlermeldung abgelehnt")
                logger.info("Mögliche Gründe:")
                logger.info("  - Falsche Zugangsdaten")
                logger.info("  - Account gesperrt")
                logger.info("  - 2-Faktor-Authentifizierung erforderlich")
                return False
            
            # Prüfe ob Login erfolgreich war
            current_url = self.driver.current_url
            logger.info(f"Aktuelle URL: {current_url}")
            
            # Verschiedene Erfolgskriterien
            if 'login' not in current_url.lower():
                logger.info("✓ Login erfolgreich (nicht mehr auf Login-Seite)")
                return True
            
            # Suche nach Logout-Button oder Dashboard-Elementen
            try:
                logout_indicators = [
                    "a[href*='logout' i]",
                    "button:contains('Abmelden')",
                    "button:contains('Logout')",
                    "div[class*='dashboard' i]",
                    "div[class*='consumption' i]"
                ]
                
                for selector in logout_indicators:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logger.info(f"✓ Login erfolgreich (Dashboard-Element gefunden: {selector})")
                        return True
                    except:
                        continue
            except:
                pass
            
            # Prüfe auf Fehlermeldungen
            try:
                error_indicators = [
                    "div[class*='error' i]",
                    "span[class*='error' i]",
                    "div[class*='alert' i]",
                    "p[class*='error' i]"
                ]
                
                for selector in error_indicators:
                    try:
                        error = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if error.is_displayed() and error.text:
                            logger.error(f"Fehlermeldung gefunden: {error.text}")
                    except:
                        continue
            except:
                pass
            
            logger.error("✗ Login fehlgeschlagen")
            self._save_debug_screenshot("login_failed")
            return False
            
        except Exception as e:
            logger.error(f"Fehler beim Login: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self._save_debug_screenshot("login_exception")
            return False
    
    def _save_debug_screenshot(self, name):
        """Speichert einen Screenshot für Debugging"""
        try:
            screenshot_path = self.download_dir / f"debug_{name}_{int(time.time())}.png"
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"Screenshot gespeichert: {screenshot_path}")
        except:
            pass
    
    def download_csv(self, days_back=7):
        """
        Navigiert zur Download-Seite und lädt CSV herunter
        
        Args:
            days_back: Anzahl Tage zurück
            
        Returns:
            str: Pfad zur heruntergeladenen Datei oder None
        """
        try:
            logger.info("Navigiere zu Verbrauchsdaten...")
            
            # Navigiere direkt zur Chart-Seite mit dem Export-Button
            chart_url = "https://smartmeter.netzburgenland.at/enview/enView.Portal/#/consumption/values/chart/month"
            logger.info(f"Navigiere zu: {chart_url}")
            self.driver.get(chart_url)
            
            # Warte auf Seiten-Inhalte
            time.sleep(5)
            
            # Screenshot nach Navigation
            self._save_debug_screenshot("chart_page_loaded")
            
            # Screenshot der aktuellen Seite
            self._save_debug_screenshot("current_page")
            
            # Zähle Dateien vor dem Download
            existing_files = set(self.download_dir.glob("*.csv"))
            logger.info(f"Aktuell {len(existing_files)} CSV-Dateien im Download-Ordner")
            
            # Erweiterte Suche nach Export/Download-Buttons mit XPath und CSS
            download_selectors = [
                # WICHTIG: Der spezifische Export-Button des Portals
                ".btn-export",
                "button.btn-export",
                "[class*='btn-export']",
                "//button[contains(@class, 'btn-export')]",
                "//*[contains(@class, 'btn-export')]",
                
                # Text-basierte XPath (sehr zuverlässig)
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'export')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'export')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')]",
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'csv')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'csv')]",
                "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'export')]/..",
                "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')]/..",
                
                # Aria-labels und Titles
                "//button[@aria-label='Export']",
                "//button[@aria-label='Download']",
                "//button[@title='Export']",
                "//button[@title='Download']",
                "//*[@aria-label='Export']",
                "//*[@aria-label='Download']",
                
                # Material Design Icons
                "//mat-icon[contains(text(), 'download')]/..",
                "//mat-icon[contains(text(), 'file_download')]/..",
                "//mat-icon[contains(text(), 'cloud_download')]/..",
                "//mat-icon[contains(text(), 'save_alt')]/..",
                "//i[contains(@class, 'download')]/..",
                
                # CSS Selektoren
                "button[class*='export' i]",
                "button[class*='download' i]",
                "a[class*='export' i]",
                "a[class*='download' i]",
                "button[id*='export' i]",
                "button[id*='download' i]",
                
                # Spezifische Angular/Material Buttons
                "mat-button:has-text('Export')",
                "mat-raised-button:has-text('Export')",
                "mat-flat-button:has-text('Export')",
                "button[mat-button]:has-text('Export')",
                "button[mat-raised-button]:has-text('Export')"
            ]
            
            logger.info(f"Suche Download-Button mit {len(download_selectors)} verschiedenen Selektoren...")
            
            download_clicked = False
            for i, selector in enumerate(download_selectors, 1):
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                element_text = element.text or element.get_attribute('aria-label') or element.get_attribute('title') or ''
                                logger.info(f"✓ Download-Element gefunden (#{i}): {selector}")
                                logger.info(f"  Text: '{element_text}'")
                                
                                # Scrolle zum Element
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(0.5)
                                
                                # Versuche zu klicken
                                try:
                                    element.click()
                                except:
                                    # Fallback: JavaScript Click
                                    self.driver.execute_script("arguments[0].click();", element)
                                
                                download_clicked = True
                                logger.info("✓ Download-Button geklickt!")
                                time.sleep(3)
                                break
                        except Exception as e:
                            continue
                    
                    if download_clicked:
                        break
                        
                except Exception as e:
                    continue
            
            if not download_clicked:
                logger.warning("⚠️ Kein Download-Button gefunden")
                logger.info("Speichere Screenshot für manuelle Analyse...")
                self._save_debug_screenshot("no_download_button_found")
                
                # Zeige alle sichtbaren Buttons für Debugging
                try:
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    visible_buttons = [btn for btn in all_buttons if btn.is_displayed()]
                    logger.info(f"Gefundene Buttons auf der Seite: {len(visible_buttons)}")
                    for idx, btn in enumerate(visible_buttons[:10], 1):  # Erste 10 Buttons
                        btn_text = btn.text or btn.get_attribute('aria-label') or btn.get_attribute('class') or 'kein Text'
                        logger.info(f"  Button {idx}: {btn_text[:50]}")
                except:
                    pass
                
                return None
            
            # Export-Button wurde geklickt - jetzt auf Auswahlfenster warten
            logger.info("✓ Export-Button geklickt, warte auf Auswahlfenster...")
            time.sleep(3)
            
            self._save_debug_screenshot("after_export_click")
            
            # Suche nach dem "Speichern" Button im Dialog
            save_button_selectors = [
                # Span mit "Speichern" Text
                "//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'speichern')]/..",
                "//span[text()='Speichern']/..",
                "//span[text()='speichern']/..",
                "//button[.//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'speichern')]]",
                "//button[.//span[text()='Speichern']]",
                "//button[.//span[text()='speichern']]",
                
                # Direkter Button mit Speichern
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'speichern')]",
                "//button[text()='Speichern']",
                
                # Im Dialog-Container
                "//mat-dialog-actions//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'speichern')]/..",
                "//mat-dialog-container//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'speichern')]/..",
                "//*[@role='dialog']//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'speichern')]/..",
                
                # CSS Selektoren
                "button span:contains('Speichern')",
                "button span:contains('speichern')"
            ]
            
            button_clicked = False
            for i, selector in enumerate(save_button_selectors, 1):
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    # Nimm den ersten sichtbaren und enabled Button
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                element_text = element.text or element.get_attribute('aria-label') or element.get_attribute('class') or ''
                                logger.info(f"✓ Speichern-Button gefunden (#{i}): {selector}")
                                logger.info(f"  Text: '{element_text}'")
                                
                                # Scrolle zum Element
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(0.5)
                                
                                # Klicke auf Button
                                try:
                                    element.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", element)
                                
                                button_clicked = True
                                logger.info("✓ Speichern-Button geklickt!")
                                time.sleep(3)
                                break
                        except Exception as e:
                            continue
                    
                    if button_clicked:
                        break
                        
                except Exception as e:
                    continue
            
            if button_clicked:
                logger.info("✓ Download gestartet, warte auf Datei...")
                time.sleep(10)
            else:
                logger.warning("⚠️ Speichern-Button nicht gefunden")
                self._save_debug_screenshot("no_save_button_found")
                time.sleep(5)
            
            # Suche neueste CSV-Datei
            new_files = set(self.download_dir.glob("*.csv")) - existing_files
            
            if new_files:
                newest_file = max(new_files, key=lambda p: p.stat().st_mtime)
                logger.info(f"✓ Neue CSV heruntergeladen: {newest_file.name}")
                return str(newest_file)
            else:
                # Prüfe ob es neue Dateien gibt (auch wenn sie vorher schon da waren)
                all_files = list(self.download_dir.glob("*.csv"))
                if all_files:
                    newest_file = max(all_files, key=lambda p: p.stat().st_mtime)
                    # Prüfe ob Datei in den letzten 5 Minuten geändert wurde
                    if time.time() - newest_file.stat().st_mtime < 300:
                        logger.info(f"✓ CSV-Datei gefunden: {newest_file.name}")
                        return str(newest_file)
                
                # Warte noch etwas länger und versuche nochmal
                logger.info("Warte weitere 10 Sekunden auf Download...")
                time.sleep(10)
                
                # Nochmal prüfen
                new_files = set(self.download_dir.glob("*.csv")) - existing_files
                if new_files:
                    newest_file = max(new_files, key=lambda p: p.stat().st_mtime)
                    logger.info(f"✓ Neue CSV heruntergeladen: {newest_file.name}")
                    return str(newest_file)
                
                logger.error("✗ Keine neue CSV-Datei gefunden")
                logger.info("Mögliche Gründe:")
                logger.info("  - Download-Button nicht gefunden")
                logger.info("  - Keine Daten für den gewählten Zeitraum")
                logger.info("  - Portal-Struktur hat sich geändert")
                logger.info("Überprüfe den downloads/ Ordner und das debug-Screenshot")
                return None
                
        except Exception as e:
            logger.error(f"Fehler beim Download: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def close(self):
        """Schließt den Browser"""
        if self.driver:
            logger.info("Schließe Browser...")
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Hauptfunktion"""
    USERNAME = "deine.email@example.com"
    PASSWORD = "dein_passwort"
    
    with SmartMeterSeleniumDownloader(USERNAME, PASSWORD, headless=False) as downloader:
        if downloader.login():
            csv_file = downloader.download_csv(days_back=7)
            if csv_file:
                print(f"\n✓ Erfolgreich! Datei: {csv_file}")
            else:
                print("\n✗ Download fehlgeschlagen")
        else:
            print("\n✗ Login fehlgeschlagen")


if __name__ == "__main__":
    main()
