# Smart Meter Burgenland - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant Custom Integration für Smart Meter der Netz Burgenland.

## 🎯 Features

Diese Integration liest automatisch deine Verbrauchsdaten vom Smart Meter Portal der Netz Burgenland aus und stellt sie als Sensoren in Home Assistant zur Verfügung.

### Verfügbare Sensoren

- **Verbrauch Heute** - Stromverbrauch des aktuellen Tages (kWh)
- **Verbrauch Gestern** - Stromverbrauch des gestrigen Tages (kWh)
- **Verbrauch Dieser Monat** - Gesamtverbrauch des aktuellen Monats (kWh)
- **Verbrauch Letzter Monat** - Gesamtverbrauch des letzten Monats (kWh)
- **Durchschnitt pro Tag** - Durchschnittlicher Tagesverbrauch der letzten 30 Tage (kWh)
- **Kosten Heute** - Kosten des aktuellen Tages (€)
- **Kosten Gestern** - Kosten des gestrigen Tages (€)
- **Kosten Dieser Monat** - Kosten des aktuellen Monats (€)
- **Kosten Letzter Monat** - Kosten des letzten Monats (€)
- **Letzter Messwert** - Letzter erfasster Verbrauchswert (kWh)

## 📋 Voraussetzungen

- Home Assistant 2023.1 oder höher
- Zugang zum Smart Meter Portal (smartmeter.netzburgenland.at)
- ChromeDriver muss auf dem Home Assistant Host installiert sein

### ChromeDriver Installation

**Auf Home Assistant OS / Supervised:**
```bash
# SSH in Home Assistant
# Installiere ChromeDriver im Container
docker exec -it homeassistant bash
apt-get update
apt-get install -y chromium-driver chromium
```

**Auf Docker:**
```yaml
# In deiner docker-compose.yml
services:
  homeassistant:
    image: homeassistant/home-assistant:latest
    volumes:
      - ./config:/config
    devices:
      - /dev/dri:/dev/dri  # Optional: Hardware-Beschleunigung
    environment:
      - CHROME_BIN=/usr/bin/chromium
```

**Auf Linux (manuell):**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Fedora/RHEL
sudo dnf install chromium-chromedriver
```

## 🚀 Installation

### Methode 1: HACS (empfohlen)

1. Öffne HACS in Home Assistant
2. Klicke auf "Integrationen"
3. Klicke auf die drei Punkte oben rechts
4. Wähle "Benutzerdefinierte Repositories"
5. Füge die URL hinzu: `https://github.com/klauskirnbauerHTL/SmartMeter_Bgld`
6. Kategorie: "Integration"
7. Klicke auf "Hinzufügen"
8. Suche nach "Smart Meter Burgenland"
9. Klicke auf "Installieren"
10. Starte Home Assistant neu

### Methode 2: Manuelle Installation

1. Kopiere den Ordner `custom_components/smartmeter_burgenland` in dein Home Assistant `config/custom_components/` Verzeichnis:

```bash
# Auf deinem Home Assistant Server
cd /config
mkdir -p custom_components
cd custom_components
git clone https://github.com/klauskirnbauerHTL/SmartMeter_Bgld.git
cp -r SmartMeter_Bgld/custom_components/smartmeter_burgenland .
```

2. Kopiere auch die `smartmeter_selenium.py` in das `/config` Verzeichnis:

```bash
cp SmartMeter_Bgld/smartmeter_selenium.py /config/
```

3. Starte Home Assistant neu

## ⚙️ Konfiguration

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **Integration hinzufügen**
3. Suche nach **Smart Meter Burgenland**
4. Gebe deine Anmeldedaten ein:
   - **Benutzername**: Deine E-Mail-Adresse für das Smart Meter Portal
   - **Passwort**: Dein Passwort
   - **Strompreis pro kWh**: Dein aktueller Strompreis (Standard: 0.15 €)
   - **Headless Modus**: Aktiviert (Browser läuft im Hintergrund)
5. Klicke auf **Absenden**

Die Integration verbindet sich nun mit dem Portal und testet die Anmeldung. Nach erfolgreicher Konfiguration werden alle Sensoren automatisch angelegt.

## 📊 Verwendung in Lovelace

### Beispiel: Energie-Karte

```yaml
type: entities
title: Stromverbrauch
entities:
  - entity: sensor.smart_meter_verbrauch_heute
    name: Heute
  - entity: sensor.smart_meter_verbrauch_gestern
    name: Gestern
  - entity: sensor.smart_meter_verbrauch_dieser_monat
    name: Dieser Monat
  - entity: sensor.smart_meter_kosten_dieser_monat
    name: Kosten Monat
```

### Beispiel: Statistik-Karte

```yaml
type: statistics-graph
title: Verbrauch letzte 7 Tage
entities:
  - sensor.smart_meter_verbrauch_heute
stat_types:
  - mean
  - max
  - min
period: day
days_to_show: 7
```

### Beispiel: Energie-Dashboard Integration

Füge die Sensoren zum Energie-Dashboard hinzu:

1. Gehe zu **Einstellungen** → **Dashboards** → **Energie**
2. Klicke auf **Stromverbrauch hinzufügen**
3. Wähle `sensor.smart_meter_verbrauch_heute`
4. Fertig! 🎉

## 🔄 Update-Intervall

Die Integration aktualisiert die Daten standardmäßig **stündlich**. Du kannst das Intervall anpassen:

```yaml
# configuration.yaml
smartmeter_burgenland:
  scan_interval: 3600  # Sekunden (Standard: 1 Stunde)
```

## 🐛 Fehlerbehebung

### "Verbindung fehlgeschlagen"

1. Prüfe deine Anmeldedaten auf dem Portal: https://smartmeter.netzburgenland.at
2. Stelle sicher, dass ChromeDriver installiert ist
3. Aktiviere Debug-Logging:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.smartmeter_burgenland: debug
```

### "CSV Download fehlgeschlagen"

- Prüfe ob genug Speicherplatz vorhanden ist
- Schaue in die Logs: **Einstellungen** → **System** → **Protokolle**
- Screenshots werden im `downloads/` Ordner gespeichert

### Browser startet nicht im Headless-Modus

Deaktiviere den Headless-Modus in der Integration-Konfiguration und prüfe, ob der Browser manuell startet.

## 🔧 Erweiterte Konfiguration

### Python-Umgebung

Die Integration nutzt die bestehende `smartmeter_selenium.py`. Stelle sicher, dass alle Dependencies installiert sind:

```bash
pip install selenium pandas
```

### Eigenes Download-Verzeichnis

Standardmäßig werden CSVs in `config/downloads/` gespeichert. Du kannst das ändern, indem du `smartmeter_selenium.py` bearbeitest.

## 📝 Lizenz

MIT License - siehe LICENSE Datei

## 🤝 Beiträge

Contributions sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## 📧 Support

Bei Problemen erstelle bitte ein Issue auf GitHub: https://github.com/klauskirnbauerHTL/SmartMeter_Bgld/issues

---

Entwickelt mit ❤️ für die Smart Meter Community in Burgenland
