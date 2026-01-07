"""Smart Meter Burgenland API Client."""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Importiere den bestehenden Selenium Downloader
# Füge den Parent-Ordner zum Path hinzu
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from smartmeter_selenium import SmartMeterSeleniumDownloader

_LOGGER = logging.getLogger(__name__)


class SmartMeterClient:
    """Client to communicate with Smart Meter Burgenland Portal."""

    def __init__(
        self,
        username: str,
        password: str,
        headless: bool = True,
        price_per_kwh: float = 0.15
    ) -> None:
        """Initialize the client."""
        self.username = username
        self.password = password
        self.headless = headless
        self.price_per_kwh = price_per_kwh
        self._downloader = None

    def _get_downloader(self):
        """Get or create downloader instance."""
        if self._downloader is None:
            self._downloader = SmartMeterSeleniumDownloader(
                self.username,
                self.password,
                headless=self.headless
            )
        return self._downloader

    def test_connection(self) -> bool:
        """Test if we can authenticate with the host."""
        try:
            downloader = self._get_downloader()
            result = downloader.login()
            downloader.close()
            self._downloader = None
            return result
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False

    def close(self):
        """Close the connection."""
        if self._downloader:
            try:
                self._downloader.close()
            except:
                pass
            self._downloader = None

    def get_consumption_data(self) -> dict:
        """Download and parse consumption data from Smart Meter Portal."""
        try:
            downloader = self._get_downloader()
            
            # Login
            if not downloader.login():
                raise Exception("Login failed")
            
            # Download CSV
            csv_path = downloader.download_csv(days_back=30)
            
            # Close browser
            downloader.close()
            self._downloader = None
            
            if not csv_path or not os.path.exists(csv_path):
                raise Exception("CSV download failed")
            
            # Parse CSV
            return self._parse_csv(csv_path)
            
        except Exception as err:
            _LOGGER.error("Error getting consumption data: %s", err)
            self.close()
            raise

    def _parse_csv(self, csv_path: str) -> dict:
        """Parse CSV file and extract consumption data."""
        try:
            # Lese CSV mit verschiedenen Encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding, sep=None, engine='python')
                    break
                except:
                    continue
            
            _LOGGER.debug(f"CSV Spalten: {df.columns.tolist()}")
            _LOGGER.debug(f"CSV Shape: {df.shape}")
            
            # Finde Datums- und Verbrauchsspalten
            date_col = None
            consumption_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if 'datum' in col_lower or 'date' in col_lower or 'zeit' in col_lower:
                    date_col = col
                if 'verbrauch' in col_lower or 'consumption' in col_lower or 'kwh' in col_lower or 'wert' in col_lower:
                    consumption_col = col
            
            if not date_col or not consumption_col:
                _LOGGER.error(f"Konnte Spalten nicht finden. Verfügbar: {df.columns.tolist()}")
                # Fallback: Nimm erste Spalte als Datum, zweite als Verbrauch
                if len(df.columns) >= 2:
                    date_col = df.columns[0]
                    consumption_col = df.columns[1]
                else:
                    raise Exception("CSV Format nicht erkannt")
            
            _LOGGER.info(f"Verwende Datumsspalte: {date_col}, Verbrauchsspalte: {consumption_col}")
            
            # Konvertiere zu datetime
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            
            # Konvertiere Verbrauch zu numeric
            df[consumption_col] = pd.to_numeric(df[consumption_col], errors='coerce')
            df = df.dropna(subset=[consumption_col])
            
            # Sortiere nach Datum
            df = df.sort_values(date_col)
            
            # Berechne Statistiken
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Heute
            today_data = df[df[date_col].dt.date == today]
            consumption_today = float(today_data[consumption_col].sum()) if not today_data.empty else 0.0
            
            # Gestern
            yesterday_data = df[df[date_col].dt.date == yesterday]
            consumption_yesterday = float(yesterday_data[consumption_col].sum()) if not yesterday_data.empty else 0.0
            
            # Dieser Monat
            this_month_data = df[df[date_col].dt.to_period('M') == pd.Period(today, freq='M')]
            consumption_month = float(this_month_data[consumption_col].sum()) if not this_month_data.empty else 0.0
            
            # Letzter Monat
            last_month = today.replace(day=1) - timedelta(days=1)
            last_month_data = df[df[date_col].dt.to_period('M') == pd.Period(last_month, freq='M')]
            consumption_last_month = float(last_month_data[consumption_col].sum()) if not last_month_data.empty else 0.0
            
            # Durchschnitt pro Tag (letzten 30 Tage)
            days_30_ago = today - timedelta(days=30)
            recent_data = df[df[date_col].dt.date >= days_30_ago]
            avg_daily = float(recent_data[consumption_col].mean()) if not recent_data.empty else 0.0
            
            # Letzter Messwert
            last_reading = float(df[consumption_col].iloc[-1]) if not df.empty else 0.0
            last_reading_time = df[date_col].iloc[-1].isoformat() if not df.empty else None
            
            return {
                "consumption_today": round(consumption_today, 2),
                "consumption_yesterday": round(consumption_yesterday, 2),
                "consumption_month": round(consumption_month, 2),
                "consumption_last_month": round(consumption_last_month, 2),
                "avg_daily": round(avg_daily, 2),
                "cost_today": round(consumption_today * self.price_per_kwh, 2),
                "cost_yesterday": round(consumption_yesterday * self.price_per_kwh, 2),
                "cost_month": round(consumption_month * self.price_per_kwh, 2),
                "cost_last_month": round(consumption_last_month * self.price_per_kwh, 2),
                "last_reading": round(last_reading, 2),
                "last_reading_time": last_reading_time,
                "price_per_kwh": self.price_per_kwh
            }
            
        except Exception as err:
            _LOGGER.error(f"Error parsing CSV: {err}")
            raise
