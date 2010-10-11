#!/usr/bin/env python

import csv
import logging
logging.getLogger().setLevel(logging.DEBUG)

import gdata.gauth
import gdata.docs.client
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

        if True:
            csv_data = self.fetch_csv(options)

            if options['convert']:
                content = self.csv_to_json(csv_data)
            else:
                content = '"%s"' % escapejs(csv_data)

            memcache.set(document_name, content, options['ttl'])

        self.response.headers["Content-Type"] = "application/javascript"
        self.response.headers["Cache-Control"] = "no-cache"
        self.response.headers["Pragma"] = "no-cache"    
        self.response.out.write('%s(%s)' % (callback, content))

    def fetch_csv(self, options):
        """
        Retrieves a single Google spreadsheet as CSV using ClientLogin
        authentication.

        TODO: handle retries and timeouts on auth calls
        TOOD: handle retries and timeouts on content fetching
        """
        client = gdata.docs.client.DocsClient()
        client.ClientLogin(
            config.USER_EMAIL, config.USER_PASSWORD, config.APP_DOMAIN)

        spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService()
        spreadsheets_client.ClientLogin(
            config.USER_EMAIL, config.USER_PASSWORD, config.APP_DOMAIN)

        docs_token = client.auth_token
        client.auth_token = gdata.gauth.ClientLoginToken(
            spreadsheets_client.GetClientLoginToken())

        return client.get_file_content(CSV_URL % options)

    def csv_to_json(self, csv_data):
        """
        Converts a Google-formatted CSV (\n line-endings) to JSON.
        """
        fileish = csv_data.split('\n')
        reader = csv.DictReader(fileish)
        return [row for row in reader] 

def main():
    application = webapp.WSGIApplication([(r'/(.*)', DocumentHandler)],
                                        debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
