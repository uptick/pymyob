from __future__ import unicode_literals

import datetime

from requests_oauthlib import OAuth2Session

from .constants import ACCESS_TOKEN_URL, AUTHORIZE_URL, MYOB_PARTNER_BASE_URL


class PartnerCredentials():
    """An object wrapping the 3-step OAuth2 process for Partner MYOB API access."""
    def __init__(self, consumer_key, consumer_secret, callback_uri,
                 verified=False,
                 oauth_token=None,
                 oauth_expires_at=None, oauth_authorization_expires_at=None,
                 oauth_session_handle=None, scope=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.callback_uri = callback_uri

        self.verified = verified
        self._oauth = None
        self.oauth_token = oauth_token
        self.oauth_expires_at = oauth_expires_at

        self._oauth = OAuth2Session(consumer_key, redirect_uri=callback_uri)
        url, _ = self._oauth.authorization_url(MYOB_PARTNER_BASE_URL + AUTHORIZE_URL)
        self.url = url + '&scope=CompanyFile'

    @property
    def state(self):
        """Obtain the useful state of this credentials object so that
        we can reconstruct it independently.
        """
        return dict(
            (attr, getattr(self, attr))
            for attr in (
                'consumer_key', 'consumer_secret', 'callback_uri',
                'verified', 'oauth_token',
                'oauth_expires_at'
            )
            if getattr(self, attr) is not None
        )

    def verify(self, code):
        "Verify an OAuth session, retrieving an access token."
        response_state = self._oauth.fetch_token(
            MYOB_PARTNER_BASE_URL + ACCESS_TOKEN_URL,
            code=code,
            client_secret=self.consumer_secret,
        )

        self.access_token = response_state.get('access_token')
        self.refresh_token = response_state.get('refresh_token')

        self.oauth_expires_at = datetime.datetime.fromtimestamp(response_state.get('expires_at'))
        self.verified = True

    def expired(self, now=None):
        # Expiry might be unset if the user hasn't finished authenticating.
        if self.oauth_expires_at is None:
            return False

        # Allow a bit of time for clock differences and round trip times
        # to prevent false negatives. If users want the precise expiry,
        # they can use self.oauth_expires_at
        CONSERVATIVE_SECONDS = 30

        now = now or datetime.datetime.now()
        return self.oauth_expires_at <= (now + datetime.timedelta(seconds=CONSERVATIVE_SECONDS))

    def refresh(self):
        """ Refresh an expired token. """
        raise NotImplementedError
