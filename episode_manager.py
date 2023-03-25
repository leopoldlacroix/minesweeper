# %%
from agent import *
from board import Board
import os

class EpisodeManager:
    def __init__(self, a: Agent, b: Board) -> None:
        self.a, self.b = a,b


        while not b.is_finished():
            os.system('cls')
            print(f"is finished: {b.is_finished()}")
            print(self.b.show_revealed())

            loc, action_type, debug = self.a.action(b.get_revealed(), b.flags, b.revealed_filter)
            
            print(loc, action_type)
            if action_type == Agent.REVEAL_ACTION:
                b.reveal(loc)
            elif action_type == Agent.FLAG_ACTION:
                b.flag(loc)
            
        print("--------")
        print(b.game_over, b.is_win())
        print(self.b.show_real())




b = Board(10, 7, 7)
a = Agent()
e = EpisodeManager(a, b)
