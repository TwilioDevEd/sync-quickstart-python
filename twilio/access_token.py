import time
import base64
import hashlib
import hmac

try:
    import json
except ImportError:
    import simplejson as json


class IpMessagingGrant(object):
    """ Grant to access Twilio IP Messaging """
    def __init__(self, service_sid=None, endpoint_id=None,
                 deployment_role_sid=None, push_credential_sid=None):
        self.service_sid = service_sid
        self.endpoint_id = endpoint_id
        self.deployment_role_sid = deployment_role_sid
        self.push_credential_sid = push_credential_sid

    @property
    def key(self):
        return "ip_messaging"

    def to_payload(self):
        grant = {}
        if self.service_sid:
            grant['service_sid'] = self.service_sid
        if self.endpoint_id:
            grant['endpoint_id'] = self.endpoint_id
        if self.deployment_role_sid:
            grant['deployment_role_sid'] = self.deployment_role_sid
        if self.push_credential_sid:
            grant['push_credential_sid'] = self.push_credential_sid

        return grant


class SyncGrant(object):
    """ Grant to access Twilio Sync """
    def __init__(self, service_sid=None, endpoint_id=None,
                 deployment_role_sid=None, push_credential_sid=None):
        self.service_sid = service_sid
        self.endpoint_id = endpoint_id
        self.deployment_role_sid = deployment_role_sid
        self.push_credential_sid = push_credential_sid

    @property
    def key(self):
        return "data_sync"

    def to_payload(self):
        grant = {}
        if self.service_sid:
            grant['service_sid'] = self.service_sid
        if self.endpoint_id:
            grant['endpoint_id'] = self.endpoint_id
        if self.deployment_role_sid:
            grant['deployment_role_sid'] = self.deployment_role_sid
        if self.push_credential_sid:
            grant['push_credential_sid'] = self.push_credential_sid

        return grant


class ConversationsGrant(object):
    """ Grant to access Twilio Conversations """
    def __init__(self, configuration_profile_sid=None):
        self.configuration_profile_sid = configuration_profile_sid

    @property
    def key(self):
        return "rtc"

    def to_payload(self):
        grant = {}
        if self.configuration_profile_sid:
            grant['configuration_profile_sid'] = self.configuration_profile_sid

        return grant


class AccessToken(object):
    """ Access Token used to access Twilio Resources """
    def __init__(self, account_sid, signing_key_sid, secret,
                 identity=None, ttl=3600, nbf=None):
        self.account_sid = account_sid
        self.signing_key_sid = signing_key_sid
        self.secret = secret

        self.identity = identity
        self.ttl = ttl
        self.nbf = nbf
        self.grants = []

    def add_grant(self, grant):
        self.grants.append(grant)

    def to_jwt(self, algorithm='HS256'):
        now = int(time.time())

        grants = {}
        if self.identity:
            grants["identity"] = self.identity

        for grant in self.grants:
            grants[grant.key] = grant.to_payload()

        payload = {
            "jti": '{0}-{1}'.format(self.signing_key_sid, now),
            "iss": self.signing_key_sid,
            "sub": self.account_sid,
            "exp": now + self.ttl,
            "grants": grants
        }

        if self.nbf is not None:
            payload['nbf'] = self.nbf

        return _encode(payload, self.secret, algorithm=algorithm)

    def __str__(self):
        return self.to_jwt()

        
def _base64url_encode(input):
    return base64.urlsafe_b64encode(input).decode('utf-8').replace('=', '')

    
signing_methods = {
    'HS256': lambda msg, key: hmac.new(key, msg, hashlib.sha256).digest(),
    'HS384': lambda msg, key: hmac.new(key, msg, hashlib.sha384).digest(),
    'HS512': lambda msg, key: hmac.new(key, msg, hashlib.sha512).digest(),
}


def _binary(txt):
    return txt.encode('utf-8')


def _encode(payload, key, algorithm='HS256'):
    segments = []
    header = {"typ": "JWT", "alg": algorithm, "cty": "twilio-fpa;v=1"}
    segments.append(_base64url_encode(_binary(json.dumps(header))))
    segments.append(_base64url_encode(_binary(json.dumps(payload))))
    sign_input = '.'.join(segments)
    try:
        signature = signing_methods[algorithm](_binary(sign_input), _binary(key))
    except KeyError:
        raise NotImplementedError("Algorithm not supported")
    segments.append(_base64url_encode(signature))
    return '.'.join(segments)
