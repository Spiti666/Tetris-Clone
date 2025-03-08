"""
Konfigurationsdatei für das Tetris-Spiel mit allen Konstanten
"""

# Fenstergröße
BREITE = 800
HOEHE = 700

# Spielfeld
SPALTEN = 10
ZEILEN = 20
BLOCK_GROESSE = 30
SPIELFELD_BREITE = SPALTEN * BLOCK_GROESSE
SPIELFELD_HOEHE = ZEILEN * BLOCK_GROESSE
SPIELFELD_X = (BREITE - SPIELFELD_BREITE) // 2
SPIELFELD_Y = HOEHE - SPIELFELD_HOEHE - 20

# Farben (RGB)
SCHWARZ = (0, 0, 0)
WEISS = (255, 255, 255)
GRAU = (128, 128, 128)
DUNKELGRAU = (50, 50, 50)
HELLGRAU = (200, 200, 200)

# Tetromino-Farben
FARBEN = [
    (0, 200, 200),    # I - Cyan
    (0, 0, 200),      # J - Blau
    (200, 150, 0),    # L - Orange
    (200, 200, 0),    # O - Gelb
    (0, 200, 0),      # S - Grün
    (200, 0, 200),    # T - Lila
    (200, 0, 0)       # Z - Rot
]

# Spezial-Tetromino-Farben für Gimmicks
SPEZIAL_FARBEN = [
    (255, 215, 0),    # Gold (Zeitlupe)
    (255, 0, 255),    # Magenta (Zeitraffer)
    (0, 255, 255),    # Neon Cyan (Linienexplosion)
    (255, 105, 180)   # Pink (Gravitation ändern)
]

# Spielparameter
ANFANGS_FALLZEIT = 0.8  # Sekunden
LEVEL_GESCHWINDIGKEIT = 0.05  # Geschwindigkeitssteigerung pro Level
PUNKTE_EINE_REIHE = 100
PUNKTE_ZWEI_REIHEN = 300
PUNKTE_DREI_REIHEN = 500
PUNKTE_VIER_REIHEN = 800

# Gimmick-Parameter
SPEZIAL_CHANCE = 0.05  # Reduziert von 0.15 auf 0.05 (5% Chance für ein Spezialblock)
ZEITLUPE_FAKTOR = 1.5  # Reduziert von 2.0 auf 1.5 (weniger starke Verlangsamung)
ZEITRAFFER_FAKTOR = 0.7  # Erhöht von 0.5 auf 0.7 (weniger starke Beschleunigung)
EXPLOSION_RADIUS = 1  # Radius der Linienexplosion (Blöcke in jede Richtung)

# Schriftarten
SCHRIFT_GROSS = 48
SCHRIFT_MITTEL = 36
SCHRIFT_KLEIN = 24

# Farben für UI-Elemente
UI_HINTERGRUND = (30, 30, 50)
UI_TEXT = (220, 220, 220)
UI_AKZENT = (100, 200, 255)
UI_HIGHLIGHT = (255, 255, 100)

# Performance-Parameter
MAX_PARTIKEL = 300  # Maximale Anzahl gleichzeitiger Partikel
MAX_FPS = 60  # Ziel-Bildwiederholrate 