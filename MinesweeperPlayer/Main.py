from GameManager import *
from logging.config import fileConfig

def main():
    fileConfig("logging_config.ini")
    manager = GameManager()
    manager.run()

# Needed for preventing recursive calls.
if __name__ == "__main__":
    main()