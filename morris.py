import pygame
from openingHelper import *
from gameHelper import *
from time import sleep
import subprocess as sb

pygame.init()

screen = pygame.display.set_mode((500, 630))

pygame.display.set_caption("Jeu du Moulin")

#images
boardImg = pygame.image.load('assets/plateau.jpg')
player1 = pygame.image.load('assets/whiteplayer.png')
player2 = pygame.image.load('assets/orangeplayer.png')
circle = pygame.image.load('assets/greencircle.png')
roboImg = pygame.image.load('assets/Robot_icon.png')

player1 = pygame.transform.scale(player1, (30, 30))
player2 = pygame.transform.scale(player2, (30, 30))
circle = pygame.transform.scale(circle, (40, 40))
roboImg = pygame.transform.scale(roboImg, (30, 30))

coords = {
    0: (70, 720, 120, 770),
	1: (420, 720, 470, 770),
	2: (770, 720, 820, 770),
	3: (180, 610, 230, 660),
	4: (420, 610, 470, 660),
	5: (660, 610, 710, 660),
	6: (300, 490, 350, 540),
	7: (420, 490, 470, 540),
	8: (540, 490, 590, 540),
	9: (70, 375, 120, 425),
	10: (180, 375, 230, 425),
	11 : (300, 375, 350, 425),
	12: (540, 375, 590, 425),
	13: (660, 375, 710, 425),
	14: (770, 375, 820, 425),
	15: (300, 260, 350, 310),
	16: (420, 260, 470, 310),
	17: (540, 260, 590, 310),
	18: (180, 140, 230, 190),
	19: (420, 140, 470, 190),
	20: (660, 140, 710, 190),
	21: (70, 30, 120, 80),
	22: (420, 30, 470, 80),
	23: (770, 30, 820, 80)
}


mul = 500/843

clickables = [pygame.Rect(mul*c[0], mul*c[1], 35, 35) for c in coords.values()]

board = list('xxxxxxxxxxxxxxxxxxxxxxxx')

turn = 2
v = 0

running = True
mill = False
played = False
moveLoc = None

MAX = 50000

Game = MiniMaxOpening(9, turn)

Font = pygame.font.SysFont('Roboto Mono',  30)
roboFont = pygame.font.SysFont('Roboto Mono',  25)

openingText = Font.render("PHASE D'OUVERTURE", False, (0,0,0))
middleGameText = Font.render("JEU MOYEN", False, (0,0,0))
endgameText = Font.render("FIN DE PARTIE", False, (0,0,0))
overText = Font.render("FINI !", False, (0,0,0))
waitText = roboFont.render(" : Je consulte mon grille-pain interne… un instant !", False, (0,0,0))
millText = roboFont.render("Moulin réalisé ! S'il vous plaît, ôtez un pion.", False, (0,0,0))
openingRobo = roboFont.render("Je suis prêt. Posez donc un pion !", False, (0,0,0))
middleRobo = roboFont.render("Déplacez votre pion, j'observe...", False, (0,0,0))
endGameRobo = roboFont.render("Tout est permis, même bouger là-bas !", False, (0,0,0))
overRobo1 = roboFont.render("Défaite acceptée. Appuyez sur R pour ma revanche !", False, (0,0,0))
overRobo2 = roboFont.render("Victoire logique ! R pour recommencer ?", False, (0,0,0))
winningRobo = roboFont.render("Je vais gagner en trichant.", False, (255,0,0))
losingRobo = roboFont.render("Oups... Vous seriez pas un pro, vous ?", False, (0,255,0))
drawingRobo = roboFont.render("Un match nul ? Suspense...", False, (0,0,255))


text_rect = openingText.get_rect(center=(150, 520))

selectMove = False
availableShifts = []
endGame = False
gameComplete = 0

fps = 30
clock = pygame.time.Clock()

def checkEndgame():
	global endGame
	endGame = False
	cnt = 0
	for b in board:
		if b == 'B':
			cnt += 1
	if cnt == 3:
		endGame = True

def count_pieces(board):
    white_count = board.count('W')
    black_count = board.count('B')
    return white_count, black_count


def checkGameComplete():
	global gameComplete

	if turn > 18:
		cnt1, cnt2 = 0, 0
		for b in board:
			if b == 'B':
				cnt1 += 1
			if b == 'W':
				cnt2 += 1
		if cnt2 < 3:
			gameComplete = -1 
		if cnt1 < 3:
			gameComplete = 1

		Game = MiniMaxGame(3)
		
		if Game.GenerateMovesMidgameEndgame(board, True) == []:
			gameComplete = -1
		if Game.GenerateMovesMidgameEndgame(board) == []:
			gameComplete = 1


def drawBoard():
	global availableShifts, mill, moveLoc
	if selectMove:
		if endGame:
			availableShifts = []
			for loc in range(len(board)):
				if board[loc] == 'x':
					availableShifts.append(loc)
					x = mul*coords[loc][0] - 5
					y = mul*coords[loc][1] - 5
					screen.blit(circle,(x, y))

		else:
			n = Game.neighbors[moveLoc]
			availableShifts = []
			for j in n:
				if board[j] == 'x':
					availableShifts.append(j)
					x = mul*coords[j][0] - 5
					y = mul*coords[j][1] - 5
					screen.blit(circle,(x, y))		


	if mill:
		cnt = 0
		for loc in range(len(board)):
			if board[loc] == 'W':
				print("Loc et board[loc] : ", loc, board[loc])
				if not Game.closeMill(loc, board):
					x = mul*coords[loc][0] - 5
					y = mul*coords[loc][1] - 5
					screen.blit(circle,(x, y))
					cnt += 1
		if cnt == 0:
			moveLoc = None
			mill = False

	
	for loc in range(len(board)):
		if board[loc] == 'W':
			x = mul*coords[loc][0]
			y = mul*coords[loc][1]
			screen.blit(player1,(x, y))
		if board[loc] == 'B':
			x = mul*coords[loc][0]
			y = mul*coords[loc][1]
			screen.blit(player2,(x, y))


def drawText():
    screen.blit(roboImg, (10, 540))
    
    white_count, black_count = count_pieces(board)
    whiteText = roboFont.render(f"Blanc: {white_count} pions", False, (0,0,0))
    blackText = roboFont.render(f"Orange: {black_count} pions", False, (0,0,0))
    screen.blit(whiteText, (360, 500))  # Position en bas à droite pour le texte des Blancs
    screen.blit(blackText, (360, 520))  # Position en bas à droite des Noirs
    
    if gameComplete == 1:
        screen.blit(overText, text_rect)
        screen.blit(overRobo1, (50, 550))
    elif gameComplete == -1:
        screen.blit(overText, text_rect)
        screen.blit(overRobo2, (50, 550))
    else:
        if turn <= 18:
            screen.blit(openingText, text_rect)
        elif endGame:
            screen.blit(endgameText, text_rect)
        else:
            screen.blit(middleGameText, text_rect)

        if played and not mill:
            screen.blit(waitText, (50, 550))
        elif mill:
            screen.blit(millText, (50, 550))
        else:
            if turn <= 18:
                screen.blit(openingRobo, (50, 550))
            elif endGame:
                screen.blit(endGameRobo, (50, 550))
            elif not gameComplete:
                screen.blit(middleRobo, (50, 550))

            if turn >= 14:
                if v > 150:
                    screen.blit(winningRobo, (50, 590))
                elif v < -150:
                    screen.blit(losingRobo, (50, 590))
                else:
                    screen.blit(drawingRobo, (50, 590))


while running:
	screen.fill((0, 119, 182))
	screen.blit(boardImg, (0, 0))
	checkEndgame()
	checkGameComplete()
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		# opening
		if (not mill) and turn <= 18 and event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:  # Left mouse button.
				# Check if the rect collides with the mouse pos.
				for i, area in enumerate(clickables):
					if area.collidepoint(event.pos):
						print("Coordonnées de la case cliquée : ", i) # Affiche les coordonnées de la case cliquée
						print("Contenu de la case cliquée : ", board[i]) # Affiche le contenu de la case cliquée
						board[i] = 'B'
						played = True
						moveLoc = i
		
		# midgame
		if selectMove and turn > 18 and event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:  # Left mouse button.
				# Check if the rect collides with the mouse pos.
				for i, area in enumerate(clickables):
					if area.collidepoint(event.pos):
						if i in availableShifts:
							board[i] = 'B'
							board[moveLoc] = 'x'
							played = True
							turn += 2
							moveLoc = i
							selectMove = False


		if (not played) and (not mill) and turn > 18 and event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:  # Left mouse button.
				# Check if the rect collides with the mouse pos.
				for i, area in enumerate(clickables):
					if area.collidepoint(event.pos):
						if board[i] == 'B':
							turn += 2
							moveLoc = i
							selectMove = True
		
		
		# mill logic
		if mill and event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:  # Left mouse button.
				# Check if the rect collides with the mouse pos.
				for i, area in enumerate(clickables):
					if area.collidepoint(event.pos):
						if board[i] == 'W':
							board[i] = 'x'
							mill = False
							moveLoc = None

		# restart logic
		if gameComplete != 0 and event.type == pygame.KEYDOWN:
			if event.key == pygame.K_r:
				gameComplete = False
				played = False
				board = list('xxxxxxxxxxxxxxxxxxxxx')
				moveLoc = None
				turn = 2

	drawBoard()
	drawText()
	
	pygame.display.update()
	clock.tick(fps)


	if played and (not mill) and (not selectMove):
		print("Board : ", board)
		if moveLoc and Game.closeMill(moveLoc, board):
			#print('Mill! remove opponent piece.')
			mill = True
			continue

	if turn <= 18 and (not mill) and played:
		Game = MiniMaxOpening(7, turn)


		root = Node(board, turn)
		v = Game.MaxMin(root, -MAX, MAX)
		#print(v, turn)
		board = Game.bestResponse
		played = False
		turn += 2

	if turn >= 18 and (not mill) and (not selectMove) and played:
		if endGame:
			Game = MiniMaxGame(4)
		else:
			Game = MiniMaxGame(5)
		
		root = Node(board, 0)
		v = Game.MaxMin(root, -MAX, MAX)
		
		if v == float('inf'):
			#print('inf detected')
			Game = MiniMaxGame(3)
			root = Node(board, 0)
			v = Game.MaxMin(root, -MAX, MAX)
		
		#print(v, turn)
		board = Game.bestResponse
		played = False
		turn += 2

		


