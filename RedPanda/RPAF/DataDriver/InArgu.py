class 实参(object):
    def __init__(self) -> None:
        self.dc = dict()

    def __getitem__(self, key):
        return self.dc[key]

    def __setitem__(self, key, value):
        self.dc[key] = value
