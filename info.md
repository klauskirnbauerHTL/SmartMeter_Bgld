# Smart Meter Burgenland Integration

Diese Integration ermöglicht es, Verbrauchsdaten von deinem Smart Meter der Netz Burgenland direkt in Home Assistant zu integrieren.

## Features

- 📊 Automatischer Abruf von Stromverbrauchsdaten
- 🔄 Regelmäßige Updates (konfigurierbar)
- 📈 Verschiedene Auflösungen (15min, stündlich, täglich, monatlich)
- 💰 Kostenschätzung basierend auf deinem Strompreis
- 📉 Langzeit-Statistiken und Trends

## Installation

### HACS (empfohlen)

1. Öffne HACS in Home Assistant
2. Gehe zu "Integrationen"
3. Klicke auf die drei Punkte oben rechts und wähle "Benutzerdefinierte Repositories"
4. Füge die Repository-URL hinzu: `https://github.com/klauskirnbauerHTL/SmartMeter_Bgld`
5. Wähle Kategorie "Integration"
6. Klicke auf "Hinzufügen"
7. Suche nach "Smart Meter Burgenland" und installiere die Integration
8. Starte Home Assistant neu

### Manuelle Installation

1. Kopiere den Ordner `custom_components/smartmeter_burgenland` in dein Home Assistant `custom_components` Verzeichnis
2. Starte Home Assistant neu

## Konfiguration

1. Gehe zu Einstellungen → Geräte & Dienste
2. Klicke auf "+ Integration hinzufügen"
3. Suche nach "Smart Meter Burgenland"
4. Gib deine Login-Daten ein:
   - E-Mail/Benutzername für das Smart Meter Portal
   - Passwort
   - Zeitraum für Datenabfrage (in Tagen)
   - Gewünschte Datenauflösung
   - Strompreis für Kostenberechnung

## Sensoren

Die Integration erstellt folgende Sensoren:

- **Aktueller Verbrauch** - Neuester Verbrauchswert
- **Tagesverbrauch** - Verbrauch des aktuellen Tages
- **Durchschnittlicher Verbrauch** - Durchschnitt über den konfigurierten Zeitraum
- **Geschätzte Kosten** - Kosten basierend auf deinem Strompreis

## Support

Bei Problemen oder Fragen erstelle bitte ein Issue auf GitHub:
https://github.com/klauskirnbauerHTL/SmartMeter_Bgld/issues
