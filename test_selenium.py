"""
Test-Skript für Selenium Login
"""

from smartmeter_selenium import SmartMeterSeleniumDownloader

# Teste den Login mit Selenium
print("🚀 Starte Selenium-Test...")
print("Der Browser wird sich öffnen - beobachte was passiert!\n")

USERNAME = input("Benutzername (E-Mail): ")
PASSWORD = input("Passwort: ")

with SmartMeterSeleniumDownloader(USERNAME, PASSWORD, headless=False) as downloader:
    if downloader.login():
        print("\n✅ Login erfolgreich!")
        print("Browser bleibt 10 Sekunden offen, damit du das Portal sehen kannst...")
        import time
        time.sleep(10)
    else:
        print("\n❌ Login fehlgeschlagen")
        print("Prüfe die Screenshots im downloads/ Ordner für Details")
