from tools import file_tools as ft
from menus import functions as lf


def preset_menu():
    presets = ft.fetch_presets()
    if presets:
        print("SAVED PRESETS:")
        for key in presets:
            print(f" * {key}:")
            for i in range(len(presets[key])):
                print(f"    - {presets[key][i]['league']}, {presets[key][i]['country']}, {presets[key][i]['continent']}")

    ft.save_presets({"test": [
        {"league": "OBOS",
         "country": "Norway",
         "continent": "Europe"},
        {"league": "Eliteserien",
         "country": "Norway",
         "continent": "Europe"}]})
    exit()

    inp = lf._list_items(["Add", "Remove"])

    if inp == "Add":
        ...
    if inp == "Remove":
        ...
