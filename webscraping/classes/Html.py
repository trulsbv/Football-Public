from datetime import date
import tools.file_tools as ft
import tools.regex_tools as rt
import tools.web_tools as wt

class HTML():
    def __init__(self, page, search, vf, extension):
        self.page = page
        self.fetched = date.today()
        self.valid_from = vf
        self.ext = extension
        self.text = self._set_html(search)
        self.title = self._set_title()
    
    def _set_title(self):
        if not self.text:
            return ""
        else:
            return rt.get_title(self.text)

    def _set_html(self, search=False, force=False):
        # TODO: Sørg for at den bare oppdaterer om den er utdatert!
        if (search and ft.is_not_valid(self.page.id, self.valid_from, self.ext)) or force:
            text = wt.get_html(self.page.url)
            self._save_html(text)
            return text
        else:
            value = ft.find_html(self.page.id)
            if value == 0:
                return False
            return ft.find_html(self.page.id)

    def _save_html(self, text=False):
        t = text if text else self.text
        ft.save_html(self.page.id, t, self.ext)