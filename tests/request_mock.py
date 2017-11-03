from __future__ import absolute_import, division, print_function

from mock import patch, ANY

import stripe


class RequestMock(object):
    def __init__(self):
        self._real_request = stripe.api_requestor.APIRequestor.request
        self._stub_request_handler = StubRequestHandler()

    def start(self):
        self.request_patcher = patch(
            'stripe.api_requestor.APIRequestor.request',
            side_effect=self._patched_request,
            autospec=True)
        self.request_spy = self.request_patcher.start()

    def stop(self):
        self.request_patcher.stop()

    def _patched_request(self, requestor, method, url, *args, **kwargs):
        response_body = self._stub_request_handler.get_response(method, url)
        if response_body:
            return response_body, stripe.api_key

        return self._real_request(requestor, method, url, *args, **kwargs)

    def stub_request(self, method, url, response_body={}):
        self._stub_request_handler.register(method, url, response_body)

    def assert_requested(self, method, url, params=ANY, headers=ANY):
        called = False
        exception = None

        # Sadly, ANY does not match a missing optional argument, so we
        # check all the possible signatures of the request method
        possible_called_args = [
            (ANY, method, url),
            (ANY, method, url, params),
            (ANY, method, url, params, headers),
        ]

        for args in possible_called_args:
            try:
                self.request_spy.assert_called_with(*args)
            except AssertionError as e:
                exception = e
            else:
                called = True
                break

        if not called:
            raise exception


class StubRequestHandler(object):
    def __init__(self):
        self._entries = {}

    def register(self, method, url, response_body={}):
        self._entries[(method, url)] = response_body

    def get_response(self, method, url):
        if (method, url) in self._entries:
            response_body = self._entries.pop((method, url))
            return response_body

        return None
