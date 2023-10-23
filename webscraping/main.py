import web_tools as wt
import regex_tools as rt
import file_tools as ft
from datetime import date

serier=["Eliteserien"]

class Page():
    def __init__(self, url, type=None):
        self.url = url
        self.fetched = False
        self.html = False
        self.id = False
        self.name = False
        self.type = type
        self._set_id()
        self._set_name()
        self.get_html()
    
    def get_name(self):
        if not self.html:
            return
        self.name = rt.get_title(self.html)
        if self.name:
            ft.save_name(self.name, self.id)
    
    def get_html(self, fetch=False):
        self.html = ft.find_html(self.id)
        if (not self.html) and fetch:
            self._fetch_html()
        self.get_name()
        return self.html

    def get_all_info(self):
        s=""
        s+=f"     id: {self.id}\n"
        s+=f"    url: {self.url}\n"
        s+=f"   name: {self.name}\n"
        if self.html: 
            s+=f"   html: True\n" 
        else:
            s+=f"   html: False\n"
        s+=f"fetched: {self.fetched}"
        print(s)

    def _is_table_page(self):
        try:
            int(self.id)
            len(self.id) == 6
            return True
        except:
            return False

    def _set_id(self):
        self.id = rt.get_id_from_url(self.url)
        if not self.id:
            self.id = rt.get_path_from_url(self.url)

    def _set_name(self):
        self.name = ft.find_name(self.id)
    
    def _fetch_html(self):
        self.html = ft.find_html(self.id)
        if self.html:
            return
        self.fetched = date.today()
        self.html = wt.get_html(self.url)
        ft.save_html(self.id, self.html)

    def __hash__(self):
        return hash(self.url)
    
    def __lt__(self, obj):
        return ((self.name) < (obj.name)) 

    def __eq__(self, other):
        if type(other) == str:
            return other == self.url
        if type(other) == Page:
            return other.url == self.url
        return False

    def __repr__(self) -> str:
        return self.url
    
def main():
    pages = []
    p = Page("https://www.fotball.no/turneringer")
    pages.append(p)
    html = p.get_html(True)
    urls = rt.find_urls(html)
    urls.sort()
    for url in urls:
        u = rt.find_league_from_url(url)
        if u:
            new = Page(url, "League")
            pages.append(new)
    pages.sort()
    for page in pages:
        print(page.name)

if __name__=="__main__":
    main()
