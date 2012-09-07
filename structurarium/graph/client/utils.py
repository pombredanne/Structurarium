import os
import hashlib


def gen(a):
    def g():
        return a + hashlib.md5(os.urandom(1024)).hexdigest()
    return g

generate_tmp_identifier = gen('tmp')
