from datetime import date
import web_tools as wt
import regex_tools as rt
import file_tools as ft

class HTML():
    def __init__(self, page, search):
        self.page = page
        self.fetched = date.today()
        self.expires_after_days = 1
        self.text = self._set_html(search)
        self.title = self._set_title()
    
    def _set_title(self):
        if not self.text:
            return ""
        else:
            return rt.get_title(self.text)

    def _set_html(self, search=False, force=False):
        # TODO: Sørg for at den bare oppdaterer om den er utdatert!
        if (search and ft.is_expired(self.page.id, self.expires_after_days)) or force:
            text = wt.get_html(self.page.url)
            self._save_html(text)
            return text
        else:
            value = ft.find_html(self.page.id)
            if value == 1:
                return self._set_html(True)
            if value == 0:
                return False
            return ft.find_html(self.page.id)

    def _save_html(self, text=False):
        t = text if text else self.text
        ft.save_html(self.page.id, t)