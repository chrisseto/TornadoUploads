import json
import logging

import requests

from tornado import web, gen
from tornado import httpclient
from tornado.ioloop import IOLoop
from tornado.web import Application

from AsyncS3 import AsyncS3Connection


from BlackMagic import WeirdUploadHandler, rndstr
from settings import RACKSPACE_AUTH, AWS_AUTH

connection = AsyncS3Connection(**AWS_AUTH)

ret = requests.post('https://identity.api.rackspacecloud.com/v2.0/tokens', headers={'Content-Type': 'application/json'}, data=json.dumps(RACKSPACE_AUTH))



@web.stream_request_body
class S3Uploader(WeirdUploadHandler):
    def upload_file(self):
        name = rndstr()
        headers = {'Content-Length': self.request.headers['Content-Length']}
        connection._make_request('PUT', 'imatestbucket', name, headers, None, None, 1000.0, self.upload_complete, self.cloudify)


@web.stream_request_body
class RackSpaceUploader(WeirdUploadHandler):
    CLIENT = httpclient.AsyncHTTPClient()
    CONTAINER = 'uploading'
    KEY = ret.json()['access']['token']['id']
    URL = ret.json()['access']['serviceCatalog'][15]['endpoints'][0]['publicURL']


    def upload_file(self):
        headers = {
            'X-Auth-Token': self.KEY,
            'Content-Encoding': 'chunked',
         }

        url = '%s/%s/%s' % (self.URL, self.CONTAINER, self.name)

        request = httpclient.HTTPRequest(url, headers=headers, method='PUT', body_producer=self.cloudify)
        self.CLIENT.fetch(request, callback=self.upload_complete)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = Application([
        (r'/s3/?', S3Uploader),
        (r'/rackspace/?', RackSpaceUploader)
    ], debug=True)

    app.listen(7777)

    IOLoop.instance().start()
