import pygame
import sys
import subprocess

def load_background():
    # Chargez l'image de fond depuis le dossier assets
    background_image = pygame.image.load('assets/menubackground.jpg')
    # Redimensionnez l'image pour qu'elle s'adapte à la fenêtre de 800x600
    background_image = pygame.transform.scale(background_image, (800, 600))
    return background_image

def draw_menu(screen, background_image):
    # Utilisez l'image de fond pour l'arrière-plan
    screen.blit(background_image, (0, 0))
    
    font = pygame.font.Font(None, 36)
    text_jvj = font.render('Joueur vs Joueur', True, (0, 0, 0))
    text_jvr = font.render('vs Robot', True, (0, 0, 0))
    text_quit = font.render('Quitter', True, (0, 0, 0))
    
    # Définissez la couleur de fond pour les boutons
    button_color = (181, 255, 233)
    padding = 10  # Espacement autour du texte
    
    # Créez des rectangles pour le fond des textes
    text_jvj_rect = text_jvj.get_rect(center=(400, 200))
    text_jvr_rect = text_jvr.get_rect(center=(400, 300))
    text_quit_rect = text_quit.get_rect(center=(400, 400))
    
    # Ajustez les rectangles pour ajouter du padding
    text_jvj_rect.inflate_ip(padding * 2, padding)
    text_jvr_rect.inflate_ip(padding * 2, padding)
    text_quit_rect.inflate_ip(padding * 2, padding)
    
    # Dessinez les rectangles de fond
    pygame.draw.rect(screen, button_color, text_jvj_rect)
    pygame.draw.rect(screen, button_color, text_jvr_rect)
    pygame.draw.rect(screen, button_color, text_quit_rect)
    
    # Redessinez les textes sur les rectangles
    screen.blit(text_jvj, text_jvj.get_rect(center=text_jvj_rect.center))
    screen.blit(text_jvr, text_jvr.get_rect(center=text_jvr_rect.center))
    screen.blit(text_quit, text_quit.get_rect(center=text_quit_rect.center))
    
    return text_jvj_rect, text_jvr_rect, text_quit_rect

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Menu Principal")
    
    background_image = load_background()
    menu_items = draw_menu(screen, background_image)
    pygame.display.flip()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_items[1].collidepoint(event.pos):
                    subprocess.run(['dist/morris.exe'])
                elif menu_items[0].collidepoint(event.pos):
                    # Cela suppose que vous avez une fonction pour lancer le jeu Joueur vs Joueur
                    pass
                elif menu_items[2].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


if __name__ == '__main__':
    main_menu()
