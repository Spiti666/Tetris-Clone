"""
Tetris-Klon mit Pygame
Steuerung:
- WASD: Tetromino bewegen/drehen
  - A: Nach links bewegen
  - D: Nach rechts bewegen
  - S: Schneller fallen
  - W: Sofort fallen lassen (Hard Drop)
- Leertaste: Tetromino drehen
- P: Pause
- R: Neustart
- ESC: Zurück zum Hauptmenü (mit Bestätigungsdialog)
- J/N: Bestätigen/Abbrechen in Dialogen

Navigation:
- Hauptmenü -> Spiel: Beliebige Taste drücken
- Spiel -> Hauptmenü: ESC drücken und Bestätigung mit J
"""

import pygame
import sys
import time
import traceback
import random
from config import BREITE, HOEHE, UI_HINTERGRUND, UI_TEXT, UI_AKZENT, ZEILEN
from game import TetrisSpiel

def zeige_bestaetigung(screen, frage):
    """Zeigt einen Bestätigungsdialog an und gibt True oder False zurück"""
    try:
        # Schriftarten
        try:
            titel_font = pygame.font.Font(None, 36)
            text_font = pygame.font.Font(None, 28)
        except:
            titel_font = pygame.font.SysFont("Arial", 36, bold=True)
            text_font = pygame.font.SysFont("Arial", 28)
        
        # Halbdurchsichtiger Hintergrund für den Dialog
        overlay = pygame.Surface((BREITE, HOEHE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Schwarzer Hintergrund mit 70% Transparenz
        screen.blit(overlay, (0, 0))
        
        # Dialog-Box
        dialog_breite = 500
        dialog_hoehe = 200
        dialog_x = (BREITE - dialog_breite) // 2
        dialog_y = (HOEHE - dialog_hoehe) // 2
        
        # Dialog-Hintergrund mit Schatten
        pygame.draw.rect(screen, (30, 30, 40), 
                       (dialog_x + 5, dialog_y + 5, dialog_breite, dialog_hoehe))
        pygame.draw.rect(screen, (60, 60, 80), 
                       (dialog_x, dialog_y, dialog_breite, dialog_hoehe))
        pygame.draw.rect(screen, (40, 40, 60), 
                       (dialog_x, dialog_y, dialog_breite, dialog_hoehe), 2)
        
        # Frage rendern
        frage_text = titel_font.render(frage, True, (255, 255, 255))
        frage_rect = frage_text.get_rect(center=(BREITE // 2, dialog_y + 50))
        screen.blit(frage_text, frage_rect)
        
        # Optionen
        ja_text = text_font.render("Ja (J)", True, (255, 255, 100))
        ja_rect = ja_text.get_rect(center=(BREITE // 2 - 80, dialog_y + 120))
        screen.blit(ja_text, ja_rect)
        
        nein_text = text_font.render("Nein (N)", True, (255, 255, 100))
        nein_rect = nein_text.get_rect(center=(BREITE // 2 + 80, dialog_y + 120))
        screen.blit(nein_text, nein_rect)
        
        # Anweisungen
        anweisung_text = text_font.render("Drücke J für Ja oder N für Nein", True, (200, 200, 200))
        anweisung_rect = anweisung_text.get_rect(center=(BREITE // 2, dialog_y + 160))
        screen.blit(anweisung_text, anweisung_rect)
        
        # Bildschirm aktualisieren
        pygame.display.flip()
        
        # Auf Antwort warten
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True  # Beenden, wenn Fenster geschlossen wird
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_j:  # J-Taste für Ja
                        return True
                    elif event.key == pygame.K_n:  # N-Taste für Nein
                        return False
                    elif event.key == pygame.K_ESCAPE:  # ESC zum Abbrechen
                        return False
            
            # Kleine Pause
            pygame.time.delay(30)
            
    except Exception as e:
        print(f"Fehler im Bestätigungsdialog: {e}")
        traceback.print_exc()
        return False  # Im Fehlerfall nicht beenden

def main():
    """Hauptfunktion des Spiels"""
    try:
        # Pygame initialisieren
        pygame.init()
        
        # Prüfen, ob Pygame erfolgreich initialisiert wurde
        if pygame.get_error() != "":
            print(f"Pygame Initialisierungsfehler: {pygame.get_error()}")
        
        # Bildschirmmodus setzen
        try:
            screen = pygame.display.set_mode((BREITE, HOEHE))
        except pygame.error as e:
            print(f"Fehler beim Setzen des Bildschirmmodus: {e}")
            return
            
        pygame.display.set_caption("Tetris mit Gimmicks")
        
        # Prüfen ob Schriftarten verfügbar sind
        system_fonts = pygame.font.get_fonts()
        if "arial" not in system_fonts:
            print("Warnung: Arial-Schriftart nicht gefunden, verwende Systemstandard")
        
        # Uhr für FPS-Begrenzung
        clock = pygame.time.Clock()
        
        # Hauptspielschleife
        spiel_laeuft = True
        while spiel_laeuft:
            # Anfangsbildschirm anzeigen
            print("Zeige Startbildschirm...")
            start_game = zeige_startbildschirm(screen)
            if not start_game:
                print("Spiel im Startbildschirm beendet")
                break
                
            print("Startbildschirm verlassen, starte Spiel...")
                
            # Tastaturwiederholrate setzen (für schnellere Bewegung bei gedrückter Taste)
            pygame.key.set_repeat(150, 50)
            
            # Spielobjekt erstellen
            spiel = TetrisSpiel()
            
            # Spielschleife
            running = True
            last_frame_time = time.time()
            
            while running:
                try:
                    current_time = time.time()
                    frame_time = current_time - last_frame_time
                    last_frame_time = current_time
                    
                    # Überprüfen, ob das Spiel zu langsam läuft
                    if frame_time > 0.1:  # Mehr als 100ms pro Frame
                        print(f"Warnung: Langsames Frame ({frame_time*1000:.2f}ms)")
                    
                    # Ereignisse verarbeiten
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            # Fenster schließen ohne Nachfrage
                            running = False
                            spiel_laeuft = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                # Sicherheitsabfrage anzeigen
                                if zeige_bestaetigung(screen, "Zum Hauptmenü zurückkehren?"):
                                    running = False  # Beendet nur die aktuelle Spielschleife
                                    # spiel_laeuft bleibt true, damit wir zum Hauptmenü zurückkehren
                            elif event.key == pygame.K_p:
                                spiel.pause_toggle()
                            elif event.key == pygame.K_r:
                                spiel.neustart()
                            
                            # Spielsteuerung (nur wenn nicht pausiert und aktiv)
                            if spiel.spiel_aktiv and not spiel.pause:
                                if event.key == pygame.K_a:
                                    spiel.tetromino_bewegen(-1, 0)
                                elif event.key == pygame.K_d:
                                    spiel.tetromino_bewegen(1, 0)
                                elif event.key == pygame.K_s:
                                    spiel.tetromino_bewegen(0, 1)
                                elif event.key == pygame.K_SPACE:
                                    spiel.tetromino_rotieren()
                                elif event.key == pygame.K_w:
                                    # Hard Drop - lässt das Tetromino sofort fallen
                                    # Finde zuerst heraus, wie weit das Tetromino fallen kann
                                    max_drops = ZEILEN  # Maximale mögliche Fallhöhe
                                    drops = 0
                                    
                                    # Speichere die aktuelle Position
                                    original_y = spiel.aktuelles_tetromino.y
                                    
                                    # Simuliere das Fallen, ohne tatsächlich zu bewegen
                                    while not spiel.kollision_pruefen(0, drops + 1, spiel.aktuelles_tetromino) and drops < max_drops:
                                        drops += 1
                                    
                                    # Wenn wir eine gültige Fallhöhe gefunden haben, setze das Tetromino dorthin
                                    if drops > 0:
                                        # Setze direkt auf die finale Position
                                        spiel.aktuelles_tetromino.y += drops
                                        
                                        # Füge das Tetromino dem Spielfeld hinzu
                                        spiel.tetromino_fixieren()
                                        
                                        # Kleine Verzögerung, damit der Spieler sehen kann, was passiert ist
                                        pygame.time.delay(50)
                            
                    # Spiellogik aktualisieren
                    spiel.update()
                    
                    # Bildschirm zeichnen
                    screen.fill(UI_HINTERGRUND)
                    spiel.spielfeld_zeichnen(screen)
                    spiel.zeichne_ui(screen)
                    
                    # Bildschirm aktualisieren
                    pygame.display.flip()
                    
                    # FPS begrenzen und kleinen Delay einbauen
                    # Um sicherzustellen, dass die Hauptschleife nicht zu viel CPU-Zeit beansprucht
                    clock.tick(60)
                    
                except Exception as e:
                    # Bei Fehlern Traceback ausgeben und weitermachen
                    print(f"Fehler in der Hauptschleife: {e}")
                    traceback.print_exc()
                    pygame.time.delay(100)  # Kurze Pause, um CPU-Last zu reduzieren bei Fehlern
            
            # Hier endet die Spielschleife, aber die Hauptschleife könnte weiterlaufen
            # (wenn wir zum Hauptmenü zurückkehren wollen)
                
    except Exception as e:
        print(f"Kritischer Fehler: {e}")
        traceback.print_exc()
    finally:
        # Pygame ordnungsgemäß beenden
        pygame.quit()
        sys.exit()

def zeige_startbildschirm(screen):
    """Zeigt den Startbildschirm an"""
    try:
        # Konstanten für das Design
        GRADIENT_TOP = (30, 30, 60)     # Dunkelblau oben
        GRADIENT_BOTTOM = (10, 10, 30)  # Fast schwarz unten
        HIGHLIGHT_COLOR = (100, 255, 200)  # Neon-Grün
        TITLE_COLOR = (255, 255, 100)  # Helles Gelb
        SHADOW_COLOR = (0, 0, 20)  # Dunkler Schatten
        
        # Rotation für animierte Blöcke
        rotation = 0
        
        # Sicherstellen, dass UI_AKZENT ein RGB-Tupel ist
        default_colors = [
            (0, 200, 200),    # Cyan
            (200, 0, 200),    # Magenta
            (200, 200, 0),    # Gelb
            (0, 200, 0),      # Grün
            (200, 0, 0),      # Rot
            (0, 0, 200)       # Blau
        ]
        
        # Fallende Tetris-Blöcke für Animationseffekt
        tetris_blöcke = []
        for _ in range(10):
            x = random.randint(0, BREITE)
            y = random.randint(-HOEHE, 0)
            größe = random.randint(20, 60)
            
            # Sichere Farbauswahl
            try:
                # Prüfe ob UI_AKZENT ein einzelner Int-Wert ist oder ein RGB-Tupel
                if isinstance(UI_AKZENT, (list, tuple)):
                    # Prüfe, ob es ein RGB-Tupel oder eine Liste von Farben ist
                    if len(UI_AKZENT) == 3 and all(isinstance(c, int) for c in UI_AKZENT):
                        # Es ist ein einzelnes RGB-Tupel
                        farbe = UI_AKZENT
                    else:
                        # Es ist eine Liste von Farben
                        farbe_idx = random.randint(0, len(UI_AKZENT)-1)
                        farbe = UI_AKZENT[farbe_idx]
                else:
                    # Fallback zu Standardfarben
                    farbe = random.choice(default_colors)
            except:
                # Bei Problemen verwende eine Standardfarbe
                farbe = random.choice(default_colors)
                
            if not isinstance(farbe, (list, tuple)) or len(farbe) != 3:
                farbe = random.choice(default_colors)
                
            geschwindigkeit = random.uniform(1.0, 3.0)
            rotation_speed = random.uniform(-2.0, 2.0)
            tetris_blöcke.append({
                'x': x, 'y': y, 'größe': größe, 'farbe': farbe,
                'geschwindigkeit': geschwindigkeit, 'rotation': 0,
                'rotation_speed': rotation_speed
            })
            
        # Schriftarten für verschiedene Elemente
        try:
            title_font = pygame.font.Font(None, 100)  # Pygame-Standardschriftart
            subtitle_font = pygame.font.Font(None, 50)
            menu_font = pygame.font.Font(None, 36)
            small_font = pygame.font.Font(None, 24)
        except Exception as e:
            print(f"Fehler beim Laden der Schriften: {e}")
            # Fallback auf SysFont
            title_font = pygame.font.SysFont("Arial", 100, bold=True)
            subtitle_font = pygame.font.SysFont("Arial", 50, bold=True)
            menu_font = pygame.font.SysFont("Arial", 36)
            small_font = pygame.font.SysFont("Arial", 24)
        
        # Event-Queue leeren (wichtig!)
        pygame.event.clear()
        
        # Auf Tastendruck warten mit Timeout
        waiting = True
        start_time = time.time()
        MAX_WAIT_TIME = 120  # Maximale Wartezeit in Sekunden
        last_update_time = start_time
        
        # Animationszyklus
        pulse = 0
        pulse_direction = 1
        
        while waiting and time.time() - start_time < MAX_WAIT_TIME:
            current_time = time.time()
            delta_time = current_time - last_update_time
            last_update_time = current_time
            
            # Steuerung der Pulsanimation
            pulse += 0.02 * pulse_direction
            if pulse >= 1.0:
                pulse_direction = -1
            elif pulse <= 0.0:
                pulse_direction = 1
            
            # Animiere die Tetrisblöcke
            for block in tetris_blöcke:
                block['y'] += block['geschwindigkeit']
                block['rotation'] += block['rotation_speed']
                if block['y'] > HOEHE + 50:
                    block['y'] = random.randint(-100, -20)
                    block['x'] = random.randint(0, BREITE)
            
            # Event-Verarbeitung - verbessert
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quit-Event erkannt im Startmenü")
                    return False
                elif event.type == pygame.KEYDOWN:
                    print(f"Tastendruck erkannt im Startmenü: {event.key}")
                    if event.key == pygame.K_ESCAPE:
                        return False
                    else:
                        return True
            
            # Zeichne Farbverlauf-Hintergrund
            for y in range(0, HOEHE, 2):
                progress = y / HOEHE
                r = GRADIENT_TOP[0] + int((GRADIENT_BOTTOM[0] - GRADIENT_TOP[0]) * progress)
                g = GRADIENT_TOP[1] + int((GRADIENT_BOTTOM[1] - GRADIENT_TOP[1]) * progress)
                b = GRADIENT_TOP[2] + int((GRADIENT_BOTTOM[2] - GRADIENT_TOP[2]) * progress)
                pygame.draw.line(screen, (r, g, b), (0, y), (BREITE, y), 2)
            
            # Zeichne animierte Tetris-Blöcke im Hintergrund
            for block in tetris_blöcke:
                # Zeichne einen rotierten Block
                surface = pygame.Surface((block['größe'], block['größe']), pygame.SRCALPHA)
                # Sicheres Zeichnen mit Fehlerprüfung für die Farbe
                try:
                    farbe = block['farbe']
                    # Stellen sicher, dass 'farbe' ein RGB-Tupel ist
                    if isinstance(farbe, (list, tuple)) and len(farbe) == 3:
                        pygame.draw.rect(surface, (farbe[0], farbe[1], farbe[2], 100), 
                                      (0, 0, block['größe'], block['größe']))
                        
                        # 3D-Effekt
                        pygame.draw.line(surface, (farbe[0], farbe[1], farbe[2], 150), 
                                       (0, 0), (block['größe'], 0), 3)
                        pygame.draw.line(surface, (farbe[0], farbe[1], farbe[2], 150), 
                                       (0, 0), (0, block['größe']), 3)
                        pygame.draw.line(surface, (farbe[0], farbe[1], farbe[2], 50), 
                                       (block['größe'], 0), (block['größe'], block['größe']), 3)
                        pygame.draw.line(surface, (farbe[0], farbe[1], farbe[2], 50), 
                                       (0, block['größe']), (block['größe'], block['größe']), 3)
                except Exception as e:
                    print(f"Fehler beim Zeichnen eines Blocks: {e}, Farbe: {block['farbe']}")
                    # Fallback zu einer sicheren Farbe
                    pygame.draw.rect(surface, (100, 100, 100, 100), 
                                  (0, 0, block['größe'], block['größe']))
                
                # Rotiere den Block
                rotated_surface = pygame.transform.rotate(surface, block['rotation'])
                new_rect = rotated_surface.get_rect(center=(block['x'], block['y']))
                screen.blit(rotated_surface, new_rect.topleft)
            
            # Titel mit Schatten
            title_shadow = title_font.render("TETRIS", True, SHADOW_COLOR)
            title_text = title_font.render("TETRIS", True, TITLE_COLOR)
            title_rect = title_text.get_rect(center=(BREITE // 2, 120))
            
            # Pulsierender Effekt für den Titel
            title_scale = 1.0 + pulse * 0.05
            scaled_title = pygame.transform.scale(title_text, 
                                               (int(title_text.get_width() * title_scale),
                                                int(title_text.get_height() * title_scale)))
            scaled_rect = scaled_title.get_rect(center=(BREITE // 2, 120))
            
            # Zeichne Schatten und dann den Titel
            screen.blit(title_shadow, (title_rect.x + 5, title_rect.y + 5))
            screen.blit(scaled_title, scaled_rect)
            
            # Untertitel mit Glühen - sichere Version
            subtitle_color = (100, 200, 255)  # Standardfarbe
            if isinstance(UI_AKZENT, (list, tuple)) and len(UI_AKZENT) == 3:
                # Sicherstellen, dass UI_AKZENT ein RGB-Tupel ist
                r = int(UI_AKZENT[0] * (0.7 + 0.3 * pulse))
                g = int(UI_AKZENT[1] * (0.7 + 0.3 * pulse))
                b = int(UI_AKZENT[2] * (0.7 + 0.3 * pulse))
                subtitle_color = (r, g, b)
                
            subtitle_text = subtitle_font.render("mit Gimmicks", True, subtitle_color)
            subtitle_rect = subtitle_text.get_rect(center=(BREITE // 2, 190))
            screen.blit(subtitle_text, subtitle_rect)
            
            # Hintergrund für Menüoptionen
            menu_background = pygame.Surface((BREITE - 200, 280), pygame.SRCALPHA)
            menu_background.fill((30, 30, 50, 180))
            screen.blit(menu_background, (100, 250))
            
            # Steuerungshinweise
            info_texte = [
                "Steuerung:",
                "A: Nach links bewegen",
                "D: Nach rechts bewegen", 
                "S: Schneller fallen",
                "W: Sofort fallen lassen (Hard Drop)",
                "Leertaste: Tetromino drehen",
                "P: Pause",
                "R: Neustart",
                "ESC: Beenden"
            ]
            
            # Zeichne Steuerungshinweise
            y_pos = 280
            for i, text in enumerate(info_texte):
                # Hervorhebung für den Titel "Steuerung:"
                if i == 0:
                    info_render = menu_font.render(text, True, HIGHLIGHT_COLOR)
                    y_pos += 10  # Zusätzlicher Abstand vor dem Titel
                else:
                    info_render = small_font.render(text, True, UI_TEXT)
                
                info_rect = info_render.get_rect(center=(BREITE // 2, y_pos))
                screen.blit(info_render, info_rect)
                y_pos += 28
            
            # Start-Hinweis mit Pulsieren
            y_pos = HOEHE - 100
            
            start_color = (
                int(255 * (0.7 + 0.3 * pulse)),
                int(255 * (0.7 + 0.3 * pulse)),
                100
            )
            start_text = menu_font.render("Drücke eine beliebige Taste zum Starten", True, start_color)
            start_rect = start_text.get_rect(center=(BREITE // 2, y_pos))
            screen.blit(start_text, start_rect)
            
            # Unterer Bereich mit Farbverlauf
            gradient_surface = pygame.Surface((BREITE, 70), pygame.SRCALPHA)
            for line in range(70):
                alpha = int(150 * (line / 70))
                pygame.draw.line(gradient_surface, (0, 0, 0, alpha), (0, line), (BREITE, line))
            screen.blit(gradient_surface, (0, HOEHE - 70))
            
            # Copyright
            copyright_text = small_font.render("© 2025 - Tetris-Klon", True, (180, 180, 180))
            copyright_rect = copyright_text.get_rect(center=(BREITE // 2, HOEHE - 30))
            screen.blit(copyright_text, copyright_rect)
            
            # Bildschirm aktualisieren
            pygame.display.flip()
            
            # Kleine Pause, um CPU-Last zu reduzieren
            pygame.time.delay(30)
        
        # Falls Timeout erreicht wurde
        if time.time() - start_time >= MAX_WAIT_TIME:
            print("Timeout beim Warten auf Tastendruck im Startbildschirm")
            return True  # Starte trotzdem das Spiel
            
        return True
        
    except Exception as e:
        print(f"Fehler im Startbildschirm: {e}")
        traceback.print_exc()
        return True  # Versuche trotz Fehler das Spiel zu starten

if __name__ == "__main__":
    try:
        print("Starte Tetris-Spiel...")
        main()
    except Exception as e:
        print(f"Fehler beim Starten des Spiels: {e}")
        traceback.print_exc()
        input("Drücke Enter zum Beenden...")  # Hält die Konsole offen bei Fehlern 