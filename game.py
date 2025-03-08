"""
Hauptspiellogik für den Tetris-Klon
"""

import random
import pygame
import time
import traceback
from config import (
    SPALTEN, ZEILEN, BLOCK_GROESSE, FARBEN, SPIELFELD_X, SPIELFELD_Y,
    ANFANGS_FALLZEIT, LEVEL_GESCHWINDIGKEIT,
    PUNKTE_EINE_REIHE, PUNKTE_ZWEI_REIHEN, PUNKTE_DREI_REIHEN, PUNKTE_VIER_REIHEN,
    ZEITLUPE_FAKTOR, ZEITRAFFER_FAKTOR, EXPLOSION_RADIUS,
    SCHWARZ, WEISS, GRAU, DUNKELGRAU, HELLGRAU, MAX_PARTIKEL
)
from tetromino import Tetromino

class TetrisSpiel:
    """Hauptspielklasse für den Tetris-Klon"""
    
    def __init__(self):
        """Initialisiert ein neues Spiel"""
        try:
            # Spielfeld initialisieren (0 = leer, 1-7 = Tetromino-Farbe)
            self.spielfeld = [[0 for _ in range(SPALTEN)] for _ in range(ZEILEN)]
            self.spielfeld_farben = [[SCHWARZ for _ in range(SPALTEN)] for _ in range(ZEILEN)]
            self.spielfeld_gimmicks = [[-1 for _ in range(SPALTEN)] for _ in range(ZEILEN)]
            
            # Spielwerte
            self.score = 0
            self.level = 1
            self.linien = 0
            self.fallzeit = ANFANGS_FALLZEIT
            self.letzte_fallzeit = time.time()
            
            # Aktives Tetromino
            self.aktuelles_tetromino = self.neues_tetromino()
            self.naechstes_tetromino = self.neues_tetromino()
            
            # Spielstatus
            self.spiel_aktiv = True
            self.pause = False
            
            # Gimmick-Status
            self.aktiver_zeitfaktor = 1.0
            self.zeitfaktor_timer = 0
            self.gravitation_richtung = 0  # 0=runter, 1=rechts, 2=links
            self.gravitation_timer = 0
            
            # Partikel für visuelle Effekte
            self.partikel = []
            
            # Spielparameter
            self.automatisch_fallen = True
            self.preview_anzeigen = True
            
            # Sound-Effekte
            self.sound_geladen = False
            self.sounds = {}
            
            # FPS-Zähler für Leistungsoptimierung
            self.frame_count = 0
            self.last_time = time.time()
            self.fps = 0
            
        except Exception as e:
            print(f"Fehler bei Spielinitialisierung: {e}")
            # Sicherstellen, dass Basisattribute gesetzt sind
            self.spielfeld = [[0 for _ in range(SPALTEN)] for _ in range(ZEILEN)]
            self.spielfeld_farben = [[SCHWARZ for _ in range(SPALTEN)] for _ in range(ZEILEN)]
            self.spielfeld_gimmicks = [[-1 for _ in range(SPALTEN)] for _ in range(ZEILEN)]
            self.score = 0
            self.level = 1
            self.linien = 0
            self.fallzeit = ANFANGS_FALLZEIT
            self.letzte_fallzeit = time.time()
            self.aktuelles_tetromino = None
            self.naechstes_tetromino = None
            self.spiel_aktiv = True
            self.pause = False
            self.aktiver_zeitfaktor = 1.0
            self.zeitfaktor_timer = 0
            self.gravitation_richtung = 0
            self.gravitation_timer = 0
            self.partikel = []
            self.automatisch_fallen = True
            self.preview_anzeigen = False  # Vorschau deaktivieren bei Fehlern
            self.sound_geladen = False
            self.sounds = {}
    
    def neues_tetromino(self):
        """Erstellt ein neues zufälliges Tetromino"""
        return Tetromino(SPALTEN // 2 - 2, 0)
    
    def spielfeld_zeichnen(self, screen):
        """Zeichnet das Spielfeld und die Tetrominos"""
        try:
            # Spielfeldhintergrund
            hintergrund = pygame.Rect(
                SPIELFELD_X - 2, SPIELFELD_Y - 2,
                SPALTEN * BLOCK_GROESSE + 4, ZEILEN * BLOCK_GROESSE + 4
            )
            pygame.draw.rect(screen, HELLGRAU, hintergrund)
            pygame.draw.rect(screen, SCHWARZ, hintergrund, 2)
            
            # Spielfeldraster
            for zeile in range(ZEILEN):
                for spalte in range(SPALTEN):
                    # Zellenposition
                    x = SPIELFELD_X + spalte * BLOCK_GROESSE
                    y = SPIELFELD_Y + zeile * BLOCK_GROESSE
                    rect = pygame.Rect(x, y, BLOCK_GROESSE, BLOCK_GROESSE)
                    
                    # Hintergrund
                    pygame.draw.rect(screen, DUNKELGRAU, rect)
                    
                    # Gesetzte Blöcke
                    if self.spielfeld[zeile][spalte] != 0:
                        farbe = self.spielfeld_farben[zeile][spalte]
                        pygame.draw.rect(screen, farbe, rect)
                        
                        # 3D-Effekt
                        pygame.draw.line(screen, self.hellere_farbe(farbe), 
                                        (rect.left, rect.top), 
                                        (rect.right, rect.top), 2)
                        pygame.draw.line(screen, self.hellere_farbe(farbe), 
                                        (rect.left, rect.top), 
                                        (rect.left, rect.bottom), 2)
                        pygame.draw.line(screen, self.dunklere_farbe(farbe), 
                                        (rect.right, rect.top), 
                                        (rect.right, rect.bottom), 2)
                        pygame.draw.line(screen, self.dunklere_farbe(farbe), 
                                        (rect.left, rect.bottom), 
                                        (rect.right, rect.bottom), 2)
                        
                        # Gimmick-Symbol anzeigen
                        gimmick = self.spielfeld_gimmicks[zeile][spalte]
                        if gimmick >= 0:
                            self.zeichne_gimmick_symbol(screen, rect, gimmick)
                    
                    # Gitternetz
                    pygame.draw.rect(screen, SCHWARZ, rect, 1)
            
            # Vorschau des aktuellen Tetrominos (wo es landen würde)
            if self.preview_anzeigen and self.aktuelles_tetromino and self.spiel_aktiv and not self.pause:
                shadow_y = self.aktuelles_tetromino.y
                
                # Verhindere endlose Schleife mit maximal Anzahl an Iterationen
                max_iterations = ZEILEN
                iterations = 0
                temp_tetromino = Tetromino(
                    self.aktuelles_tetromino.x,
                    shadow_y,
                    self.aktuelles_tetromino.form_idx
                )
                temp_tetromino.aktuelle_rotation = self.aktuelles_tetromino.aktuelle_rotation
                temp_tetromino.form = temp_tetromino.formen[temp_tetromino.aktuelle_rotation]
                
                while not self.kollision_pruefen(0, 1, temp_tetromino) and iterations < max_iterations:
                    shadow_y += 1
                    temp_tetromino.y = shadow_y
                    iterations += 1
                
                # Falls das Tetromino nicht bereits am Boden ist
                if shadow_y > self.aktuelles_tetromino.y:
                    shadow_tetromino = Tetromino(
                        self.aktuelles_tetromino.x, 
                        shadow_y,
                        self.aktuelles_tetromino.form_idx
                    )
                    shadow_tetromino.aktuelle_rotation = self.aktuelles_tetromino.aktuelle_rotation
                    shadow_tetromino.form = shadow_tetromino.formen[shadow_tetromino.aktuelle_rotation]
                    
                    # Transparente Vorschau zeichnen
                    for i, zeile in enumerate(shadow_tetromino.form):
                        for j, zelle in enumerate(zeile):
                            if zelle == 'O':
                                x = SPIELFELD_X + (shadow_tetromino.x + j) * BLOCK_GROESSE
                                y = SPIELFELD_Y + (shadow_tetromino.y + i) * BLOCK_GROESSE
                                rect = pygame.Rect(x, y, BLOCK_GROESSE, BLOCK_GROESSE)
                                
                                # Transparente Version der Originalfarbe
                                r, g, b = self.aktuelles_tetromino.farbe
                                transparent_farbe = (r, g, b, 100)
                                
                                # Umriss zeichnen
                                pygame.draw.rect(screen, (r//2, g//2, b//2), rect, 2)
            
            # Aktuelles Tetromino zeichnen
            if self.aktuelles_tetromino and self.spiel_aktiv:
                self.aktuelles_tetromino.zeichnen(screen, SPIELFELD_X, SPIELFELD_Y)
            
            # Nächstes Tetromino-Vorschau zeichnen (in einer Box rechts vom Spielfeld)
            vorschau_x = SPIELFELD_X + SPALTEN * BLOCK_GROESSE + 30
            vorschau_y = SPIELFELD_Y + 50
            vorschau_breite = 6 * BLOCK_GROESSE
            vorschau_hoehe = 6 * BLOCK_GROESSE
            
            # Vorschaubox
            vorschau_box = pygame.Rect(vorschau_x, vorschau_y, vorschau_breite, vorschau_hoehe)
            pygame.draw.rect(screen, HELLGRAU, vorschau_box)
            pygame.draw.rect(screen, SCHWARZ, vorschau_box, 2)
            
            # Titel der Vorschaubox
            font = pygame.font.SysFont("Arial", 24)
            naechstes_text = font.render("Nächstes:", True, WEISS)
            screen.blit(naechstes_text, (vorschau_x + 10, vorschau_y - 35))
            
            # Nächstes Tetromino in der Vorschaubox
            if self.naechstes_tetromino:
                try:
                    vorschau_tetromino = Tetromino(0, 0, self.naechstes_tetromino.form_idx)
                    
                    # Attribute sicher kopieren (mit Fehlerbehandlung)
                    if hasattr(self.naechstes_tetromino, 'ist_spezial'):
                        vorschau_tetromino.ist_spezial = self.naechstes_tetromino.ist_spezial
                    
                    if hasattr(self.naechstes_tetromino, 'spezial_typ'):
                        vorschau_tetromino.spezial_typ = self.naechstes_tetromino.spezial_typ
                    
                    if hasattr(self.naechstes_tetromino, 'farbe'):
                        vorschau_tetromino.farbe = self.naechstes_tetromino.farbe
                    
                    if hasattr(self.naechstes_tetromino, 'gimmick_effekt'):
                        vorschau_tetromino.gimmick_effekt = self.naechstes_tetromino.gimmick_effekt
                    
                    # Position anpassen (zentriert in der Vorschaubox)
                    vorschau_tetromino.x = 1
                    vorschau_tetromino.y = 1
                    vorschau_tetromino.zeichnen(screen, vorschau_x, vorschau_y)
                except Exception as e:
                    print(f"Fehler beim Zeichnen des Vorschau-Tetrominos: {e}")
            
            # Partikel zeichnen
            self.partikel_aktualisieren(screen)
        except Exception as e:
            print(f"Fehler beim Zeichnen des Spielfelds: {e}")
            traceback.print_exc()
    
    def zeichne_gimmick_symbol(self, screen, rect, gimmick_typ):
        """Zeichnet ein spezielles Symbol für Gimmick-Blöcke"""
        center_x = rect.left + BLOCK_GROESSE // 2
        center_y = rect.top + BLOCK_GROESSE // 2
        radius = BLOCK_GROESSE // 4
        
        if gimmick_typ == 0:  # Zeitlupe
            # Sanduhr-Symbol
            pygame.draw.polygon(screen, WEISS, 
                             [(center_x - radius, center_y - radius),
                              (center_x + radius, center_y - radius),
                              (center_x, center_y)])
            pygame.draw.polygon(screen, WEISS, 
                             [(center_x - radius, center_y + radius),
                              (center_x + radius, center_y + radius),
                              (center_x, center_y)])
                              
        elif gimmick_typ == 1:  # Zeitraffer
            # Blitz-Symbol
            pygame.draw.polygon(screen, WEISS, 
                             [(center_x, center_y - radius),
                              (center_x - radius//2, center_y),
                              (center_x, center_y),
                              (center_x - radius//2, center_y + radius)])
                              
        elif gimmick_typ == 2:  # Linienexplosion
            # Stern-Symbol
            for i in range(8):
                angle = i * 3.14159 / 4
                end_x = center_x + int(radius * 1.2 * (1 if i % 2 == 0 else 0.5) * (
                    -1 if angle > 3.14159 and angle < 2 * 3.14159 else 1))
                end_y = center_y + int(radius * 1.2 * (1 if i % 2 == 0 else 0.5) * (
                    -1 if angle > 0 and angle < 3.14159 else 1))
                pygame.draw.line(screen, WEISS, 
                              (center_x, center_y), (end_x, end_y), 2)
                              
        elif gimmick_typ == 3:  # Gravitation ändern
            # Pfeil-Symbol
            pygame.draw.polygon(screen, WEISS, 
                             [(center_x, center_y - radius),
                              (center_x + radius, center_y),
                              (center_x - radius, center_y)])
    
    def partikel_aktualisieren(self, screen):
        """Aktualisiert und zeichnet alle Partikel"""
        neue_partikel = []
        for partikel in self.partikel:
            # Partikel: [x, y, color, radius, lebensdauer, x_vel, y_vel]
            x, y, farbe, radius, lebensdauer, x_vel, y_vel = partikel
            
            # Partikel bewegen
            x += x_vel
            y += y_vel
            radius *= 0.95  # Größe reduzieren
            lebensdauer -= 1
            
            # Lebende Partikel beibehalten
            if lebensdauer > 0 and radius > 0.5:
                pygame.draw.circle(screen, farbe, (int(x), int(y)), int(radius))
                neue_partikel.append([x, y, farbe, radius, lebensdauer, x_vel, y_vel])
                
        self.partikel = neue_partikel

    def partikel_erstellen(self, x, y, farbe, anzahl=10):
        """Erstellt Partikeleffekte an der angegebenen Position"""
        # Maximale Anzahl von Partikeln begrenzen
        if len(self.partikel) > MAX_PARTIKEL:
            # Wenn zu viele Partikel, entferne die ältesten
            self.partikel = self.partikel[-MAX_PARTIKEL//2:]
        
        # Begrenze die anzahl für diese Erstellung
        anzahl = min(anzahl, 20)
        
        for _ in range(anzahl):
            winkel = random.uniform(0, 6.28)  # 0 bis 2*Pi
            geschwindigkeit = random.uniform(1, 3)
            x_vel = geschwindigkeit * pygame.math.Vector2(1, 0).rotate(winkel * 180 / 3.14159).x
            y_vel = geschwindigkeit * pygame.math.Vector2(1, 0).rotate(winkel * 180 / 3.14159).y
            radius = random.uniform(2, 5)
            lebensdauer = random.randint(20, 40)
            
            self.partikel.append([x, y, farbe, radius, lebensdauer, x_vel, y_vel])
    
    def tetromino_bewegen(self, dx, dy):
        """Bewegt das aktuelle Tetromino wenn möglich"""
        if not self.aktuelles_tetromino or not self.spiel_aktiv or self.pause:
            return False
            
        if not self.kollision_pruefen(dx, dy, self.aktuelles_tetromino):
            self.aktuelles_tetromino.x += dx
            self.aktuelles_tetromino.y += dy
            return True
        
        # Wenn das Tetromino nicht nach unten bewegt werden kann, setze es fest
        if dy > 0:
            self.tetromino_fixieren()
            return True
            
        return False
    
    def tetromino_rotieren(self):
        """Rotiert das aktuelle Tetromino wenn möglich"""
        if not self.aktuelles_tetromino or not self.spiel_aktiv or self.pause:
            return
            
        self.aktuelles_tetromino.rotieren()
        
        # Prüfe, ob die neue Position gültig ist
        if self.kollision_pruefen(0, 0, self.aktuelles_tetromino):
            # Versuche das Tetromino nach links/rechts zu schieben, falls es am Rand kollidiert
            verschiebungen = [1, -1, 2, -2]
            valid_rotation = False
            
            for dx in verschiebungen:
                if not self.kollision_pruefen(dx, 0, self.aktuelles_tetromino):
                    self.aktuelles_tetromino.x += dx
                    valid_rotation = True
                    break
            
            # Wenn keine gültige Position gefunden wurde, mach die Drehung rückgängig
            if not valid_rotation:
                self.aktuelles_tetromino.pos_rückgängig_rotieren()
    
    def tetromino_fixieren(self):
        """Fügt das aktuelle Tetromino dem Spielfeld hinzu"""
        if not self.aktuelles_tetromino:
            return
            
        positions = self.aktuelles_tetromino.get_positions()
        
        # Prüfe ob das Spiel vorbei ist (Tetromino kann nicht mehr platziert werden)
        for x, y in positions:
            if y < 0:
                self.spiel_aktiv = False
                return
        
        # Tetromino zum Spielfeld hinzufügen
        for x, y in positions:
            if 0 <= y < ZEILEN and 0 <= x < SPALTEN:
                self.spielfeld[y][x] = self.aktuelles_tetromino.form_idx + 1
                self.spielfeld_farben[y][x] = self.aktuelles_tetromino.farbe
                
                # Speichere Gimmick-Effekt wenn vorhanden
                if self.aktuelles_tetromino.ist_spezial:
                    self.spielfeld_gimmicks[y][x] = self.aktuelles_tetromino.gimmick_effekt
                    
                    # Partikeleffekt für spezielle Blöcke
                    bx = SPIELFELD_X + x * BLOCK_GROESSE + BLOCK_GROESSE // 2
                    by = SPIELFELD_Y + y * BLOCK_GROESSE + BLOCK_GROESSE // 2
                    self.partikel_erstellen(bx, by, self.aktuelles_tetromino.farbe, 15)
        
        # Volle Reihen entfernen
        self.reihen_entfernen()
        
        # Nächstes Tetromino vorbereiten
        self.aktuelles_tetromino = self.naechstes_tetromino
        
        # Neues Tetromino erstellen und an den oberen Rand des Spielfelds setzen
        self.naechstes_tetromino = self.neues_tetromino()
        
        # Eine kleine Verzögerung hinzufügen, damit das neue Tetromino nicht sofort fallen gelassen wird
        self.letzte_fallzeit = time.time() + 0.3  # Leichte Verzögerung für besseres Gameplay
    
    def reihen_entfernen(self):
        """Entfernt volle Reihen und aktualisiert den Score"""
        volle_reihen = []
        for y in range(ZEILEN):
            if all(self.spielfeld[y][x] != 0 for x in range(SPALTEN)):
                volle_reihen.append(y)
        
        # Entferne die vollen Reihen
        anzahl_reihen = len(volle_reihen)
        if anzahl_reihen > 0:
            # Prüfe auf Gimmick-Effekte in den zu entfernenden Reihen
            for reihe in volle_reihen:
                for x in range(SPALTEN):
                    if self.spielfeld_gimmicks[reihe][x] >= 0:
                        self.gimmick_aktivieren(self.spielfeld_gimmicks[reihe][x], x, reihe)
            
            # Punkte hinzufügen
            if anzahl_reihen == 1:
                self.score += PUNKTE_EINE_REIHE * self.level
            elif anzahl_reihen == 2:
                self.score += PUNKTE_ZWEI_REIHEN * self.level
            elif anzahl_reihen == 3:
                self.score += PUNKTE_DREI_REIHEN * self.level
            elif anzahl_reihen == 4:
                self.score += PUNKTE_VIER_REIHEN * self.level
            
            # Partikeleffekte für entfernte Reihen
            for reihe in volle_reihen:
                for x in range(SPALTEN):
                    px = SPIELFELD_X + x * BLOCK_GROESSE + BLOCK_GROESSE // 2
                    py = SPIELFELD_Y + reihe * BLOCK_GROESSE + BLOCK_GROESSE // 2
                    self.partikel_erstellen(px, py, self.spielfeld_farben[reihe][x], 5)
            
            # Entferne die Reihen und verschiebe die darüber liegenden nach unten
            for reihe in sorted(volle_reihen):
                for y in range(reihe, 0, -1):
                    for x in range(SPALTEN):
                        self.spielfeld[y][x] = self.spielfeld[y-1][x]
                        self.spielfeld_farben[y][x] = self.spielfeld_farben[y-1][x]
                        self.spielfeld_gimmicks[y][x] = self.spielfeld_gimmicks[y-1][x]
                
                # Oberste Reihe leeren
                for x in range(SPALTEN):
                    self.spielfeld[0][x] = 0
                    self.spielfeld_farben[0][x] = SCHWARZ
                    self.spielfeld_gimmicks[0][x] = -1
            
            # Linien und Level aktualisieren
            self.linien += anzahl_reihen
            
            # Level erhöhen je 10 Linien
            neues_level = self.linien // 10 + 1
            if neues_level > self.level:
                self.level = neues_level
                self.fallzeit = max(0.05, ANFANGS_FALLZEIT - (self.level - 1) * LEVEL_GESCHWINDIGKEIT)
    
    def gimmick_aktivieren(self, gimmick_typ, x, y):
        """Aktiviert den Effekt eines Gimmick-Blocks"""
        if gimmick_typ == 0:  # Zeitlupe
            self.aktiver_zeitfaktor = ZEITLUPE_FAKTOR
            self.zeitfaktor_timer = 200  # Reduziert von 500
            
            # Effekt-Partikel
            px = SPIELFELD_X + x * BLOCK_GROESSE + BLOCK_GROESSE // 2
            py = SPIELFELD_Y + y * BLOCK_GROESSE + BLOCK_GROESSE // 2
            self.partikel_erstellen(px, py, (255, 215, 0), 10)  # Reduziert von 20
                
        elif gimmick_typ == 1:  # Zeitraffer
            self.aktiver_zeitfaktor = ZEITRAFFER_FAKTOR
            self.zeitfaktor_timer = 200  # Reduziert von 500
            
            # Effekt-Partikel
            px = SPIELFELD_X + x * BLOCK_GROESSE + BLOCK_GROESSE // 2
            py = SPIELFELD_Y + y * BLOCK_GROESSE + BLOCK_GROESSE // 2
            self.partikel_erstellen(px, py, (255, 0, 255), 10)  # Reduziert von 20
                
        elif gimmick_typ == 2:  # Linienexplosion
            # Entferne Blöcke im Umkreis
            for dy in range(-EXPLOSION_RADIUS, EXPLOSION_RADIUS + 1):
                for dx in range(-EXPLOSION_RADIUS, EXPLOSION_RADIUS + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < SPALTEN and 0 <= ny < ZEILEN:
                        if self.spielfeld[ny][nx] != 0:
                            # Partikeleffekt
                            px = SPIELFELD_X + nx * BLOCK_GROESSE + BLOCK_GROESSE // 2
                            py = SPIELFELD_Y + ny * BLOCK_GROESSE + BLOCK_GROESSE // 2
                            self.partikel_erstellen(px, py, self.spielfeld_farben[ny][nx], 8)  # Reduziert von 15
                            
                            # Block entfernen
                            self.spielfeld[ny][nx] = 0
                            self.spielfeld_farben[ny][nx] = SCHWARZ
                            self.spielfeld_gimmicks[ny][nx] = -1
                            
            # Zusätzlicher Punktebonus
            self.score += 50 * self.level
                            
        elif gimmick_typ == 3:  # Gravitation ändern
            # Wechsele zwischen den Gravitationsrichtungen
            self.gravitation_richtung = (self.gravitation_richtung + 1) % 3
            self.gravitation_timer = 200  # Reduziert von 300
            
            # Effekt-Partikel im gesamten Spielfeld
            for i in range(10):  # Reduziert von 20
                px = SPIELFELD_X + random.randint(0, SPALTEN) * BLOCK_GROESSE
                py = SPIELFELD_Y + random.randint(0, ZEILEN) * BLOCK_GROESSE
                self.partikel_erstellen(px, py, (255, 105, 180), 5)  # Reduziert von 10
    
    def zeitfaktor_aktualisieren(self):
        """Aktualisiert den aktiven Zeitfaktor"""
        if self.zeitfaktor_timer > 0:
            self.zeitfaktor_timer -= 1
            if self.zeitfaktor_timer == 0:
                self.aktiver_zeitfaktor = 1.0
    
    def gravitation_aktualisieren(self):
        """Aktualisiert die Gravitationsrichtung"""
        if self.gravitation_timer > 0:
            self.gravitation_timer -= 1
            
            # Wenn Timer abgelaufen, zurück zur normalen Gravitation
            if self.gravitation_timer == 0:
                self.gravitation_richtung = 0
    
    def gravitation_anwenden(self):
        """Wendet die aktuelle Gravitationsrichtung an"""
        if not self.aktuelles_tetromino or not self.spiel_aktiv or self.pause:
            return
            
        if self.gravitation_richtung == 0:  # Nach unten
            self.tetromino_bewegen(0, 1)
        elif self.gravitation_richtung == 1:  # Nach rechts
            self.tetromino_bewegen(1, 0)
        elif self.gravitation_richtung == 2:  # Nach links
            self.tetromino_bewegen(-1, 0)
    
    def kollision_pruefen(self, dx, dy, tetromino):
        """Prüft, ob das Tetromino mit dem Spielfeld oder dem Rand kollidieren würde"""
        if not tetromino:
            return False
            
        for i, zeile in enumerate(tetromino.form):
            for j, zelle in enumerate(zeile):
                if zelle == 'O':
                    x = tetromino.x + j + dx
                    y = tetromino.y + i + dy
                    
                    # Außerhalb der Grenzen
                    if x < 0 or x >= SPALTEN or y >= ZEILEN:
                        return True
                    
                    # Kollision mit einem bereits platzierten Block
                    if y >= 0 and self.spielfeld[y][x] != 0:
                        return True
        
        return False
    
    def update(self):
        """Aktualisiert den Spielzustand"""
        if not self.spiel_aktiv or self.pause:
            return
        
        try:    
            # Zeitfaktor aktualisieren
            self.zeitfaktor_aktualisieren()
            
            # Gravitationsrichtung aktualisieren
            self.gravitation_aktualisieren()
            
            # Automatisches Fallen
            jetzt = time.time()
            if self.automatisch_fallen and jetzt - self.letzte_fallzeit > self.fallzeit * self.aktiver_zeitfaktor:
                self.letzte_fallzeit = jetzt
                self.gravitation_anwenden()
        except Exception as e:
            print(f"Fehler in update: {e}")
    
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
                
    def zeichne_ui(self, screen):
        """Zeichnet die Benutzeroberfläche (Punktzahl, Level, usw.)"""
        # Spielinformationen
        info_x = SPIELFELD_X + SPALTEN * BLOCK_GROESSE + 30
        info_y = SPIELFELD_Y + 200
        
        # Fonts
        font = pygame.font.SysFont("Arial", 24)
        
        # Score
        score_text = font.render(f"Punkte: {self.score}", True, WEISS)
        screen.blit(score_text, (info_x, info_y))
        
        # Level
        level_text = font.render(f"Level: {self.level}", True, WEISS)
        screen.blit(level_text, (info_x, info_y + 40))
        
        # Linien
        linien_text = font.render(f"Linien: {self.linien}", True, WEISS)
        screen.blit(linien_text, (info_x, info_y + 80))
        
        # Aktive Gimmick-Effekte
        aktiv_y = info_y + 140
        
        if self.zeitfaktor_timer > 0:
            if self.aktiver_zeitfaktor > 1.0:
                zeit_text = font.render("Zeitlupe aktiv!", True, (255, 215, 0))
                screen.blit(zeit_text, (info_x, aktiv_y))
                aktiv_y += 30
            elif self.aktiver_zeitfaktor < 1.0:
                zeit_text = font.render("Zeitraffer aktiv!", True, (255, 0, 255))
                screen.blit(zeit_text, (info_x, aktiv_y))
                aktiv_y += 30
                
        if self.gravitation_timer > 0:
            if self.gravitation_richtung == 1:
                grav_text = font.render("Gravitation: Rechts", True, (255, 105, 180))
                screen.blit(grav_text, (info_x, aktiv_y))
                aktiv_y += 30
            elif self.gravitation_richtung == 2:
                grav_text = font.render("Gravitation: Links", True, (255, 105, 180))
                screen.blit(grav_text, (info_x, aktiv_y))
                aktiv_y += 30
        
        # Game Over Anzeige
        if not self.spiel_aktiv:
            font_gross = pygame.font.SysFont("Arial", 48)
            gameover_text = font_gross.render("GAME OVER", True, (255, 0, 0))
            text_rect = gameover_text.get_rect(center=(SPIELFELD_X + SPALTEN * BLOCK_GROESSE // 2, 
                                                      SPIELFELD_Y + ZEILEN * BLOCK_GROESSE // 2))
            screen.blit(gameover_text, text_rect)
            
            font_klein = pygame.font.SysFont("Arial", 24)
            neustart_text = font_klein.render("Drücke R zum Neustart", True, WEISS)
            neustart_rect = neustart_text.get_rect(center=(SPIELFELD_X + SPALTEN * BLOCK_GROESSE // 2, 
                                                          text_rect.bottom + 30))
            screen.blit(neustart_text, neustart_rect)
        
        # Pause Anzeige
        if self.pause:
            font_gross = pygame.font.SysFont("Arial", 48)
            pause_text = font_gross.render("PAUSE", True, WEISS)
            text_rect = pause_text.get_rect(center=(SPIELFELD_X + SPALTEN * BLOCK_GROESSE // 2, 
                                                   SPIELFELD_Y + ZEILEN * BLOCK_GROESSE // 2))
            screen.blit(pause_text, text_rect)
    
    def neustart(self):
        """Startet das Spiel neu"""
        self.__init__()  # Initialisiert ein neues Spiel
    
    def pause_toggle(self):
        """Schaltet die Pause ein/aus"""
        self.pause = not self.pause 