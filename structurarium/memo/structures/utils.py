def check_alive(function):
    def wrapped(self, *args):
        if not self.alive():
            return 'ERROR', 'KEY DOES NOT EXISTS'
        return function(self, *args)
    return wrapped


def write(function):
    function.write = True
    return function
