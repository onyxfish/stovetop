#!/usr/bin/env python

import logging
logging.getLogger().setLevel(logging.DEBUG)

import gdata.alt.appengine
import gdata.gauth
import gdata.docs.data
import gdata.docs.client
import gdata.service
import gdata.spreadsheet.service
from google.appengine.api import memcache
from google.appengine.api.urlfetch import fetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import config
from lib.escape import escapejs

CSV_URL = 'http://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%(key)s&exportFormat=csv'
        
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
            csv = self.fetch_csv(options)

            if options['convert']:
                # TODO: convert to JSON
                # content = csv_to_json(csv)
                raise NotImplementedError('JSON conversion is not yet supported.')
            else:
                content = escapejs(csv)

            memcache.set(document_name, content, options['ttl'])

        self.response.headers["Content-Type"] = "application/javascript"
        self.response.headers["Cache-Control"] = "no-cache"
        self.response.headers["Pragma"] = "no-cache"    
        self.response.out.write('%s("%s")' % (callback, content))

    def fetch_csv(self, options):
        client = gdata.docs.client.DocsClient()
        #gdata.alt.appengine.run_on_appengine(client, store_tokens=True, single_user_mode=True)

        # TODO: handle retries and timeouts
        client.ClientLogin(config.USER_EMAIL, config.USER_PASSWORD, config.APP_DOMAIN)

        spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService()
        #gdata.alt.appengine.run_on_appengine(spreadsheets_client, store_tokens=True, single_user_mode=True)

        spreadsheets_client.ClientLogin(config.USER_EMAIL, config.USER_PASSWORD, config.APP_DOMAIN)

        docs_token = client.auth_token
        client.auth_token = gdata.gauth.ClientLoginToken(spreadsheets_client.GetClientLoginToken())

        # TODO: handle retries and timeouts
        return client.get_file_content(CSV_URL % options)

def main():
    application = webapp.WSGIApplication([(r'/(.*)', DocumentHandler)],
                                        debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
