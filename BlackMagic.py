import time
import string
import random
import hashlib

import toro

from tornado import gen, web
from tornado.web import RequestHandler


@web.stream_request_body
class WeirdUploadHandler(RequestHandler):

    @web.asynchronous
    def post(self):
        pass

    def upload_complete(self, response):
        if response.error:
            self.finish()
            raise response.error

        self.write({
            'size': int(self.request.headers['Content-Length']),
            'sha256': self.hash.hexdigest(),
            'timeTaken': time.time() - self.start_time
        })
        self.finish()

    def upload_file(self):
        raise NotImplemented()

    def prepare(self):
        #Note: Grab content length and pass to httpclient
        self.q = toro.Queue()
        self.hash = hashlib.sha256()
        self.name = rndstr()
        self.upload_started = False
        self.start_time = time.time()

    @gen.coroutine
    def cloudify(self, write):
        while True:
            try:
                chunk = yield self.q.get(deadline=1000)
            except toro.Timeout:
                break
            yield write(chunk)

    @gen.coroutine
    def data_received(self, data):
        yield self.q.put(data)
        self.hash.update(data)

        if not self.upload_started:
            # Make sure there is at least one chunk in the queue
            self.upload_started = True
            self.upload_file()

def rndstr(length=10):
    return ''.join([random.choice(string.ascii_letters) for _ in xrange(10)])

