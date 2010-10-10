#!/usr/bin/env python

USER_EMAIL = 'example@gmail.com'
USER_PASSWORD = 'your_password_here'

DOCUMENTS = {
    'boilertest': {
        # Google Docs key (from url)
        'key': '0AlXMOHKxzQVRdGt5aWV0UG9XaWVIVWVCYWRqVi11dGc',
        # Number of seconds to keep in memcache before refetching
        'ttl': 15,
        # Convert to JSON server-side?
        'convert': False
    }
}
