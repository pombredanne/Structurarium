from structurarium.memo.client import MemoClient


rex = MemoClient(('127.0.0.1', 8001))

rex.SUGGESTADD('SPELLCHECKER')

with open('wordlist.txt') as words:
    for word in words:
        rex.SUGGESTADD('SPELLCHECKER', word.strip())
