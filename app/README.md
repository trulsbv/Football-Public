# To run:
Flags:
    * -test
    * -test2
    * -testES
    * -log (NOT IMPLEMENTED)
    * -help

Create a file .env inside the webscraping folder and insert:
VISUALCROSSING_KEY = "[your_key_no_brackets]"

# Possible improvements:
- Use Panda instead of objects ?
- Make tests
    1. Read from analysis AND from html
    2. Make sure that some data is poorly formatted (as fotball.no sometimes is)
- Add docstrings


test = [
        ["-288px -0", 9],
        ["-324px -252", 80],
        ["-0px -252", 71],
        ["-108px -288", 84],
        ["-324px -288", 90],
        ["-0px -216", 61]
        ]
    for item in test:
        print(f"{item[1]} == {px_to_minute(item[0])}")
