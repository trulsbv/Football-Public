import tools.prints as prints
import math


def _list_items(items: list, per_page: int = 10, page=0, accept_none=False) -> any:
    """
    Takes a list and items per page. Lets the user
    Choose one of the items in the list

    Arguments:
        * List of items
        * Number of items to show per page

    Returns:
        * String name of item
    """
    max_pages = math.floor(len(items) / per_page)
    if len(items) - (max_pages * per_page) > 0:
        max_pages = max_pages + 1

    ctr = per_page * page
    i = 0
    inp = ""
    print(f"\nPage {page+1}/{max_pages}")
    while ctr < len(items) and i < per_page:
        print(f"[{i}] {items[ctr]}")
        ctr += 1
        i += 1
    s = "[0 - "
    if len(items) < per_page:
        s += f"{len(items)-1}"
    else:
        s += f"{per_page-1}"
    s += "] Select"
    if accept_none:
        s += ", [Q] Quit"
    if len(items) > per_page:
        s += ", [P] Previous page, [N] Next page"
    print(s)
    inp = input(" => ")
    if accept_none and inp == "":
        return None

    if inp.isnumeric():
        inp = int(inp)
        if not (inp < 0 or inp >= i):
            return items[page * per_page + inp]
    else:
        inp = inp.upper()
        if inp == "Q":
            return None
        if inp == "N":
            if ctr >= len(items):
                return _list_items(items, per_page, 0)
            return _list_items(items, per_page, page + 1)
        if inp == "P":
            if page == 0:
                return _list_items(items, per_page, max_pages - 1)
            return _list_items(items, per_page, page - 1)

    prints.error("Select item", "Invalid input")
    return _list_items(items, per_page, page)
