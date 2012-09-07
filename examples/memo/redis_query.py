import redis, json


def iter_trigrams(string):
    for start in range(len(string))[:-2]:
        trigram = string[start:start+3]
        yield trigram


r = redis.StrictRedis(host='localhost', port=6379, db=0)

missplellings_w_corrections_file = open('missplellings_w_corrections.txt')
missplellings_w_corrections = missplellings_w_corrections_file.read()
missplellings_w_corrections_file.close()
missplellings_w_corrections = json.loads(missplellings_w_corrections)


hit = 0
total = len(missplellings_w_corrections)

for mistake, corrections in missplellings_w_corrections.iteritems():
    trigrams = iter_trigrams(mistake)
    suggestions = []
    for trigram in trigrams:
        suggestions.append(r.smembers(trigram))

    s = {}

    for suggestion in suggestions:
        for word in suggestion:
            try:
                s[word] += 1
            except KeyError:
                s[word] = 1

    suggestions = sorted(
        s.keys(),
        key=lambda x: s[x],
        reverse=True
    )

    suggestions = suggestions[:10]

    for correction in corrections:
        if correction in suggestions:
            # at the end ``miss`` can be superior to total
            # because we want all possible correction
            # to be suggested :)
            hit += 1

print hit, '/', total
