from board import *
# from skimage.measure import block_reduce

class Agent:
    FLAG_ACTION = 'flag'
    REVEAL_ACTION = 'reveal'

    not_bomb = 0
    
    def action(self, revealed_board: np.ndarray[int], flags: np.ndarray[bool],  revealed_filter: np.ndarray[bool]):
        bomb_probability, bomb_for_sure = self.bomb_probability(revealed_board, revealed_filter, flags)
        debug = {"probs": bomb_probability, "bomb": bomb_for_sure}
        assert not np.isnan(bomb_probability).any() , "Should not have nans"
        
        if bomb_probability.any():
            bomb_probability = np.nan_to_num(bomb_probability)
            bombe_loc = np.unravel_index(bomb_for_sure.argmax(), revealed_board.shape)
            return bombe_loc, Agent.FLAG_ACTION, debug
        
        not_bomb_loc = np.unravel_index(bomb_probability.argmin(), revealed_board.shape)
        
        
        return not_bomb_loc, Agent.REVEAL_ACTION, debug

    def bomb_probability(self, revealed_int_board: np.ndarray, revealed_filter: np.ndarray[bool], flags: np.ndarray[bool]) -> tuple(np.ndarray[float]):
        one_mat = np.ones((3,3))

        unknown_board = ~revealed_filter & ~flags
        hidden_tiles_we_have_info_on = convolve(revealed_int_board.astype(bool), one_mat, mode="constant")
        hidden_tiles_we_have_info_on &= unknown_board

        nb_unrevealed_tiles = convolve(unknown_board.astype(int), one_mat, mode="constant")
        nb_bombs_spoted = convolve(flags.astype(int), one_mat, mode="constant")

        spoting_bomb_from_tile_probability: np.ndarray[float] = (revealed_int_board - nb_bombs_spoted)/np.clip(nb_unrevealed_tiles, 1, 9)
        spoting_bomb_from_tile_probability[~revealed_filter] = 0
        
        bomb_for_sure = convolve((spoting_bomb_from_tile_probability >=1).astype(int), one_mat, mode="constant")
        bomb_for_sure[flags|revealed_filter] = 0

        nb_revealed_tiles = convolve((revealed_filter).astype(int), one_mat, mode="constant")
        bomb_probability: np.ndarray[float] = convolve(spoting_bomb_from_tile_probability, one_mat, mode="constant")/np.clip(nb_revealed_tiles, 1, 9)
        bomb_probability[~hidden_tiles_we_have_info_on] = 0
        return bomb_probability, bomb_for_sure
        
    
    
    