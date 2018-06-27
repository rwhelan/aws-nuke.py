

class BaseNuker:
    enabled = True
    global_service = False
    def __init__(self):
        self.dependencies = []
        self.name = ''

    def nuke_resources(self):
        raise NotImplementedError

    def list_resources(self):
        return [f"<<< list for {self.name} not implemented >>>"]
