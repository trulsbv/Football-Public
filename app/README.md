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

# Known Fotball.no errors:
Had to change 8189858 and 25656 to 26577 in all files as Sandnes Ulf's home arena had a 404 error.

Sandnes-ulf - KFUM endte 1-2, men fotball.no har ikke registrert det ene målet
https://www.google.com/search?q=Sandnes+ulf+-+kfum&sca_esv=584527748&rlz=1C1ONGR_noNO1026NO1026&sxsrf=AM9HkKm3U2KMZC5aIiWOPFjP-j7kkjWMnQ%3A1700642103490&ei=N71dZcSzHcCTxc8P-fawGA&ved=0ahUKEwiEq9_DmdeCAxXASfEDHXk7DAMQ4dUDCBA&uact=5&oq=Sandnes+ulf+-+kfum&gs_lp=Egxnd3Mtd2l6LXNlcnAiElNhbmRuZXMgdWxmIC0ga2Z1bTIFEAAYgAQyCBAAGIAEGMsBMggQABiABBjLATIGEAAYFhgeMgYQABgWGB4yBhAAGBYYHjIGEAAYFhgeMgYQABgWGB4yBhAAGBYYHjILEAAYgAQYigUYhgNImypQrwdY3yhwBHgBkAEAmAGdAaABsQ-qAQQxNi41uAEDyAEA-AEBwgIKEAAYRxjWBBiwA8ICChAjGIAEGIoFGCfCAgsQLhiABBiKBRiRAsICCxAuGIAEGMcBGNEDwgIEECMYJ8ICERAuGIAEGIoFGMcBGNEDGJECwgIKEAAYgAQYigUYQ8ICBRAuGIAEwgILEC4YgAQYxwEYrwHCAgoQLhiABBiKBRhDwgIaEC4YgAQYigUYkQIYlwUY3AQY3gQY3wTYAQHCAggQLhiABBjLAcICDhAuGIAEGMsBGMcBGNEDwgIIEC4YywEYgATCAgsQLhiABBjLARjUAsICGhAuGIAEGIoFGJECGJcFGNwEGN4EGOAE2AEBwgIKEC4YywEYgAQYCsICEBAuGIAEGMsBGMcBGNEDGArCAgoQABiABBjLARgKwgIQEC4YgAQYywEYxwEYrwEYCsICBxAuGIAEGArCAg0QLhiABBjHARjRAxgKwgIHEAAYgAQYCsICFxAuGIAEGMsBGJcFGNwEGN4EGOAE2AEBwgILEAAYgAQYigUYkQLiAwQYACBBiAYBkAYIugYGCAEQARgU&sclient=gws-wiz-serp#sie=m;/g/11sczn2tkk;2;/m/06h829;dt;fp;1;;;