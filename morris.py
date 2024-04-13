import pygame
from openingHelper import *
from gameHelper import *
from time import sleep
import subprocess as sb

pygame.init()

screen = pygame.display.set_mode((500, 630))

pygame.display.set_caption("Nine Men Morris")

#images
boardImg = pygame.image.load('static/morrisSmall.png')
leafImg = pygame.image.load('static/green1.png')
fireImg = pygame.image.load('static/fire1.png')
highImg = pygame.image.load('static/high.png')
roboImg = pygame.image.load('static/robo1.png')

coords = {
	0: (70, 720, 120, 770),
	1: (770, 720, 820, 770),
	2: (180, 610, 230, 660),
	3: (660, 610, 710, 660),
	4: (300, 490, 350, 540),
	5: (540, 490, 590, 540),
	6: (70, 375, 120, 425),
	7: (180, 375, 230, 425),
	8: (300, 375, 350, 425),
	9: (540, 375, 590, 425),
	10: (660, 375, 710, 425),
	11: (770, 375, 820, 425),
	12: (300, 260, 350, 310),
	13: (420, 260, 470, 310),
	14: (540, 260, 590, 310),
	15: (180, 140, 230, 190),
	16: (420, 140, 470, 190),
	17: (660, 140, 710, 190),  
	18: (70, 30, 120, 80),
	19: (420, 30, 470, 80),
	20: (770, 30, 820, 80)
}

mul = 500/843

clickables = [pygame.Rect(mul*c[0], mul*c[1], 35, 35) for c in coords.values()]

board = list('xxxxxxxxxxxxxxxxxxxxx')

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

openingText = Font.render("OPENING PHASE", False, (0,0,0))
middleGameText = Font.render("MIDDLE GAME", False, (0,0,0))
endgameText = Font.render("ENDGAME", False, (0,0,0))
overText = Font.render("END!", False, (0,0,0))
waitText = roboFont.render(" : Ok, let me think . . . . . . . .", False, (0,0,0))
millText = roboFont.render(" : Ah! Mill! Go ahead and remove my piece", False, (0,0,0))
openingRobo = roboFont.render(" : Place a piece on any empty vertice", False, (0,0,0))
middleRobo = roboFont.render(" : Click on your piece and move to an adjacent spot", False, (0,0,0))
endGameRobo = roboFont.render(" : Click on your piece and move to any spot", False, (0,0,0))
overRobo1 = roboFont.render(" : I accept my defeat. GG. Press R to restart", False, (0,0,0))
overRobo2 = roboFont.render(" : As expected. GG. Press R to restart", False, (0,0,0))
winningRobo = roboFont.render(" : I am winning this easily.", False, (255,0,0))
losingRobo = roboFont.render(" : Ah, you might actually win this.", False, (0,255,0))
drawingRobo = roboFont.render(" : This could be a draw", False, (0,0,255))

text_rect = openingText.get_rect(center=(250, 510))

selectMove = False
availableShifts = []
endGame = False
gameComplete = 0


fps = 20
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
					screen.blit(highImg,(x, y))

		else:
			n = Game.neighbors[moveLoc]
			availableShifts = []
			for j in n:
				if board[j] == 'x':
					availableShifts.append(j)
					x = mul*coords[j][0] - 5
					y = mul*coords[j][1] - 5
					screen.blit(highImg,(x, y))		


	if mill:
		cnt = 0
		for loc in range(len(board)):
			if board[loc] == 'W':
				if not Game.closeMill(loc, board):
					x = mul*coords[loc][0] - 5
					y = mul*coords[loc][1] - 5
					screen.blit(highImg,(x, y))
					cnt += 1
		if cnt == 0:
			moveLoc = None
			mill = False

	
	for loc in range(len(board)):
		if board[loc] == 'W':
			x = mul*coords[loc][0]
			y = mul*coords[loc][1]
			screen.blit(fireImg,(x, y))
		if board[loc] == 'B':
			x = mul*coords[loc][0]
			y = mul*coords[loc][1]
			screen.blit(leafImg,(x, y))


def drawText():
	screen.blit(roboImg, (10, 540))
	
	if gameComplete == 1:
		screen.blit(overText, text_rect)
		screen.blit(overRobo1, (50, 550))
	if gameComplete == -1:
		screen.blit(overText, text_rect)
		screen.blit(overRobo2, (50, 550))

	else:
		if turn <= 18:
			screen.blit(openingText, text_rect)
		elif endGame:
			screen.blit(endgameText, text_rect)
		else:
			screen.blit(middleGameText, text_rect)

		if played and (not mill):
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
	screen.fill((255, 255, 255))
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

		


