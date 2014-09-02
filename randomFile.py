import string
import random

class RandomFile(object):

    def __init__(self, size=None):
        self.loc = 0
        self.length = size or random.randint((1024**2) * 5, (1024**2) * 10)

    def read(self, n=None):
        if not n:
            n = self.length
        self.loc += n
        if self.loc >= self.length:
            return ''
        elif n + self.loc > self.length:
            n = self.length - self.loc
        return ''.join([random.choice(string.ascii_letters) for _ in xrange(n)])

    def __iter__(self):
        yield self.read(1024)


    def __len__(self):
        return self.length
