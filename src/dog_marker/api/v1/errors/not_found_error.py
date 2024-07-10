class EntityNotFound(Exception):
    def __init__(self, msg: str = "Entity not found"):
        self.msg = msg
