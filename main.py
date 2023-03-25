# %%
from board import *
from agent import Agent


b = Board(10, 7,7)
a = Agent(b.shape)

revealed = b.get_revealed()
print(revealed, a.action(revealed))
# %%
debugs = []
while not b.is_finished():
    action, debug = a.spot_not_bomb(b.get_revealed())
    b.reveal_all_adjacents(action)
    debugs.append(debug)
    print(
        f'action: {action}',
        debug
    )



