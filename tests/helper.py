from __future__ import absolute_import, division, print_function

import os
import sys
import unittest2

from distutils.version import StrictVersion
from mock import patch, Mock

import stripe
from stripe import six
from stripe.six.moves.urllib.request import urlopen
from stripe.six.moves.urllib.error import HTTPError

from tests.request_mock import RequestMock


MOCK_MINIMUM_VERSION = '0.4.0'
MOCK_PORT = os.environ.get('STRIPE_MOCK_PORT', 12111)


try:
    resp = urlopen('http://localhost:%s/' % MOCK_PORT)
    info = resp.info()
except HTTPError as e:
    info = e.info()
except Exception:
    sys.exit("Couldn't reach stripe-mock at `localhost:%s`. Is "
             "it running? Please see README for setup instructions." %
             MOCK_PORT)

version = info.get('Stripe-Mock-Version')
if version != 'master' \
        and StrictVersion(version) < StrictVersion(MOCK_MINIMUM_VERSION):
    sys.exit("Your version of stripe-mock (%s) is too old. The minimum "
             "version to run this test suite is %s. Please "
             "see its repository for upgrade instructions." %
             (version, MOCK_MINIMUM_VERSION))


def with_stripe_attributes(**kwargs):
    def wrapper(cls):
        orig_setUp = getattr(cls, 'setUp')
        orig_tearDown = getattr(cls, 'tearDown')

        cls._RESTORE_ATTRIBUTES = list(kwargs.keys())

        def setUp(self):
            self._stripe_original_attributes = {}
            for attr in self._RESTORE_ATTRIBUTES:
                self._stripe_original_attributes[attr] = getattr(stripe, attr)
                setattr(stripe, attr, kwargs[attr])
            orig_setUp(self)

        def tearDown(self):
            orig_tearDown(self)
            for attr in self._RESTORE_ATTRIBUTES:
                setattr(stripe, attr, self._stripe_original_attributes[attr])

        cls.setUp = setUp
        cls.tearDown = tearDown

        return cls

    return wrapper


@with_stripe_attributes(
    api_base='http://localhost:%s' % MOCK_PORT,
    api_key='sk_test_123',
    client_id='ca_123'
)
class StripeMockTestCase(unittest2.TestCase):
    def setUp(self):
        super(StripeMockTestCase, self).setUp()

        self.request_mock = RequestMock()
        self.request_mock.start()

    def tearDown(self):
        super(StripeMockTestCase, self).tearDown()

        self.request_mock.stop()

    def stub_request(self, *args, **kwargs):
        return self.request_mock.stub_request(*args, **kwargs)

    def assert_requested(self, *args, **kwargs):
        return self.request_mock.assert_requested(*args, **kwargs)


@with_stripe_attributes(
    api_base=os.environ.get('STRIPE_API_BASE', stripe.api_base),
    api_key=os.environ.get(
            'STRIPE_API_KEY', 'tGN0bIwXnHdwOa85VABjPdSn8nWY7G7I'),
    api_version=os.environ.get('STRIPE_API_VERSION', '2017-04-06'),
    client_id=os.environ.get('STRIPE_CLIENT_ID', 'ca_test')
)
class StripeTestCase(unittest2.TestCase):
    pass


class StripeUnitTestCase(StripeTestCase):
    REQUEST_LIBRARIES = ['urlfetch', 'requests', 'pycurl', 'urllib.request']

    def setUp(self):
        super(StripeUnitTestCase, self).setUp()

        self.request_patchers = {}
        self.request_mocks = {}
        for lib in self.REQUEST_LIBRARIES:
            patcher = patch("stripe.http_client.%s" % (lib,))

            self.request_mocks[lib] = patcher.start()
            self.request_patchers[lib] = patcher

    def tearDown(self):
        super(StripeUnitTestCase, self).tearDown()

        for patcher in six.itervalues(self.request_patchers):
            patcher.stop()


class StripeApiTestCase(StripeTestCase):

    def setUp(self):
        super(StripeApiTestCase, self).setUp()

        self.requestor_patcher = patch('stripe.api_requestor.APIRequestor')
        self.requestor_class_mock = self.requestor_patcher.start()
        self.requestor_mock = self.requestor_class_mock.return_value

    def tearDown(self):
        super(StripeApiTestCase, self).tearDown()

        self.requestor_patcher.stop()

    def mock_response(self, res):
        self.requestor_mock.request = Mock(return_value=(res, 'reskey'))


class StripeResourceTest(StripeApiTestCase):

    def setUp(self):
        super(StripeResourceTest, self).setUp()
        self.mock_response({})
