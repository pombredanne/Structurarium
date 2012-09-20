from uuid import uuid1

try:
    from setproctitle import setproctitle
    def _setproctitle(title):
        setproctitle("structurarium.%s" % title)
except ImportError:
    def _setproctitle(title):
        return


def generate_identifier():
    return uuid1().hex
