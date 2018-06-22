

class BaseNuker:
    enabled = True
    def __init__(self):
        self.dependencies = []
        self.name = ''

    def nuke(self):
        raise NotImplementedError
