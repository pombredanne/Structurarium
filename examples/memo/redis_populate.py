import redis


r = redis.StrictRedis(host='localhost', port=6379, db=0)


def iter_trigrams(string):
    for start in range(len(string))[:-2]:
        trigram = string[start:start+3]
        yield trigram


words = open('wordlist.txt')
for word in words:
    word = word.strip()
    for trigram in iter_trigrams(word):
        r.sadd(trigram, word)

words.close()
