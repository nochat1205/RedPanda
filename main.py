import sys

from RedPanda.logger import Logger
from RedPanda.main import MainApplication

if __name__ == "__main__":
    sys.exit(MainApplication.Run(sys.argv))
