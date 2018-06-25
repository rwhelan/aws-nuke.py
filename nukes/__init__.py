

class BaseNuker:
    enabled = True
    def __init__(self):
        self.dependencies = []
        self.name = ''

    def nuke(self):
        raise NotImplementedError

    def list_resources(self):
        return [f"<<< list for {self.name} not implemented >>>"]
