# Smart Meter Netz Burgenland - Downloader mit GUI

Automatischer Download und Auswertung von Stromverbrauchsdaten vom Smart Meter Portal der Netz Burgenland mit grafischer Benutzeroberfläche.

## 🎯 Features

- ✅ **Grafische Benutzeroberfläche** (PyQt6) für einfache Bedienung
- ✅ Automatischer Login auf smartmeter.netzburgenland.at
- ✅ Download von Verbrauchsdaten als CSV
- ✅ Unterstützung verschiedener Zeitauflösungen (15min, stündlich, täglich, monatlich)
- ✅ Automatische Datenauswertung mit Statistiken
- ✅ Periodischer automatischer Download
- ✅ Kostenschätzung basierend auf Verbrauch
- ✅ Export der Analyseergebnisse als JSON
- ✅ Live-Log während des Downloads

## 📋 Voraussetzungen

- Python 3.8 oder höher
- Zugang zum Smart Meter Portal (smartmeter.netzburgenland.at)
- Internetverbindung

## 🚀 Schnellstart

### 1. Abhängigkeiten installieren

```bash
# Virtual Environment aktivieren (falls vorhanden)
source .venv/bin/activate

# Pakete installieren
pip install -r requirements.txt
```

### 2. GUI starten

```bash
python smartmeter_gui.py
```

## 📖 Verwendung

### GUI-Anwendung (empfohlen)

1. **Starte die GUI:**
   ```bash
   python smartmeter_gui.py
   ```

2. **Einstellungen konfigurieren:**
   - Gehe zum Tab "⚙️ Einstellungen"
   - Trage deine Login-Daten ein (E-Mail & Passwort)
   - Wähle Zeitraum, Auflösung und Strompreis
   - Optional: Aktiviere periodischen Download
   - Klicke auf "💾 Einstellungen speichern"

3. **Verbindung testen:**
   - Klicke auf "🔍 Verbindung testen"
   - Überprüfe ob Login erfolgreich ist

4. **Daten herunterladen:**
   - Gehe zum Tab "📥 Download"
   - Klicke auf "📥 Download jetzt starten"
   - Verfolge den Fortschritt im Log

5. **Ergebnisse ansehen:**
   - Klicke auf "📁 Downloads-Ordner öffnen"
   - CSV- und JSON-Dateien befinden sich im `downloads/` Verzeichnis

### Kommandozeile (CLI)

Alternativ kannst du auch die Kommandozeilen-Version verwenden:

```bash
python smartmeter_downloader.py
```

Bearbeite vorher die Einstellungen in der `main()` Funktion oder erstelle eine `config.py`.

## ⚙️ Konfiguration

### GUI

Alle Einstellungen werden automatisch in `config.json` gespeichert.

### Verfügbare Optionen

- **Benutzername:** Deine E-Mail oder Kundennummer für das Smart Meter Portal
- **Passwort:** Dein Passwort
- **Zeitraum:** Anzahl Tage zurück (1-365)
- **Datenauflösung:**
  - `15min` - 15-Minuten-Werte (sehr detailliert)
  - `hourly` - Stündliche Werte
  - `daily` - Tägliche Werte
  - `monthly` - Monatliche Werte
- **Strompreis:** Für Kostenschätzung (€/kWh)
- **Periodischer Download:** Automatischer Download in festgelegten Intervallen

## 📁 Projektstruktur

```
SmartMeter_Bgld/
├── smartmeter_gui.py           # GUI-Anwendung (PyQt6)
├── smartmeter_downloader.py    # Download-Engine
├── requirements.txt            # Python-Abhängigkeiten
├── config.json                 # Gespeicherte Einstellungen (wird automatisch erstellt)
├── .gitignore                  # Git-Ausschlüsse
├── downloads/                  # Heruntergeladene Dateien (wird automatisch erstellt)
│   ├── smartmeter_*.csv       # CSV-Rohdaten
│   └── smartmeter_*_analysis.json  # Analyseergebnisse
└── .venv/                      # Python Virtual Environment
```

## 📊 Ausgabeformate

### CSV-Datei

Enthält die Rohdaten vom Smart Meter Portal:
- Datum/Zeit
- Verbrauch (kWh)
- Weitere Messwerte

### JSON-Datei

Analyseergebnisse im JSON-Format:
```json
{
  "Verbrauch": {
    "total": 45.67,
    "average": 2.34,
    "max": 5.12,
    "min": 0.45
  },
  "period": {
    "start": "2026-01-01",
    "end": "2026-01-07"
  },
  "estimated_cost": 13.70
}
```

## 🖼️ Screenshots

### Einstellungen-Tab
- Eingabe von Login-Daten
- Konfiguration von Download-Parametern
- Test der Verbindung

### Download-Tab
- Start des Downloads
- Live-Log-Ausgabe
- Zugriff auf Downloads-Ordner

## 🛠️ Troubleshooting

### GUI startet nicht

```bash
# Prüfe ob PyQt6 installiert ist
pip install PyQt6

# Oder installiere alle Abhängigkeiten neu
pip install -r requirements.txt
```

### Login funktioniert nicht

1. Überprüfe deine Zugangsdaten im Browser: [smartmeter.netzburgenland.at](https://smartmeter.netzburgenland.at)
2. Stelle sicher, dass du die E-Mail-Adresse korrekt eingegeben hast
3. Prüfe ob das Portal erreichbar ist
4. Verwende den "Verbindung testen" Button in der GUI

### Keine Daten verfügbar

- Smart Meter Daten sind oft mit 1-2 Tagen Verzögerung verfügbar
- Versuche einen älteren Zeitraum (z.B. letzte Woche statt gestern)

### Import-Fehler

```bash
# Stelle sicher, dass alle Dateien vorhanden sind:
ls -la
# Du solltest sehen: smartmeter_gui.py, smartmeter_downloader.py

# Installiere fehlende Pakete:
pip install -r requirements.txt
```

## 🔐 Sicherheit

⚠️ **WICHTIG - Zugangsdaten schützen:**

1. `config.json` wird lokal gespeichert und enthält dein Passwort im Klartext
2. Die Datei ist in `.gitignore` enthalten (wird nicht in Git committed)
3. Schütze deinen Computer mit einem Passwort
4. Teile die `config.json` Datei mit niemandem

### Für Produktivumgebungen

Verwende Umgebungsvariablen statt gespeicherter Passwörter:

```bash
export SMARTMETER_USERNAME="deine.email@example.com"
export SMARTMETER_PASSWORD="dein_passwort"
```

## 🔄 Updates

Um die neueste Version zu erhalten:

```bash
git pull
pip install -r requirements.txt --upgrade
```

## 🤝 Support

Bei Fragen oder Problemen:

1. Überprüfe die [Netz Burgenland Website](https://smartmeter.netzburgenland.at)
2. Kontaktiere den Netz Burgenland Support
3. Prüfe die Logs in der GUI für Fehlermeldungen

## 📝 Hinweise

- Die Struktur der API kann sich ändern - das Skript muss ggf. angepasst werden
- Respektiere die Nutzungsbedingungen des Smart Meter Portals
- Verwende angemessene Download-Intervalle (nicht zu häufig)
- Daten sind meist mit 1-2 Tagen Verzögerung verfügbar
- Die GUI läuft im Hauptthread - während Downloads ist sie reaktionsfähig

## 📜 Lizenz

MIT License - Freie Verwendung für private und kommerzielle Zwecke

---

**© 2026 | Erstellt für HTL Pinkafeld**
