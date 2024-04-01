from classes.Html import HTML
import settings


class Page:
    def __init__(
        self, url, search=True, force=False, valid_from=False, extension=".html"
    ):
        """
        Set search to false if you don't want to keep the page updated / fetch the page at all
        """
        self.url = url
        self.id = self._set_id()
        self.fetched = False
        self.html = HTML(self, search, valid_from, extension)
        if force:
            print("FORCE")
            self.html._set_html(force=True)

    def update_html(self):
        if not self.html.text:
            self._update_html()
            return
        if self.html.text.split("\n")[0] != str(settings.DATE):
            self._update_html()

    def _update_html(self):
        self.html._set_html(True)

    def _set_id(self):
        id = self.url.replace("https://www.", "")
        return id[:-1] if id[-1] == "/" else id

    def __hash__(self):
        return hash(self.url)

    def __lt__(self, obj):
        return (self.id) < (obj.id)

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.url
        if isinstance(other, Page):
            return other.url == self.url
        return False

    def __repr__(self) -> str:
        return self.url
