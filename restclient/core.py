import base64
import copy
import hashlib
import collections
import json
import os
import random
import sys
import threading
import datetime
import traceback
import requests
import argparse
import time

from .limit import Limiter


class Client(object):
    def __init__(self, host, auth, prefix="", headers=None, timeout=None):
        self.host = host
        self.prefix = prefix
        self.session = requests.Session()
        self.session.auth = auth
        self.headers = headers or {}
        self.timeout = timeout
        self._limiter = Limiter(period=0.1)
        self._total_req = 0
        self._lock = threading.Lock()
        if self.host.endswith("/"):
            self.host = self.host[:-1]
        if self.prefix and not self.prefix.startswith("/"):
            self.prefix = "/" + self.prefix
        if self.prefix and self.prefix.endswith("/"):
            self.prefix = self.prefix[:-1]

    @classmethod
    def login(cls, host, username, password):
        params = {"username": username, "password": password}
        rsp = requests.post(host + "/auth/login", data=params)
        rsp.raise_for_status()
        data = rsp.json()
        return cls(host, data[0])

    def _stats(self):
        with self._lock:
            self._total_req += 1

    def _get_headers(self, opts=None):
        headers = copy.copy(self.headers)
        if opts and "headers" in opts:
            h = opts.pop("headers")
            headers.update(h)
        return headers

    def _get_url(self, path):
        if not path.startswith("/"):
            path = "/" + path
        
        return self.host + self.prefix + path

    def _http_method(self, method, path, **kwargs):
        f = getattr(self.session, method)
        kwargs["headers"] = self._get_headers(kwargs.get("headers"))

        if "data" in kwargs and (
            type(kwargs["data"]) == dict or type(kwargs["data"]) == list
        ):
            if method != "get":
                # convert body params to JSON
                kwargs["json"] = kwargs.pop("data")
                kwargs["headers"]['Content-Type'] = 'application/json'
            else:
                 # For get all params should be query params
                kwargs["params"] = kwargs.pop("data")

        # Generate URL
        url = self._get_url(path)        
        self._stats()
        with self._limiter:
            rsp = f(url, **kwargs)
        # Check Status
        if not rsp.ok:
            print(kwargs)
            print(rsp.text)
            
        # Raise Status
        rsp.raise_for_status()
        return rsp.json()

    def get(self, path, **kwargs):
        return self._http_method("get", path, **kwargs)

    def post(self, path, **kwargs):
        return self._http_method("post", path, **kwargs)

    def put(self, path, **kwargs):
        return self._http_method("put", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._http_method("patch", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._http_method("delete", path, **kwargs)
