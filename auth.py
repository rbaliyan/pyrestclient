import requests

class BearerAuth(requests.auth.AuthBase):
    token = None

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class TokenAuth(requests.auth.AuthBase):
    token = None

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Token token=" + self.token
        return r
