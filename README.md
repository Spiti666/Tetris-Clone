# Tetris mit Gimmicks

Ein in Python mit Pygame erstellter Tetris-Klon mit speziellen Gimmick-Funktionen und modernem Design.

## Funktionen

- Klassisches Tetris-Gameplay mit modernen Erweiterungen
- Attraktives, animiertes Hauptmenü mit Partikeleffekten
- Moderne Optik mit 3D-Effekten und Partikelanimationen
- Spezielle Gimmick-Blöcke mit verschiedenen Effekten:
  - **Zeitlupe**: Verlangsamt das Fallen der Blöcke
  - **Zeitraffer**: Beschleunigt das Fallen der Blöcke
  - **Linienexplosion**: Entfernt Blöcke in der Umgebung
  - **Gravitationsänderung**: Ändert die Fallrichtung der Blöcke (nach links/rechts)
- Vorschaufunktion für das nächste Tetromino
- Schatten-Vorschau, wohin das aktuelle Tetromino fallen wird
- Punkte- und Levelsystem mit steigender Schwierigkeit
- Benutzerfreundliche Navigation mit Bestätigungsdialogen

## Steuerung

- **A/D**: Tetromino nach links/rechts bewegen
- **S**: Schneller fallen
- **W**: Sofort fallen lassen (Hard Drop)
- **Leertaste**: Tetromino drehen
- **P**: Pause
- **R**: Neustart
- **ESC**: Zurück zum Hauptmenü (mit Bestätigungsdialog)
- **J/N**: Bestätigen/Abbrechen in Dialogen

## Installation

1. Stellen Sie sicher, dass Python (3.7 oder höher) installiert ist
2. Installieren Sie die benötigten Pakete:
   ```
   pip install -r requirements.txt
   ```
3. Starten Sie das Spiel:
   ```
   python main.py
   ```

## Anforderungen

- Python 3.7+
- Pygame 2.5.2+

## Navigation

- **Hauptmenü**: Zeigt Steuerungsinformationen und Spieloptionen
- **Spiel**: Das eigentliche Tetris-Gameplay
- **ESC-Taste im Spiel**: Öffnet einen Bestätigungsdialog zur Rückkehr zum Hauptmenü
- **Hauptmenü -> Spiel**: Drücken Sie eine beliebige Taste im Hauptmenü
- **Spiel -> Hauptmenü**: Drücken Sie ESC und bestätigen Sie mit "J"

## Fehlerbehebung

Wenn Sie auf Probleme mit dem Spiel stoßen, versuchen Sie folgende Schritte:

1. **Spiel reagiert nicht mehr** - Wenn das Spiel einfriert oder "keine Rückmeldung" zeigt:
   - Starten Sie das Spiel neu
   - Überprüfen Sie, ob Ihr System die Mindestanforderungen erfüllt
   - Reduzieren Sie die Grafikeinstellungen in config.py:
     - Ändern Sie `SPEZIAL_CHANCE` auf einen niedrigeren Wert (z.B. 0.05)
     - Verringern Sie die Auflösung (`BREITE` und `HOEHE`)

2. **Performanceprobleme**:
   - Schließen Sie andere ressourcenintensive Programme
   - Reduzieren Sie die Anzahl der Partikeleffekte, indem Sie `MAX_PARTIKEL` in config.py reduzieren
   - Deaktivieren Sie die Schatten-Vorschau, indem Sie `self.preview_anzeigen = False` in der `__init__` Methode der `TetrisSpiel`-Klasse setzen

3. **Bekannte Fehler**:
   - Auf älteren Computern kann es zu Verlangsamungen kommen, wenn viele Gimmick-Effekte gleichzeitig aktiviert werden
   - Bei sehr schnellem Spiel (hohe Level) kann es zu Ungenauigkeiten bei der Kollisionserkennung kommen

4. **Debugging**:
   - Starten Sie das Spiel von der Kommandozeile, um Fehlermeldungen anzuzeigen:
     ```
     python main.py > debug.log 2>&1
     ```
   - Überprüfen Sie anschließend die debug.log-Datei auf Fehler

## Spielablauf

Das Spielprinzip folgt dem klassischen Tetris: Steuern Sie fallende Blöcke (Tetrominos), um komplette horizontale Reihen zu bilden. Vollständige Reihen werden entfernt und geben Punkte.

Die Besonderheit dieses Klons sind die Gimmick-Blöcke, die zufällig erscheinen und spezielle Effekte haben, wenn sie Teil einer entfernten Reihe sind. Dadurch wird das Gameplay dynamischer und strategischer.

## Punktesystem

- 1 Reihe: 100 × Level
- 2 Reihen: 300 × Level
- 3 Reihen: 500 × Level
- 4 Reihen: 800 × Level
- Linienexplosion: Zusätzliche 50 × Level

Das Level steigt mit jeder 10. entfernten Reihe, wodurch die Fallgeschwindigkeit zunimmt und mehr Punkte pro Reihe erzielt werden können.

## Entwickelt mit

- Python 3.7+
- Pygame 2.5.2+
- © 2025 - Entwickelt mit Liebe für klassische Spiele 