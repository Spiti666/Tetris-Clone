"""
Tetromino-Module für das Tetris-Spiel mit allen Formen und deren Logik
"""

import random
import pygame
from config import FARBEN, SPEZIAL_FARBEN, BLOCK_GROESSE, SPEZIAL_CHANCE

# Definition aller Tetromino-Formen
TETROMINOS = [
    # I-Form
    [
        [".....",
         ".....",
         "OOOO.",
         ".....",
         "....."],
        [".....",
         "..O..",
         "..O..",
         "..O..",
         "..O.."]
    ],
    # J-Form
    [
        [".....",
         ".....",
         ".OOO.",
         "...O.",
         "....."],
        [".....",
         "..O..",
         "..O..",
         ".OO..",
         "....."],
        [".....",
         ".....",
         ".O...",
         ".OOO.",
         "....."],
        [".....",
         "..OO.",
         "..O..",
         "..O..",
         "....."]
    ],
    # L-Form
    [
        [".....",
         ".....",
         ".OOO.",
         ".O...",
         "....."],
        [".....",
         ".OO..",
         "..O..",
         "..O..",
         "....."],
        [".....",
         ".....",
         "...O.",
         ".OOO.",
         "....."],
        [".....",
         "..O..",
         "..O..",
         "..OO.",
         "....."]
    ],
    # O-Form
    [
        [".....",
         ".....",
         ".OO..",
         ".OO..",
         "....."]
    ],
    # S-Form
    [
        [".....",
         ".....",
         "..OO.",
         ".OO..",
         "....."],
        [".....",
         "..O..",
         "..OO.",
         "...O.",
         "....."]
    ],
    # T-Form
    [
        [".....",
         ".....",
         ".OOO.",
         "..O..",
         "....."],
        [".....",
         "..O..",
         ".OO..",
         "..O..",
         "....."],
        [".....",
         ".....",
         "..O..",
         ".OOO.",
         "....."],
        [".....",
         "..O..",
         "..OO.",
         "..O..",
         "....."]
    ],
    # Z-Form
    [
        [".....",
         ".....",
         ".OO..",
         "..OO.",
         "....."],
        [".....",
         "...O.",
         "..OO.",
         "..O..",
         "....."]
    ]
]

class Tetromino:
    """Klasse für die Tetris-Formen"""
    
    def __init__(self, x, y, form_idx=None):
        """Initialisiert ein neues Tetromino"""
        try:
            if form_idx is None:
                # Zufällige Form auswählen
                self.form_idx = random.randint(0, len(TETROMINOS) - 1)
            else:
                # Sicherstellen, dass form_idx gültig ist
                self.form_idx = max(0, min(form_idx, len(TETROMINOS) - 1))
            
            self.formen = TETROMINOS[self.form_idx]
            self.aktuelle_rotation = 0
            self.form = self.formen[self.aktuelle_rotation]
            
            # Initialisiere spezial_typ immer, unabhängig davon, ob es ein Spezialblock ist
            self.spezial_typ = 0
            
            # Standardfarbe oder spezielle Farbe (Gimmick)
            self.ist_spezial = random.random() < SPEZIAL_CHANCE
            
            if self.ist_spezial:
                self.spezial_typ = random.randint(0, len(SPEZIAL_FARBEN) - 1)
                self.farbe = SPEZIAL_FARBEN[self.spezial_typ]
                self.gimmick_effekt = self.spezial_typ
            else:
                self.farbe = FARBEN[self.form_idx]
                self.gimmick_effekt = -1
            
            # Position auf dem Spielfeld
            self.x = x
            self.y = y
            
            # Glüheffekt für spezielle Blöcke
            self.glow_step = 0
            self.glow_direction = 1
        except Exception as e:
            print(f"Fehler bei Tetromino-Initialisierung: {e}")
            # Fallback zu sicheren Werten
            self.form_idx = 0
            self.formen = TETROMINOS[0]
            self.aktuelle_rotation = 0
            self.form = self.formen[0]
            self.ist_spezial = False
            self.spezial_typ = 0  # Auch hier initialisieren
            self.farbe = FARBEN[0]
            self.gimmick_effekt = -1
            self.x = x
            self.y = y
            self.glow_step = 0
            self.glow_direction = 1
        
    def rotieren(self):
        """Tetromino im Uhrzeigersinn drehen"""
        self.aktuelle_rotation = (self.aktuelle_rotation + 1) % len(self.formen)
        self.form = self.formen[self.aktuelle_rotation]
        
    def pos_rückgängig_rotieren(self):
        """Rotationsindex zurücksetzen (wird bei Kollision verwendet)"""
        self.aktuelle_rotation = (self.aktuelle_rotation - 1) % len(self.formen)
        self.form = self.formen[self.aktuelle_rotation]
        
    def get_positions(self):
        """Gibt die absoluten Positionen der Blöcke zurück"""
        positions = []
        if not self.form:  # Sicherheitscheck
            return positions
        
        for i, zeile in enumerate(self.form):
            if i >= len(self.form):  # Sicherheitscheck
                break
            
            for j, zelle in enumerate(zeile):
                if j >= len(zeile):  # Sicherheitscheck
                    break
                
                if zelle == 'O':
                    positions.append((self.x + j, self.y + i))
        return positions
    
    def update_glow(self):
        """Aktualisiert den Glüheffekt für spezielle Blöcke"""
        if self.ist_spezial:
            self.glow_step += 0.05 * self.glow_direction
            if self.glow_step >= 1.0:
                self.glow_direction = -1
            elif self.glow_step <= 0.0:
                self.glow_direction = 1
                
    def get_glow_color(self):
        """Gibt die aktuelle Glühfarbe zurück"""
        if not self.ist_spezial:
            return self.farbe
            
        r, g, b = self.farbe
        glow_intensity = abs(self.glow_step - 0.5) * 0.7 + 0.3  # 0.3 - 1.0
        
        # Begrenzen der Werte auf 0-255
        r_glow = min(255, int(r * glow_intensity))
        g_glow = min(255, int(g * glow_intensity))
        b_glow = min(255, int(b * glow_intensity))
        
        return (r_glow, g_glow, b_glow)
    
    def zeichnen(self, screen, offset_x, offset_y):
        """Zeichnet das Tetromino auf den Bildschirm"""
        try:
            self.update_glow()
            farbe = self.get_glow_color()
            
            if not self.form:  # Sicherheitscheck
                return
            
            for i, zeile in enumerate(self.form):
                if i >= len(self.form):  # Sicherheitscheck
                    continue
                
                for j, zelle in enumerate(zeile):
                    if j >= len(zeile):  # Sicherheitscheck
                        continue
                    
                    if zelle == 'O':
                        # Hauptblock zeichnen
                        x_pos = offset_x + (self.x + j) * BLOCK_GROESSE
                        y_pos = offset_y + (self.y + i) * BLOCK_GROESSE
                        
                        # Prüfen, ob die Position gültig ist
                        if x_pos < 0 or y_pos < 0 or x_pos > screen.get_width() or y_pos > screen.get_height():
                            continue
                            
                        rect = pygame.Rect(
                            x_pos,
                            y_pos,
                            BLOCK_GROESSE, BLOCK_GROESSE
                        )
                        pygame.draw.rect(screen, farbe, rect)
                        
                        # Hellerer Rand oben links (3D-Effekt)
                        pygame.draw.line(screen, self.hellere_farbe(farbe), 
                                        (rect.left, rect.top), 
                                        (rect.right, rect.top), 2)
                        pygame.draw.line(screen, self.hellere_farbe(farbe), 
                                        (rect.left, rect.top), 
                                        (rect.left, rect.bottom), 2)
                        
                        # Dunklerer Rand unten rechts (3D-Effekt)
                        pygame.draw.line(screen, self.dunklere_farbe(farbe), 
                                        (rect.right, rect.top), 
                                        (rect.right, rect.bottom), 2)
                        pygame.draw.line(screen, self.dunklere_farbe(farbe), 
                                        (rect.left, rect.bottom), 
                                        (rect.right, rect.bottom), 2)
                        
                        # Spezialsymbol für Gimmick-Blöcke
                        if self.ist_spezial:
                            self.zeichne_spezial_symbol(screen, rect)
        except Exception as e:
            print(f"Fehler beim Zeichnen des Tetrominos: {e}")
    
    def zeichne_spezial_symbol(self, screen, rect):
        """Zeichnet ein spezielles Symbol für Gimmick-Blöcke"""
        # Symbole für verschiedene Gimmicks
        center_x = rect.left + BLOCK_GROESSE // 2
        center_y = rect.top + BLOCK_GROESSE // 2
        radius = BLOCK_GROESSE // 4
        
        if self.gimmick_effekt == 0:  # Zeitlupe
            # Sanduhr-Symbol
            pygame.draw.polygon(screen, (255, 255, 255), 
                              [(center_x - radius, center_y - radius),
                               (center_x + radius, center_y - radius),
                               (center_x, center_y)])
            pygame.draw.polygon(screen, (255, 255, 255), 
                              [(center_x - radius, center_y + radius),
                               (center_x + radius, center_y + radius),
                               (center_x, center_y)])
                               
        elif self.gimmick_effekt == 1:  # Zeitraffer
            # Blitz-Symbol
            pygame.draw.polygon(screen, (255, 255, 255), 
                              [(center_x, center_y - radius),
                               (center_x - radius//2, center_y),
                               (center_x, center_y),
                               (center_x - radius//2, center_y + radius)])
                               
        elif self.gimmick_effekt == 2:  # Linienexplosion
            # Stern-Symbol
            for i in range(8):
                angle = i * 3.14159 / 4
                end_x = center_x + int(radius * 1.2 * (1 if i % 2 == 0 else 0.5) * (
                    -1 if angle > 3.14159 and angle < 2 * 3.14159 else 1))
                end_y = center_y + int(radius * 1.2 * (1 if i % 2 == 0 else 0.5) * (
                    -1 if angle > 0 and angle < 3.14159 else 1))
                pygame.draw.line(screen, (255, 255, 255), 
                               (center_x, center_y), (end_x, end_y), 2)
                               
        elif self.gimmick_effekt == 3:  # Gravitation ändern
            # Pfeil-Symbol
            pygame.draw.polygon(screen, (255, 255, 255), 
                              [(center_x, center_y - radius),
                               (center_x + radius, center_y),
                               (center_x - radius, center_y)])
    
    def hellere_farbe(self, farbe, faktor=1.3):
        """Gibt eine hellere Version der Farbe zurück"""
        r, g, b = farbe
        return (min(255, int(r * faktor)), 
                min(255, int(g * faktor)), 
                min(255, int(b * faktor)))
                
    def dunklere_farbe(self, farbe, faktor=0.7):
        """Gibt eine dunklere Version der Farbe zurück"""
        r, g, b = farbe
        return (max(0, int(r * faktor)), 
                max(0, int(g * faktor)), 
                max(0, int(b * faktor))) 