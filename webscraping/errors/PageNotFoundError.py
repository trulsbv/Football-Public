class PageNotFoundError(Exception):
    def __init__(self, where, page):
        self.message = f"The page '{page}' in {where} is not accessible"
        super().__init__(self.message)
