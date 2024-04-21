import pygame
from board import Board, CELL_SIZE, MARGIN
from pygame.locals import QUIT

if __name__ == '__main__':
    pygame.init()
    cell_size = CELL_SIZE
    margin = MARGIN
    screen = pygame.display.set_mode((7 * cell_size + margin * 5 , 7 * cell_size + margin))
    board = Board()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # Handle events for draggable pieces
            for player_pieces in board.pieces.values():
                for piece in player_pieces:
                    piece.handle_event(event, board.pieces)

        # Update the position of draggable pieces
        board.start_timer("main_loop")
        board.update_draggable_pieces()
        board.end_timer("main_loop")

        # Redraw the board
        board.draw(screen, cell_size, margin)

    pygame.quit()