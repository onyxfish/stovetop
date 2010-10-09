#!/usr/bin/env python

import logging
logging.getLogger().setLevel(logging.DEBUG)

from google.appengine.api import memcache
from google.appengine.api.urlfetch import fetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import config
from lib.escape import escapejs

CSV_URL = 'https://spreadsheets.google.com/pub?key=%(key)s&hl=en&output=csv'

class DocumentHandler(webapp.RequestHandler):
    def get(self, document_name):
        callback = self.request.get('callback')

        if not callback:
            return self.error(400)

        try:
            options = config.DOCUMENTS[document_name]
        except KeyError:
            return self.error(404)

        content = memcache.get(document_name)

        if not content:
            # TODO: handle http errors
            result = fetch(CSV_URL % options)
            csv = result.content

            if options['convert']:
                # TODO: convert to JSON
                # content = csv_to_json(csv)
                raise NotImplementedError('JSON conversion is not yet supported.')
            else:
                content = escapejs(csv)

            memcache.set(document_name, content, options['ttl'])
            logging.debug('set to cache')

        self.response.headers["Content-Type"] = "application/javascript"
        self.response.headers["Cache-Control"] = "no-cache"
        self.response.headers["Pragma"] = "no-cache"    
        self.response.out.write('%s("%s")' % (callback, content))

def main():
    application = webapp.WSGIApplication([(r'/(.*)', DocumentHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
