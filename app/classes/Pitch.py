import tools.file_tools as ft
from classes.Page import Page


class Pitch:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.name = None
        self.games = []  # not used yet? But the pitch could keep the games played at it
        self.fetch_info()

    def fetch_info(self):
        (
            self.name,
            self.surface,
            self.size,
            self.lighting,
            self.length,
            self.width,
            self.owner,
            self.municipality,
        ) = ft.get_baneinfo(self.page.html.text)

    def get_analysis(self):
        return {
            "name": self.name,
            "surface": self.surface,
            "size": self.size,
            "lighting": self.lighting,
            "length": self.length,
            "width": self.width,
            "owner": self.owner,
            "municipality": self.municipality,
        }

    def __repr__(self) -> str:
        if self.name is None:
            self.fetch_info()
        return self.name
