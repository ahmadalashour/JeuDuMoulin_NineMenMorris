import pygame
from board import Board
from globals import CELL_SIZE, MARGIN
from pygame.locals import QUIT

if __name__ == "__main__":
    pygame.init()
    cell_size = CELL_SIZE
    margin = MARGIN
    screen = pygame.display.set_mode(
        (7 * cell_size + margin * 5, 7 * cell_size + margin)
    )
    board = Board()

    running = True
    remove_piece = False
    backup_phase = board.phase
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if not board.game_over():
                if not remove_piece:
                    # Handle events for draggable pieces
                    for piece in board.pieces[board.turn]:
                        legality = piece.handle_event(event, board)
                        if legality == "remove":
                            remove_piece = True
                            backup_phase = board.phase
                            board.phase = "capturing"
                            break
                        if legality == "move":
                            board.turn = "orange" if board.turn == "white" else "white"
                            break
                else:
                    other_turn = "orange" if board.turn == "white" else "white"
                    removed = False
                    for piece in board.pieces[other_turn]:
                        if piece.handle_remove_event(event):
                            removed = True
                            board.pieces[other_turn].remove(piece)
                            break
                    if removed:
                        remove_piece = False
                        board.turn = "orange" if board.turn == "white" else "white"
                        board.phase = backup_phase
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    board = Board()

        # Update the position of draggable pieces
        board.start_timer("main_loop")
        board.update_draggable_pieces()
        board.end_timer("main_loop")

        # Redraw the board
        board.draw(screen, cell_size, margin)

    pygame.quit()
