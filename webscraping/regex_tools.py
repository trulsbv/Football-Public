import re

def find_urls(
    html: str,
    base_url: str = "https://www.fotball.no",
    output: str | None = None,
) -> set[str]:
    """
    Find all the url links in a html text using regex

    Arguments:
        html (str): html string to parse
        base_url (str): the base url to the wikipedia.org pages
        output (Optional[str]): file to write to if wanted
    Returns:
        urls (Set[str]) : set with all the urls found in html text
    """
    # create and compile regular expression(s)
    urls = []

    if type(html) != str:
        return urls
    
    # 1. find all the anchor tags, then
    a_pat = re.compile(r"<a[^>]+>", flags=re.IGNORECASE)
    # 2. find the urls href attributes

    # finds links that start with http
    abs_href_pat = re.compile(r'href="(https[^"]+)"', flags=re.IGNORECASE)
    # finds links that starts with two //, same protocol but different host
    new_host_href_pat = re.compile(r'href="([\/]{2}[^"]+)"', flags=re.IGNORECASE)

    # finds links that starts with a single / until we meet a # or ", meaning it's the same host
    same_host_href_pat = re.compile(r'href="([\/][^\/][^#|"]+)"', flags=re.IGNORECASE)

    same_host_2_pat = re.compile(r'href="([\/][^\/].*)#[^"]*">', flags=re.IGNORECASE)

    for a_tag in a_pat.findall(html):
        match_abs = abs_href_pat.search(a_tag)
        match_new_host = new_host_href_pat.search(a_tag)
        match_same_host = same_host_href_pat.search(a_tag)
        match_same_host2 = same_host_2_pat.search(a_tag)

        if match_abs:
            a = match_abs.group(1)
            if ".pdf" not in a:
                urls.append(a.rstrip("/"))
        
        elif match_new_host:
            a = "https:" + match_new_host.group(1)
            if ".pdf" not in a:
                urls.append(a.rstrip("/"))

        elif match_same_host:
            a = f"{base_url}" + match_same_host.group(1)
            if ".pdf" not in a:
                urls.append(a.rstrip("/"))

        elif match_same_host2:
            a = f"{base_url}" + match_same_host2.group(1)
            if ".pdf" not in a:
                urls.append(a.rstrip("/"))
        
    # Write to file if requested
    if output:
        f = open(output, "w", encoding="UTF-8")
        for item in urls:
            f.write(item+"\n")
    return urls

def find_league_from_url(url):
    id_pat = re.compile(r'https:\/\/www\.fotball\.no(.*\/turneringe?r?\/.*)')
    match = id_pat.search(url)
    if match:
        return match.group(1)
    return False

def get_id_from_url(url):
    id_pat = re.compile(r'fiksId=(\d*)')
    match = id_pat.search(url)
    if match:
        return match.group(1)
    
    id_no_id_pat = re.compile(r'https:\/\/www\.[^.]*\.[A-z]{2,3}\/(.*)')
    match = id_no_id_pat.search(url)
    if match:
        new = match.group(1).replace("/", "-")
        return new[:-1] if new[-1] == "/" else new
    return False

def get_path_from_url(url):
    id_pat = re.compile(r'https:\/\/www\.[A-z]*\.[A-z]{2,3}\/(.*)')
    match = id_pat.search(url)
    if match:
        return match.group(1).replace("/", "-")

def get_title(html):
    title_pat = re.compile(r'<title>[\s]*([^<]*)<\/title>')
    match = title_pat.search(html)
    if match:
        return match.group(1)
    return False

def get_team_name(html):
    name_pat = re.compile(r'<title>(.*) - Hjem - Norges Fotballforbund<\/title>')
    match = name_pat.search(html)
    if match:
        return match.group(1)
    return False

def get_krets(html):
    krets_pat = re.compile(r'<li><b>Krets: <\/b><a href=[^>]*>([^>]*)<\/a><\/li>')
    match = krets_pat.search(html)
    if match:
        return match.group(1)
    return False
