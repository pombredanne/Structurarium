class Cache(dict):

    # FIXME wrap multiprocessing.manager.dict instance

    def check_and_set(self, key, original, new):
        if self[key].value == original.value:
            self[key] = new
            return True
        return False
