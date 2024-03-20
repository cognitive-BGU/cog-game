from src.interface import run_gui
from src.game import run_game
COMP_CAMERA = 0


if __name__ == '__main__':
    config = run_gui()
    run_game(config, COMP_CAMERA)

print("hello world")
