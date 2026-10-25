import random
from typing import List, Optional, Tuple

class TicTacToe:
    """
    A class representing an interactive Tic-Tac-Toe game with a Minimax AI bot.
    
    Attributes:
        board (List[str]): 3x3 grid representation of the game state.
        human_player (str): Symbol for the human player ('X').
        ai_player (str): Symbol for the AI player ('O').
        current_player (str): Whose turn it is currently.
    """

    def __init__(self, human_player: str = 'X', ai_player: str = 'O'):
        if not (len(human_player) == 1 and len(ai_player) == 1 and human_player != ai_player):
            raise ValueError("Players must be single characters and distinct.")
        
        self.board = [''] * 9
        self.human_player = human_player
        self.ai_player = ai_player
        self.current_player = human_player

    def reset(self) -> None:
        """Resets the game board to an empty state."""
        self.board = [''] * 9
        self.current_player = self.human_player

    def get_empty_indices(self) -> List[int]:
        """Returns a list of indices where the board is empty."""
        return [i for i, cell in enumerate(self.board) if cell == '']

    def check_winner(self, player: str) -> bool:
        """
        Checks if the specified player has won.
        
        Args:
            player (str): The player symbol to check ('X' or 'O').
            
        Returns:
            bool: True if the player has won, False otherwise.
        """
        winning_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8), # Columns
            (0, 4, 8), (2, 4, 6)              # Diagonals
        ]
        
        for a, b, c in winning_combinations:
            if (self.board[a] == player and 
                self.board[b] == player and 
                self.board[c] == player):
                return True
        return False

    def is_board_full(self) -> bool:
        """Checks if the board is completely filled."""
        return all(cell != '' for cell in self.board)

    def get_opponent(self, player: str) -> str:
        """Returns the opponent's symbol given a player's symbol."""
        return 'O' if player == 'X' else 'X'