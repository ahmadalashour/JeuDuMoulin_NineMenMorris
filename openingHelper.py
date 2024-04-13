import sys

class Node:
	def __init__(self, board, depth):
		self.position = board
		self.depth = depth
		self.code = ''.join(board)


class MiniMaxOpening:
	def __init__(self, maxDepth, currDepth):
		self.evaluatedPositions = 0
		self.bestResponse = None
		self.currDepth = currDepth
		self.maxDepth = currDepth + maxDepth

		self.neighbors = {
			0: [1, 2, 6],
			1: [0, 11],
			2: [0, 4, 7, 3],
			3: [2, 10],
			4: [2, 5, 8],
			5: [4, 9],
			6: [0, 7, 18],
			7: [2, 6, 8, 15],
			8: [4, 7, 12],
			9: [5, 10, 14],
			10: [3, 9, 11, 17],
			11: [1, 10, 20],
			12: [8, 13],
			13: [12, 14, 16],
			14: [9, 13],
			15: [7, 16],
			16: [13, 15, 17, 19],
			17: [10, 16],
			18: [6, 19],
			19: [16, 18, 20],
			20: [11, 19]
		}

		self.checkMillMap = {
			0: [[6,18],[2,4]],
			1: [[11,20]],
			2: [[7,15],[0,4]],
			3: [[10,17]],
			4: [[0,2],[8,12]],
			5: [[9,14]],
			6: [[0,18],[7,8]],
			7: [[6,8],[2,15]],
			8: [[6,7],[4,12]],
			9: [[5,14],[10,11]],
			10: [[9,11],[3,17]],
			11: [[9,10],[1,20]],
			12: [[8,4],[13,14]],
			13: [[12,14],[16,19]],
			14: [[5,9],[12,13]],
			15: [[2,7],[16,17]],
			16: [[15,17],[13,19]],
			17: [[15,16],[10,3]],
			18: [[0,6],[19,20]],
			19: [[13,16],[18,20]],
			20: [[18,19],[11,1]]
		}


		
	def closeMill(self, j, b):
		for millNeighbors in self.checkMillMap[j]:
			if (b[millNeighbors[0]] == b[j]) and (b[millNeighbors[1]] == b[j]):
				return True

		return False


	def potentialCloseMill(self, j, b):
		for millNeighbors in self.checkMillMap[j]:
			if (b[millNeighbors[0]] == b[j]) and (b[millNeighbors[1]] == 'x'):
				return True
			if (b[millNeighbors[0]] == 'x') and (b[millNeighbors[1]] == b[j]):
				return True

		return False


	def countMills(self, board):
		numBlackCloseMills = 0
		numWhiteCloseMills = 0
		numPotBlackCloseMills = 0
		numPotWhiteCloseMills = 0

		for loc in range(len(board)):
			if board[loc] == 'W':
				if self.closeMill(loc, board):
					numWhiteCloseMills += 1
				if self.potentialCloseMill(loc, board):
					numPotWhiteCloseMills += 1
			if board[loc] == 'B':
				if self.closeMill(loc, board):
					numBlackCloseMills += 1
				if self.potentialCloseMill(loc, board):
					numPotBlackCloseMills += 1
		
		return numWhiteCloseMills, numBlackCloseMills, \
			numPotWhiteCloseMills, numPotBlackCloseMills


	def countPieces(self, board):
		numWhitePieces = 0
		numBlackPieces = 0

		for b in board:
			if b=='W':
				numWhitePieces += 1
			if b=='B':
				numBlackPieces += 1

		return numWhitePieces, numBlackPieces

	def checkBlocked(self, board, loc):
		res = True
		n = self.neighbors[loc]
		for ni in n:
			if board[ni] == 'x':
				res = False
		return res

	def blocked(self, board):
		whiteBlocked = 0
		blackBlocked = 0

		for loc in range(len(board)):
			if board[loc] == 'W':
				if self.checkBlocked(board, loc):
					whiteBlocked += 1
			if board[loc] == 'B':
				if self.checkBlocked(board, loc):
					blackBlocked += 1
		
		return whiteBlocked - blackBlocked	

	def staticMidGame(self, board):
		numWhitePieces = 0
		numBlackPieces = 0
		for b in board:
			if b=='W':
				numWhitePieces += 1
			if b=='B':
				numBlackPieces += 1

		numBlackMoves = len(self.GenerateMovesMidgameEndgame(board, True))

		numWhiteCloseMills, numBlackCloseMills, \
		numPotWhiteCloseMills, numPotBlackCloseMills = self.countMills(board)

		if numBlackPieces <= 2:
			return 10000
		elif numWhitePieces <= 2:
			return -10000
		elif numBlackMoves == 0:
			return 10000
		else:
			return 100 * ((numWhitePieces - numBlackPieces) + \
				3*(numWhiteCloseMills - numBlackCloseMills) + \
				2*(numPotWhiteCloseMills - numPotBlackCloseMills) + \
				self.blocked(board)) - numBlackMoves


	def static(self, board):
		
		numWhitePieces, numBlackPieces = self.countPieces(board)

		numWhiteCloseMills, numBlackCloseMills, \
		numPotWhiteCloseMills, numPotBlackCloseMills = self.countMills(board)

		return (numWhitePieces - numBlackPieces) + \
			3*(numWhiteCloseMills - numBlackCloseMills) + \
			2*(numPotWhiteCloseMills - numPotBlackCloseMills)+ \
			self.blocked(board)


	def MinMax(self, x, alpha, beta):
		depth = x.depth
		if self.maxDepth == depth:
			self.evaluatedPositions += 1
			if depth <= 18:
				return self.static(x.position)
			else:
				return self.staticMidGame(x.position)

		
		v = 50000 - depth
		if depth <= 18:
			children = self.GenerateMovesOpening(x.position, switchColor=True)
			children = sorted(children, key=self.static)
		else:
			children = self.GenerateMovesMidgameEndgame(x.position, switchColor=True)
			children = sorted(children, key=self.staticMidGame)

		for y in children:
			node_y = Node(y, depth+1)
			v = min(v, self.MaxMin(node_y, alpha, beta))
			if v <= alpha:
				return v
			else:
				beta = min(v,beta)
		return v


	def MaxMin(self, x, alpha, beta):
		depth = x.depth
		if self.maxDepth == depth:
			self.evaluatedPositions += 1
			if depth <= 18:
				return self.static(x.position)
			else:
				return self.staticMidGame(x.position)
		
		v = -50000 + depth
		if depth <= 18:
			children = self.GenerateMovesOpening(x.position)
			children = sorted(children, key=self.static, reverse=True)
		else:
			children = self.GenerateMovesMidgameEndgame(x.position)
			children = sorted(children, key=self.staticMidGame, reverse=True)
		
		for y in children:
			node_y = Node(y, depth+1)
			tmpV = v
			v = max(v, self.MinMax(node_y, alpha, beta))
			
			if v > tmpV and node_y.depth==(self.currDepth+1):
					self.bestResponse = y
			
			if v >= beta:
				return v
			else:
				alpha = max(v,alpha)

		return v


	def switchColors(self, board):
		for i in range(len(board)):
			if type(board[i]) == list:
				for j in range(len(board[i])):
					if board[i][j] == 'W':
						board[i][j] = 'B'
					elif board[i][j] == 'B':
						board[i][j] = 'W'

			else:
				if board[i] == 'W':
					board[i] = 'B'
				elif board[i] == 'B':
					board[i] = 'W'
		return board



	def GenerateRemove(self, board, L):
		numPositions = 0

		for loc in range(len(board)):
			if board[loc] == 'B':
				if not self.closeMill(loc, board):
					b = board.copy()
					b[loc] = 'x'
					L.append(b)
					numPositions += 1

		if numPositions == 0:
			L.append(board.copy())


	def GenerateAdd(self, board):
		L = []

		for loc in range(len(board)):
			if board[loc] == 'x':
				b = board.copy()
				b[loc] = 'W'
				if self.closeMill(loc, b):
					self.GenerateRemove(b, L)
				else:
					L.append(b)
		
		return L



	def GenerateHopping(self, board):
		L = []
		for loc1 in range(len(board)):
			if board[loc1] == 'W':
				for loc2 in range(len(board)):
					if board[loc2] == 'x':
						b = board.copy()
						b[loc1] = 'x'
						b[loc2] = 'W'
						if self.closeMill(loc2, b):
							self.GenerateRemove(b, L)
						else:
							L.append(b)
		return L


	def GenerateMove(self, board):
		L = []
		for loc in range(len(board)):
			if board[loc] == 'W':
				n = self.neighbors[loc]
				for j in n:
					if board[j] == 'x':
						b = board.copy()
						b[loc] = 'x'
						b[j] = 'W'
						if self.closeMill(j,b):
							self.GenerateRemove(b, L)
						else:
							L.append(b)
		return L


	def GenerateMovesMidgameEndgame(self, board, switchColor=False):
		if switchColor:
			board = self.switchColors(board)

		numWhitePieces = 0
		for b in board:
			if b=='W':
				numWhitePieces += 1

		if numWhitePieces == 3:
			L = self.GenerateHopping(board)
		else:
			L = self.GenerateMove(board)

		if switchColor:
			board = self.switchColors(board)
			L = self.switchColors(L)
		
		return L


	def GenerateMovesOpening(self, board, switchColor=False):
		if switchColor:
			board = self.switchColors(board)

		L = self.GenerateAdd(board)

		if switchColor:
			board = self.switchColors(board)
			L = self.switchColors(L)
		
		return L
