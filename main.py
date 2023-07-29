from src.interface import start_gui
from src.game import start_game
COMP_CAMERA = 0


if __name__ == '__main__':
    config = start_gui()
    print(config)
    start_game(config, COMP_CAMERA)
