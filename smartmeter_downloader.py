"""
Smart Meter Netz Burgenland CSV Downloader
Lädt periodisch Verbrauchsdaten vom Smart Meter Portal herunter und wertet sie aus.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
import json

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartMeterDownloader:
    """Klasse zum Herunterladen und Auswerten von Smart Meter Daten von Netz Burgenland"""
    
    def __init__(self, username, password):
        """
        Initialisiert den Downloader
        
        Args:
            username: Benutzername (E-Mail oder Kundennummer)
            password: Passwort
        """
        self.base_url = "https://smartmeter.netzburgenland.at"
        self.portal_url = "https://smartmeter.netzburgenland.at/enview/enView.Portal"
        self.api_url = "https://smartmeter.netzburgenland.at/enview/enView.Portal/api"
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Referer': 'https://smartmeter.netzburgenland.at/enview/enView.Portal/',
            'Origin': 'https://smartmeter.netzburgenland.at'
        })
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        self.logged_in = False
        
    def login(self):
        """
        Meldet sich auf dem Smart Meter Portal an
        
        Returns:
            bool: True wenn Login erfolgreich, sonst False
        """
        try:
            logger.info("Verbinde mit Smart Meter Portal...")
            logger.info(f"Versuche Login für Benutzer: {self.username}")
            
            # Erst Portal-Seite laden um Cookies/Session zu bekommen
            logger.info("Lade Portal-Seite...")
            try:
                init_response = self.session.get(f"{self.portal_url}/", timeout=30)
                logger.info(f"  Portal geladen: {init_response.status_code}")
            except Exception as e:
                logger.warning(f"  Portal-Seite nicht erreichbar: {e}")
            
            # Verschiedene Login-Methoden ausprobieren (enView Portal spezifisch)
            login_attempts = [
                # Versuch 1: enView.Portal Authentication API
                {
                    'url': f"{self.portal_url}/api/Authentication",
                    'method': 'json',
                    'data': {
                        'userName': self.username,
                        'password': self.password
                    }
                },
                # Versuch 2: Alternative Feldnamen
                {
                    'url': f"{self.portal_url}/api/Authentication",
                    'method': 'json',
                    'data': {
                        'username': self.username,
                        'password': self.password
                    }
                },
                # Versuch 3: Login-Endpunkt
                {
                    'url': f"{self.portal_url}/api/Login",
                    'method': 'json',
                    'data': {
                        'userName': self.username,
                        'password': self.password
                    }
                },
                # Versuch 4: Auth-Endpunkt mit email
                {
                    'url': f"{self.portal_url}/api/Authentication",
                    'method': 'json',
                    'data': {
                        'email': self.username,
                        'password': self.password
                    }
                },
                # Versuch 5: User/Authenticate
                {
                    'url': f"{self.portal_url}/api/User/Authenticate",
                    'method': 'json',
                    'data': {
                        'userName': self.username,
                        'password': self.password
                    }
                },
                # Versuch 6: Account/Login
                {
                    'url': f"{self.portal_url}/api/Account/Login",
                    'method': 'json',
                    'data': {
                        'userName': self.username,
                        'password': self.password
                    }
                },
                # Versuch 7: Form-basiert
                {
                    'url': f"{self.portal_url}/api/Authentication",
                    'method': 'form',
                    'data': {
                        'userName': self.username,
                        'password': self.password
                    }
                }
            ]
            
            for i, attempt in enumerate(login_attempts, 1):
                try:
                    logger.info(f"Login-Versuch {i}/{len(login_attempts)}: {attempt['url']}")
                    
                    if attempt['method'] == 'json':
                        response = self.session.post(
                            attempt['url'],
                            json=attempt['data'],
                            timeout=30,
                            allow_redirects=True
                        )
                    else:
                        response = self.session.post(
                            attempt['url'],
                            data=attempt['data'],
                            timeout=30,
                            allow_redirects=True
                        )
                    
                    logger.info(f"  Status: {response.status_code}")
                    
                    # Erfolgreiche Antworten prüfen
                    if response.status_code in [200, 201, 302]:
                        # Prüfe auf Token/Session in Cookies
                        if self.session.cookies:
                            logger.info(f"  Cookies erhalten: {len(self.session.cookies)} Cookie(s)")
                        
                        # Prüfe JSON Response
                        try:
                            result = response.json()
                            logger.info(f"  JSON Response Keys: {list(result.keys())}")
                            
                            # Verschiedene Erfolgs-Indikatoren
                            if (result.get('success') or 
                                result.get('authenticated') or
                                'token' in result or 
                                'sessionId' in result or
                                'access_token' in result or
                                result.get('status') == 'success'):
                                
                                logger.info("✓ Login erfolgreich (JSON-Bestätigung)")
                                self.logged_in = True
                                
                                # Speichere Token/Session-ID
                                for key in ['token', 'access_token', 'authToken', 'sessionId']:
                                    if key in result:
                                        self.session.headers.update({
                                            'Authorization': f"Bearer {result[key]}",
                                            'X-Auth-Token': result[key]
                                        })
                                        logger.info(f"  Token gespeichert: {key}")
                                        break
                                
                                return True
                        except:
                            # Kein JSON oder nicht parsebar
                            pass
                        
                        # Prüfe ob Redirect zu Dashboard erfolgt (Zeichen für erfolgreichen Login)
                        if response.history:
                            logger.info(f"  Redirects: {[r.status_code for r in response.history]}")
                        
                        # Prüfe HTML-Inhalt auf Erfolgs-Indikatoren
                        if 'dashboard' in response.text.lower() or 'logout' in response.text.lower():
                            logger.info("✓ Login erfolgreich (Dashboard/Logout gefunden)")
                            self.logged_in = True
                            return True
                        
                        # Wenn Cookies gesetzt wurden, könnte Login erfolgreich sein
                        if len(self.session.cookies) > 0 and response.status_code == 200:
                            logger.info("✓ Login wahrscheinlich erfolgreich (Cookies erhalten)")
                            self.logged_in = True
                            return True
                    
                    logger.info(f"  Versuch {i} nicht erfolgreich")
                    
                except Exception as e:
                    logger.info(f"  Versuch {i} fehlgeschlagen: {str(e)[:100]}")
                    continue
            
            logger.error("✗ Alle Login-Versuche fehlgeschlagen")
            logger.error("Bitte überprüfe:")
            logger.error("  1. Sind die Zugangsdaten korrekt?")
            logger.error("  2. Funktioniert der Login im Browser?")
            logger.error("  3. Verwendet das Portal evtl. Captcha oder 2FA?")
            return False
                
        except Exception as e:
            logger.error(f"Fehler beim Login: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def download_csv(self, start_date=None, end_date=None, data_type='15min'):
        """
        Lädt die CSV-Datei mit Verbrauchsdaten herunter
        
        Args:
            start_date: Startdatum (datetime) - Standard: gestern
            end_date: Enddatum (datetime) - Standard: heute
            data_type: Datentyp ('15min', 'hourly', 'daily', 'monthly')
        
        Returns:
            str: Pfad zur heruntergeladenen Datei oder None bei Fehler
        """
        if not self.logged_in:
            logger.warning("Nicht angemeldet - führe Login durch...")
            if not self.login():
                return None
        
        try:
            # Standardwerte für Datum setzen
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=7)  # Letzte 7 Tage
            
            # Parameter für den CSV-Export (verschiedene Varianten)
            param_variants = [
                # Variante 1: ISO-Format mit from/to
                {
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'resolution': data_type,
                    'format': 'csv'
                },
                # Variante 2: startDate/endDate
                {
                    'startDate': start_date.strftime('%Y-%m-%d'),
                    'endDate': end_date.strftime('%Y-%m-%d'),
                    'resolution': data_type,
                    'format': 'csv'
                },
                # Variante 3: ISO-Format mit Zeitstempel
                {
                    'from': start_date.strftime('%Y-%m-%dT00:00:00'),
                    'to': end_date.strftime('%Y-%m-%dT23:59:59'),
                    'type': data_type
                },
                # Variante 4: Timestamps
                {
                    'fromTimestamp': int(start_date.timestamp() * 1000),
                    'toTimestamp': int(end_date.timestamp() * 1000),
                    'resolution': data_type
                }
            ]
            
            logger.info(f"Lade Daten von {start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')} ({data_type})...")
            
            # CSV herunterladen - verschiedene mögliche Endpunkte ausprobieren
            endpoints = [
                f"{self.portal_url}/api/MeteringData/Export",
                f"{self.portal_url}/api/Consumption/Export",
                f"{self.portal_url}/api/Data/Export",
                f"{self.portal_url}/api/ConsumptionData/Export",
                f"{self.portal_url}/api/MeterData/Export",
                f"{self.api_url}/consumption/export",
                f"{self.api_url}/meteringdata/export",
                f"{self.base_url}/api/consumption/export"
            ]
            
            response = None
            successful_endpoint = None
            
            for endpoint in endpoints:
                for params in param_variants:
                    try:
                        logger.info(f"Probiere: {endpoint}")
                        response = self.session.get(endpoint, params=params, timeout=30)
                        
                        # Prüfe ob Response aussieht wie CSV
                        if response.status_code == 200 and len(response.content) > 100:
                            # Prüfe Content-Type oder Inhalt
                            content_type = response.headers.get('Content-Type', '').lower()
                            if 'csv' in content_type or 'text' in content_type or response.content.startswith(b'Date') or response.content.startswith(b'Datum') or b',' in response.content[:100] or b';' in response.content[:100]:
                                successful_endpoint = endpoint
                                logger.info(f"  ✓ Erfolg! CSV erhalten")
                                break
                    except Exception as e:
                        logger.debug(f"  Fehler bei {endpoint}: {str(e)[:50]}")
                        continue
                
                if successful_endpoint:
                    break
            
            if response.status_code == 200:
                # Dateinamen mit Timestamp erstellen
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"smartmeter_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{timestamp}.csv"
                filepath = self.download_dir / filename
                
                # CSV speichern
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✓ CSV erfolgreich heruntergeladen: {filepath}")
                return str(filepath)
            else:
                logger.error(f"✗ Download fehlgeschlagen: Status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Fehler beim Download: {e}")
            return None
    
    def analyze_csv(self, filepath):
        """
        Wertet die CSV-Datei aus
        
        Args:
            filepath: Pfad zur CSV-Datei
            
        Returns:
            dict: Analyseergebnisse
        """
        try:
            # CSV einlesen - Smart Meter CSV hat oft Semikolon als Trennzeichen
            try:
                df = pd.read_csv(filepath, sep=';', decimal=',')
            except:
                df = pd.read_csv(filepath)
            
            logger.info("\n" + "="*70)
            logger.info("SMART METER DATENAUSWERTUNG")
            logger.info("="*70)
            
            # Grundlegende Informationen
            logger.info(f"\n📊 Anzahl Datensätze: {len(df)}")
            logger.info(f"📋 Spalten: {', '.join(df.columns.tolist())}")
            
            # Erste Zeilen anzeigen
            logger.info("\n📝 Erste 5 Einträge:")
            logger.info("\n" + df.head().to_string())
            
            results = {}
            
            # Verbrauchsanalyse (typische Spaltennamen für Smart Meter Daten)
            consumption_cols = [col for col in df.columns if 'verbrauch' in col.lower() or 'consumption' in col.lower() or 'wert' in col.lower()]
            
            if consumption_cols:
                for col in consumption_cols:
                    try:
                        # Konvertiere zu numerischen Werten
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
                        
                        total = df[col].sum()
                        avg = df[col].mean()
                        max_val = df[col].max()
                        min_val = df[col].min()
                        
                        logger.info(f"\n⚡ {col}:")
                        logger.info(f"  • Gesamt: {total:.2f} kWh")
                        logger.info(f"  • Durchschnitt: {avg:.2f} kWh")
                        logger.info(f"  • Maximum: {max_val:.2f} kWh")
                        logger.info(f"  • Minimum: {min_val:.2f} kWh")
                        
                        results[col] = {
                            'total': float(total),
                            'average': float(avg),
                            'max': float(max_val),
                            'min': float(min_val)
                        }
                        
                    except Exception as e:
                        logger.warning(f"Konnte Spalte {col} nicht analysieren: {e}")
            
            # Zeitanalyse
            date_cols = [col for col in df.columns if 'datum' in col.lower() or 'date' in col.lower() or 'zeit' in col.lower() or 'time' in col.lower()]
            
            if date_cols:
                date_col = date_cols[0]
                logger.info(f"\n📅 Zeitraum:")
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    logger.info(f"  • Von: {df[date_col].min()}")
                    logger.info(f"  • Bis: {df[date_col].max()}")
                    
                    results['period'] = {
                        'start': str(df[date_col].min()),
                        'end': str(df[date_col].max())
                    }
                except:
                    logger.info(f"  • Von: {df[date_col].iloc[0]}")
                    logger.info(f"  • Bis: {df[date_col].iloc[-1]}")
            
            # Fehlende Werte
            missing = df.isnull().sum()
            if missing.sum() > 0:
                logger.info("\n⚠️  Fehlende Werte:")
                for col, count in missing[missing > 0].items():
                    logger.info(f"  • {col}: {count}")
            
            # Kosten schätzen (ca. 0,30 €/kWh als Beispiel)
            if consumption_cols and results:
                price_per_kwh = 0.30
                first_col = consumption_cols[0]
                estimated_cost = results[first_col]['total'] * price_per_kwh
                logger.info(f"\n💰 Geschätzte Kosten (bei {price_per_kwh}€/kWh): {estimated_cost:.2f} €")
                results['estimated_cost'] = float(estimated_cost)
            
            logger.info("\n" + "="*70 + "\n")
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Auswertung: {e}")
            return {}
    
    def run_once(self, days_back=7, data_type='15min'):
        """
        Führt einen kompletten Download- und Auswertungszyklus durch
        
        Args:
            days_back: Anzahl der Tage zurück zum Herunterladen
            data_type: Datentyp ('15min', 'hourly', 'daily', 'monthly')
        """
        logger.info("\n" + "="*70)
        logger.info(f"🚀 Starte Download-Zyklus: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        logger.info("="*70)
        
        # Login
        if not self.logged_in:
            if not self.login():
                logger.error("Login fehlgeschlagen - Abbruch")
                return False
        
        # Datum berechnen
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # CSV herunterladen
        filepath = self.download_csv(start_date, end_date, data_type)
        if not filepath:
            logger.error("Download fehlgeschlagen - Abbruch")
            return False
        
        # CSV auswerten
        results = self.analyze_csv(filepath)
        
        # Ergebnisse auch als JSON speichern
        if results:
            json_path = filepath.replace('.csv', '_analysis.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Analyseergebnisse gespeichert: {json_path}")
        
        return True
    
    def run_periodic(self, interval_hours=24, days_back=7, data_type='15min'):
        """
        Führt den Download periodisch aus
        
        Args:
            interval_hours: Intervall in Stunden zwischen Downloads
            days_back: Anzahl der Tage zurück zum Herunterladen
            data_type: Datentyp ('15min', 'hourly', 'daily', 'monthly')
        """
        logger.info(f"🔄 Starte periodischen Download")
        logger.info(f"   • Intervall: alle {interval_hours} Stunden")
        logger.info(f"   • Zeitraum: letzte {days_back} Tage")
        logger.info(f"   • Auflösung: {data_type}")
        logger.info("   • Drücke Ctrl+C zum Beenden\n")
        
        try:
            while True:
                self.run_once(days_back=days_back, data_type=data_type)
                
                next_run = datetime.now() + timedelta(hours=interval_hours)
                logger.info(f"\n⏰ Nächster Download: {next_run.strftime('%d.%m.%Y %H:%M:%S')}")
                logger.info(f"   Warte {interval_hours} Stunden...\n")
                
                time.sleep(interval_hours * 3600)
                
        except KeyboardInterrupt:
            logger.info("\n\n👋 Programm wurde beendet")


def main():
    """Hauptfunktion"""
    
    # KONFIGURATION - HIER ANPASSEN!
    USERNAME = "deine.email@example.com"  # Oder Kundennummer
    PASSWORD = "dein_passwort"
    
    # Download-Einstellungen
    DAYS_BACK = 7  # Letzte 7 Tage
    DATA_TYPE = '15min'  # '15min', 'hourly', 'daily', 'monthly'
    INTERVAL_HOURS = 24  # Alle 24 Stunden
    
    # Downloader erstellen
    downloader = SmartMeterDownloader(
        username=USERNAME,
        password=PASSWORD
    )
    
    # Einmaliger Download (zum Testen)
    downloader.run_once(days_back=DAYS_BACK, data_type=DATA_TYPE)
    
    # Oder: Periodischer Download (auskommentieren zum Aktivieren)
    # downloader.run_periodic(
    #     interval_hours=INTERVAL_HOURS,
    #     days_back=DAYS_BACK,
    #     data_type=DATA_TYPE
    # )


if __name__ == "__main__":
    main()
