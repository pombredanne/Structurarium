Structurarium-old vs redis 2.2.2
================================


populate
--------

python redis_populate.py  54,05s user 14,71s system 90% cpu 1:16,02 total
redis server : 97364 K

python rex_populate.py  11,44s user 5,89s system 58% cpu 29,606 total
structurarium server : 137504 K

query
-----

python redis_query.py  46,16s user 0,32s system 96% cpu 47,992 total
result: 300 / 424
memory: 97428 K

python rex_query.py  0,12s user 0,05s system 5% cpu 3,197 total
result: 296 / 424
memory: 138244 K
