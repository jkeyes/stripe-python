from __future__ import absolute_import, division, print_function

from mock import patch, ANY

import stripe


class RequestMock(object):
    def __init__(self):
        self._real_request = stripe.api_requestor.APIRequestor.request
        self._stub_request_handler = StubRequestHandler()

    def start(self):
        self.constructor_patcher = patch(
            'stripe.api_requestor.APIRequestor.__init__',
            side_effect=stripe.api_requestor.APIRequestor.__init__,
            autospec=True)
        self.constructor_spy = self.constructor_patcher.start()

        self.request_patcher = patch(
            'stripe.api_requestor.APIRequestor.request',
            side_effect=self._patched_request,
            autospec=True)
        self.request_spy = self.request_patcher.start()

    def stop(self):
        self.request_patcher.stop()
        self.constructor_patcher.stop()

    def _patched_request(self, requestor, method, url, *args, **kwargs):
        response_body = self._stub_request_handler.get_response(method, url)
        if response_body is not None:
            return response_body, stripe.api_key

        return self._real_request(requestor, method, url, *args, **kwargs)

    def stub_request(self, method, url, response_body={}):
        self._stub_request_handler.register(method, url, response_body)

    def assert_api_version(self, expected_api_version):
        # Note that this method only checks that an API version was provided
        # as a keyword argument in APIRequestor's constructor, not as a
        # positional argument.

        if 'api_version' not in self.constructor_spy.call_args[1]:
            msg = ("Expected APIRequestor to have been constructed with "
                   "api_version='%s'. No API version was provided." %
                   expected_api_version)
            raise AssertionError(msg)

        actual_api_version = self.constructor_spy.call_args[1]['api_version']
        if actual_api_version != expected_api_version:
            msg = ("Expected APIRequestor to have been constructed with "
                   "api_version='%s'. Constructed with api_version='%s' "
                   "instead." % (expected_api_version, actual_api_version))
            raise AssertionError(msg)

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
