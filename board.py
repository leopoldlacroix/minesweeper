# %%
from tools import prompt_colors as colors
import numpy as np
import pandas as pd
from scipy.ndimage import convolve

class Board:
    not_revealed_str = colors.highlight_black + " "
    flag_str = colors.green + "F"
    int_to_show_dict = {-1: colors.red + 'B', 0:colors.white+'0',  1:colors.ok_blue+'1', 2:colors.yellow+"2", 3:colors.red+"3", 4:colors.black+"4", 5:colors.red+"5", 6:colors.red+"6", 7:colors.red+"7", 8:colors.red+"8", 9:colors.red+"9"}

    def __init__(self, nb_bombs = 10, width = 7, length = 7, board_repr = None) -> None:      
        if board_repr != None:
            self.from_string(board_repr)
            return
        
        self.nb_bombs = nb_bombs
        self.shape = (width, length)
        self.total_tiles = width*length
        self.game_over = False

        tiles = [-1]*nb_bombs + [0]*(self.total_tiles - nb_bombs)
        tiles = np.random.choice(tiles, self.total_tiles, replace=False).reshape(*self.shape)
        nb_bombs_arround = convolve(tiles,np.ones((3,3)), mode="constant")
        
        self._board: np.ndarray = tiles + -(tiles+1)*nb_bombs_arround
        self.flags = np.zeros(self.shape).astype(bool)
        
        self.revealed_filter = np.zeros(self.shape).astype(bool)
        first_revealed_ij = zip(*np.where(self._board == 0)).__next__()
        self.reveal_all_adjacents(first_revealed_ij)

    def from_string(self, board_repr:str):
        str_board = np.array([e[1:].split(' ') for e in board_repr.replace("F", "-1").split("\n")])
        board = Board.show_to_int(str_board)
        self.nb_bombs = (board == -1).sum()
        self.shape = board.shape
        self.total_tiles = np.prod(board.shape)
        self.game_over = False

        self._board: np.ndarray[int] = board
        self.flags = np.zeros(self.shape).astype(bool)
        self.revealed_filter = np.zeros(self.shape).astype(bool) + (board != -1).astype(int)        

    def get_revealed(self) -> np.ndarray:
        revealed = self.get_real()
        revealed[~self.revealed_filter] = 0
        return revealed
    

    def show_revealed(self) -> str:
        revealed: np.ndarray = self.get_revealed()
        replace = lambda x: Board.int_to_show_dict[x]
        revealed = np.vectorize(replace)(revealed)
        revealed[~self.revealed_filter] = Board.not_revealed_str
        revealed[self.flags] = Board.flag_str
        return "\n".join(np.apply_along_axis("".join, 1,  revealed))+colors.normal

    def show_to_int(board: np.ndarray[str]) -> np.ndarray[float]:
        """Turns strs to floats replacing inrevealed tiles by 0

        Args:
            board (np.ndarray[str]): the shown board

        Returns:
            np.ndarray[float]: the board with floats
        """
        to_int = lambda x: int(Board.show_to_int_dict[x[-1]])
        return np.vectorize(to_int)(board)

    
    def show_real(self):
        revealed = self.get_real()
        replace = lambda x: Board.int_to_show_dict[x]
        revealed = np.vectorize(replace)(revealed)
        return f"\n".join(np.apply_along_axis("".join, 1,  revealed))+colors.normal
    


    def reveal_all_adjacents(self, ij):
        ijs_to_check = [ij]

        while ijs_to_check != []:
            ij = ijs_to_check.pop()
            
            if not self.revealed_filter[*ij]:
                self.revealed_filter[*ij] = True
                if self._board[*ij] == 0:
                    ijs_to_check += self.all_adjacents(ij)
        
    def all_adjacents(self, ij):
        surround = 3
        
        adjacents_indexes: np.ndarray = np.array([
            np.tile(np.array([-1, 0, 1]), surround),
            np.repeat(np.array([-1, 0, 1]), surround)
        ]).T + ij

        is_valid = np.apply_along_axis(all, 1, ((0,0) <= adjacents_indexes)&(adjacents_indexes < self.shape))

        adjacents_indexes = adjacents_indexes[is_valid]
        return adjacents_indexes.tolist()


    def reveal(self, ij):
        if self.game_over: Exception("Can't play")

        if self._board[*ij] == -1 or self.flags[*ij]:
            self.game_over = True

        self.reveal_all_adjacents(ij)

    def flag(self, ij):
        if self.is_finished(): Exception("Can't play")
        if self._board[*ij] != -1:
            self.game_over = True
            self.revealed_filter[*ij] = True

        else:
            self.flags[*ij] = True
        return self.game_over
        
        
    def get_real(self):
        return self._board.copy()
    
    def is_finished(self) -> bool:
        return self.game_over or self.is_win()
    
    def is_lost(self):
        return self.game_over
    
    def is_win(self):
        return self.revealed_filter.sum() == np.prod(self.shape) 