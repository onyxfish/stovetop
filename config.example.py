#!/usr/bin/env python

APP_DOMAIN = 'example.appspot.com'

USER_EMAIL = 'example@gmail.com'
USER_PASSWORD = 'your_password_here'

DOCUMENTS = {
    # The name of the document to be used in URLs
    'exampledoc': {
        # Google spreadsheet key (from Google url)
        'key': '0AlXMOHKxzQVRdGt5aWV0UG9XaWVIVWVCYWRqVi11dGc',
        # Number of seconds to keep in memcache before refetching
        'ttl': 15,
        # Convert to JSON server-side?
        'convert': False
    }
}
