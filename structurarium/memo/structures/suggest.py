from base import Base
from utils import check_alive
from utils import write


def iter_trigrams(string):
    for start in range(len(string))[:-2]:
        trigram = string[start:start + 3]
        yield trigram


class Suggest(Base):

    def __init__(self, memo, key):
        super(Suggest, self).__init__(memo, key)
        self.value = dict()

    @staticmethod
    @write
    def SUGGESTADD(memo, key, *strings):
        if key in memo.dict:
            if not memo.dict[key].alive():
                memo.dict[key] = Suggest(memo, key)
            else:
                if not isinstance(memo.dict[key], Suggest):
                    return 'ERROR', 'WRONG VALUE'
        else:
            memo.dict[key] = Suggest(memo, key)
        value = memo.dict[key]
        for string in strings:
            if len(string) < 3:
                continue
            else:

                for trigram in iter_trigrams(string):
                    if not trigram in value.value:
                        value.value[trigram] = list()
                    value.value[trigram].append(string)
        return 'RESULT', 'OK'

    @check_alive
    def SUGGEST(self, string, limit=10):
        suggestions = dict()
        for trigram in iter_trigrams(string):
            strings = self.value.get(trigram, [])
            for s in strings:
                try:
                    suggestions[s] += 1
                except:
                    suggestions[s] = 1
        suggestions = sorted(
            suggestions.keys(),
            key=lambda x: suggestions[x],
            reverse=True
        )
        suggestions = suggestions[:10]
        return 'RESULT', suggestions
