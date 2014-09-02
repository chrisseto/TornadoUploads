import string
import random

from invoke import task, run

from randomFile import RandomFile

def rndstr(length=10):
    return ''.join([random.choice(string.ascii_letters) for _ in xrange(length)])


@task
def genfile(size, name=None):
    size = int(size) * (1024 ** 2)
    name = 'files/%s' % (name or rndstr())
    run('openssl rand -base64 -out %s %s' % (name, size))

@task
def rfile(size, name=None):
    blocksize = 1024 ** 2
    name = name or rndstr()
    name = 'files/%s' % name
    run('dd if=/dev/urandom of=%s bs=%s count=%s' % (name, blocksize, size))

@task
def upload(file_loc, service):
    run('curl -i -F name=%s -F filedata=@%s http://localhost:7777/%s' % (rndstr(), file_loc, service))
