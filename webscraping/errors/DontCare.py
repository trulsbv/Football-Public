class DontCare(Exception):
    def __init__(self):
        self.message = "Really. Don't. Care."
        super().__init__(self.message)
