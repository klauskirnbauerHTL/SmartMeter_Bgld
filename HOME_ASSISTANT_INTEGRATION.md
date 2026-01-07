# Smart Meter Burgenland - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/klauskirnbauerHTL/SmartMeter_Bgld.svg)](https://github.com/klauskirnbauerHTL/SmartMeter_Bgld/releases)
[![License](https://img.shields.io/github/license/klauskirnbauerHTL/SmartMeter_Bgld.svg)](LICENSE)

Home Assistant Integration für Smart Meter der Netz Burgenland GmbH. Automatischer Abruf und Visualisierung deiner Stromverbrauchsdaten direkt in Home Assistant.

## 📋 Übersicht

Diese Integration ermöglicht es dir, deine Smart Meter Daten von [smartmeter.netzburgenland.at](https://smartmeter.netzburgenland.at) direkt in Home Assistant zu integrieren.

### Features

- 📊 **Automatischer Datenabruf** - Regelmäßige Updates deiner Verbrauchsdaten
- 🔄 **Verschiedene Auflösungen** - 15-Minuten, Stündlich, Täglich oder Monatlich
- 💰 **Kostenberechnung** - Automatische Berechnung der Stromkosten
- 📈 **Home Assistant Statistiken** - Vollständige Integration in HA Statistiken und Energy Dashboard
- 🎯 **Einfache Konfiguration** - Einrichtung über die Home Assistant UI

## 🚀 Installation

### HACS (empfohlen)

1. Stelle sicher, dass [HACS](https://hacs.xyz/) installiert ist
2. Öffne HACS → Integrationen
3. Klicke auf die drei Punkte (⋮) oben rechts
4. Wähle "Benutzerdefinierte Repositories"
5. Füge folgende URL hinzu: `https://github.com/klauskirnbauerHTL/SmartMeter_Bgld`
6. Wähle als Kategorie: "Integration"
7. Klicke auf "HINZUFÜGEN"
8. Suche nach "Smart Meter Burgenland" in HACS
9. Klicke auf "HERUNTERLADEN"
10. **Starte Home Assistant neu**

### Manuelle Installation

1. Lade die neueste Version von [GitHub Releases](https://github.com/klauskirnbauerHTL/SmartMeter_Bgld/releases) herunter
2. Entpacke das Archiv
3. Kopiere den Ordner `custom_components/smartmeter_burgenland` in dein Home Assistant `config/custom_components/` Verzeichnis
4. **Starte Home Assistant neu**

## ⚙️ Konfiguration

### Einrichtung über die UI

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **+ INTEGRATION HINZUFÜGEN**
3. Suche nach **"Smart Meter Burgenland"**
4. Gib deine Zugangsdaten ein:
   - **E-Mail/Benutzername**: Dein Login für das Smart Meter Portal
   - **Passwort**: Dein Passwort
   - **Zeitraum (Tage)**: Wie viele Tage zurück Daten abgerufen werden sollen (1-365)
   - **Auflösung**: Wähle zwischen:
     - `15min` - 15-Minuten-Werte (sehr detailliert)
     - `hourly` - Stündliche Werte
     - `daily` - Tägliche Werte
     - `monthly` - Monatliche Werte
   - **Strompreis (€/kWh)**: Dein aktueller Strompreis für die Kostenberechnung

5. Klicke auf **SENDEN**

Die Integration wird nun eingerichtet und beginnt automatisch mit dem Abruf der Daten.

## 📊 Sensoren

Nach der Einrichtung werden folgende Sensoren erstellt:

### Hauptsensoren

| Sensor | Beschreibung | Einheit |
|--------|-------------|---------|
| `sensor.smartmeter_current_consumption` | Neuester Verbrauchswert | kWh |
| `sensor.smartmeter_daily_consumption` | Verbrauch des aktuellen Tages | kWh |
| `sensor.smartmeter_average_consumption` | Durchschnittsverbrauch | kWh |
| `sensor.smartmeter_estimated_cost` | Geschätzte Kosten (Zeitraum) | € |

### Attribute

Jeder Sensor enthält zusätzliche Attribute wie:
- Zeitstempel der letzten Aktualisierung
- Minimum/Maximum Werte
- Trend-Informationen

## 🔧 Verwendung im Energy Dashboard

1. Gehe zu **Einstellungen** → **Dashboards** → **Energie**
2. Unter **Stromnetzbezug** klicke auf **Verbrauch hinzufügen**
3. Wähle `sensor.smartmeter_current_consumption`
4. Konfiguriere optional Kosten mit `sensor.smartmeter_estimated_cost`

## 🔄 Update-Intervall

- Die Daten werden standardmäßig alle **2 Stunden** aktualisiert
- Dies kann in der Integration angepasst werden

## 📝 Beispiel-Automatisierung

```yaml
automation:
  - alias: "Benachrichtigung bei hohem Verbrauch"
    trigger:
      - platform: numeric_state
        entity_id: sensor.smartmeter_current_consumption
        above: 5.0  # kWh
    action:
      - service: notify.notify
        data:
          title: "Hoher Stromverbrauch!"
          message: "Aktueller Verbrauch: {{ states('sensor.smartmeter_current_consumption') }} kWh"
```

## 🐛 Problembehandlung

### Integration erscheint nicht

- Stelle sicher, dass Home Assistant neu gestartet wurde
- Überprüfe die Logs: **Einstellungen** → **System** → **Logs**

### Login schlägt fehl

- Überprüfe deine Zugangsdaten
- Teste den Login auf [smartmeter.netzburgenland.at](https://smartmeter.netzburgenland.at)
- Stelle sicher, dass dein Account Zugriff auf Smart Meter Daten hat

### Keine Daten werden abgerufen

- Überprüfe die Logs auf Fehlermeldungen
- Stelle sicher, dass Selenium richtig installiert ist
- Versuche, den Zeitraum zu verkürzen

### Debug-Modus aktivieren

Füge folgendes zu deiner `configuration.yaml` hinzu:

```yaml
logger:
  default: info
  logs:
    custom_components.smartmeter_burgenland: debug
```

## 📚 Weitere Informationen

- **GitHub Repository**: [SmartMeter_Bgld](https://github.com/klauskirnbauerHTL/SmartMeter_Bgld)
- **Issue Tracker**: [Issues](https://github.com/klauskirnbauerHTL/SmartMeter_Bgld/issues)
- **GUI Standalone Version**: Siehe [README.md](README.md) für die Desktop-Anwendung

## 👨‍💻 Entwicklung

Dieses Projekt ist Open Source und Beiträge sind willkommen!

```bash
# Repository klonen
git clone https://github.com/klauskirnbauerHTL/SmartMeter_Bgld.git

# Abhängigkeiten installieren
pip install -r requirements.txt

# Tests ausführen
python test_selenium.py
```

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE)

## 🙏 Danksagungen

- [Home Assistant](https://www.home-assistant.io/)
- [Netz Burgenland](https://www.netzburgenland.at/)

---

**Hinweis**: Dies ist ein inoffizielles Projekt und steht in keiner Verbindung zur Netz Burgenland GmbH.
