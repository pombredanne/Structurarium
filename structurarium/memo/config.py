class Config(object):

    def __init__(self, args, config):
        self.args = args
        self.config = config

    def get(self, key, d=None):
        section, key = key.split('.')
        try:
            value = self.config.get(section, key)
        except:
            pass
        else:
            return value
        return getattr(self.args, key, d)

    def getint(self, key, d=None):
        section, key = key.split('.')
        try:
            value = self.config.getint(section, key)
        except:
            pass
        else:
            return value
        return getattr(self.args, key, d)

    def getlist(self, key, d):
        section, key = key.split('.')
        try:
            value = self.config.get(section, key)
            value = value.split()
        except:
            pass
        else:
            return value
        return getattr(self.args, key, d)
