# 📦 GitHub Repository Setup - Anleitung

## ✅ Was wurde vorbereitet

Alle notwendigen Dateien für ein professionelles GitHub Repository und Home Assistant Custom Component wurden erstellt:

### Repository-Struktur
```
SmartMeter_Bgld/
├── .github/
│   ├── workflows/
│   │   └── validate.yml          # Automatische Tests
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md         # Bug Report Template
│   │   └── feature_request.md    # Feature Request Template
│   └── PULL_REQUEST_TEMPLATE.md  # Pull Request Template
├── custom_components/
│   └── smartmeter_burgenland/    # Home Assistant Integration
│       ├── __init__.py
│       ├── config_flow.py
│       ├── const.py
│       ├── manifest.json
│       ├── sensor.py
│       ├── smartmeter_client.py
│       ├── strings.json
│       └── translations/
│           └── de.json
├── .gitignore                     # Git Ignore Datei
├── CONTRIBUTING.md                # Contribution Guidelines
├── HOME_ASSISTANT_INTEGRATION.md  # HA Integration Anleitung
├── LICENSE                        # MIT License
├── README.md                      # Haupt-README
├── hacs.json                      # HACS Konfiguration
└── info.md                        # HACS Info
```

## 🚀 Schritte zum Erstellen des GitHub Repositories

### Schritt 1: Repository auf GitHub erstellen

1. Gehe zu [github.com](https://github.com)
2. Klicke auf das **+** oben rechts → **New repository**
3. Fülle aus:
   - **Repository name**: `SmartMeter_Bgld`
   - **Description**: `Home Assistant Integration für Smart Meter der Netz Burgenland`
   - **Visibility**: Public (wichtig für HACS!)
   - **NICHT** "Initialize with README" anklicken (wir haben schon eine)
4. Klicke auf **Create repository**

### Schritt 2: Lokales Repository mit GitHub verbinden

Öffne PowerShell im Projektordner und führe folgende Befehle aus:

```powershell
# Navigiere zum Projekt
cd "c:\Users\Klaus\OneDrive - htlpinkafeld.at\HTL\git\SmartMeter_Bgld"

# Prüfe ob Git initialisiert ist
git status

# Falls nicht initialisiert:
git init
git branch -M main

# Füge alle Dateien hinzu (bereits gemacht)
git add .

# Erstelle ersten Commit
git commit -m "Initial commit: Home Assistant Integration v1.0.0"

# Verbinde mit GitHub (ersetze USERNAME mit deinem GitHub Username)
git remote add origin https://github.com/klauskirnbauerHTL/SmartMeter_Bgld.git

# Pushe zum Repository
git push -u origin main
```

### Schritt 3: GitHub Repository konfigurieren

#### 3.1 Beschreibung und Topics hinzufügen
1. Gehe zu deinem Repository auf GitHub
2. Klicke auf das Zahnrad ⚙️ bei "About"
3. Füge hinzu:
   - **Description**: "Home Assistant Integration für Smart Meter der Netz Burgenland"
   - **Website**: Optional deine Website
   - **Topics**: `home-assistant`, `hacs`, `smart-meter`, `burgenland`, `energy-monitoring`

#### 3.2 Release erstellen
1. Gehe zu **Releases** → **Create a new release**
2. Fülle aus:
   - **Tag version**: `v1.0.0`
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**:
     ```markdown
     # 🎉 Initial Release
     
     Erste Version der Smart Meter Burgenland Integration für Home Assistant.
     
     ## Features
     - ✅ Automatischer Abruf von Verbrauchsdaten
     - ✅ Verschiedene Zeitauflösungen (15min, stündlich, täglich, monatlich)
     - ✅ Kostenberechnung
     - ✅ Home Assistant UI Konfiguration
     
     ## Installation
     Siehe [Installationsanleitung](https://github.com/klauskirnbauerHTL/SmartMeter_Bgld#-installation)
     ```
3. Klicke auf **Publish release**

## 📝 HACS Integration

### Voraussetzungen für HACS
✅ Public GitHub Repository  
✅ `hacs.json` vorhanden  
✅ `info.md` vorhanden  
✅ `manifest.json` mit korrekten URLs  
✅ Release erstellt (v1.0.0)  

### Installation in HACS

Nutzer können die Integration so installieren:

1. HACS öffnen → Integrationen
2. ⋮ (Menü) → Benutzerdefinierte Repositories
3. URL hinzufügen: `https://github.com/klauskirnbauerHTL/SmartMeter_Bgld`
4. Kategorie: Integration
5. Hinzufügen

### Optional: HACS Default Repository werden

Um in die Standard HACS Repository-Liste aufgenommen zu werden:

1. Gehe zu: https://github.com/hacs/default
2. Erstelle einen Pull Request
3. Folge den Anweisungen im Template

## 🔒 Sicherheit

### Sensible Daten schützen

Die `.gitignore` schützt bereits:
- `config.json` (mit Passwörtern)
- `secrets.yaml`
- `*.db` (Datenbanken)
- `downloads/*.csv` (persönliche Daten)

**WICHTIG**: Niemals Passwörter oder API-Keys committen!

## 📊 GitHub Features aktivieren

### Issues aktivieren
✅ Bereits aktiviert (Issue Templates vorhanden)

### Discussions (optional)
1. Settings → General → Features → Discussions ☑️
2. Nutze für Community-Fragen

### GitHub Actions
✅ Workflow bereits vorhanden (`.github/workflows/validate.yml`)
- Validiert automatisch bei jedem Push/PR
- Prüft HACS-Kompatibilität

## 🎯 Nächste Schritte

### Sofort:
1. ✅ Repository auf GitHub erstellen
2. ✅ Code pushen
3. ✅ Release v1.0.0 erstellen
4. ✅ In HACS testen

### Später:
- 📝 Wiki erstellen mit ausführlicher Dokumentation
- 🤝 Community aufbauen (Discussions)
- 🔄 Automatische Releases mit GitHub Actions
- 📊 Usage Statistics (optional)

## 📞 Support

Bei Fragen oder Problemen:
- **Issues**: https://github.com/klauskirnbauerHTL/SmartMeter_Bgld/issues
- **Discussions**: https://github.com/klauskirnbauerHTL/SmartMeter_Bgld/discussions

## 🎓 Weiterführende Links

- [HACS Documentation](https://hacs.xyz/docs/publish/start)
- [Home Assistant Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index)
- [GitHub Actions for Home Assistant](https://github.com/marketplace?type=actions&query=home+assistant)

---

**Viel Erfolg mit deiner Integration! 🚀**
