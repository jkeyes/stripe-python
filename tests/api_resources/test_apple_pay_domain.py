from __future__ import absolute_import, division, print_function

import stripe
from tests.helper import StripeMockTestCase


class ApplePayDomainTest(StripeMockTestCase):
    def test_is_listable(self):
        resources = stripe.ApplePayDomain.list()
        self.assert_requested(
            'get',
            '/v1/apple_pay/domains'
        )
        self.assertIsInstance(resources.data, list)
        self.assertIsInstance(resources.data[0], stripe.ApplePayDomain)

    def test_is_retrievable(self):
        resource = stripe.ApplePayDomain.retrieve('apwc_123')
        self.assert_requested(
            'get',
            '/v1/apple_pay/domains/apwc_123'
        )
        self.assertIsInstance(resource, stripe.ApplePayDomain)

    def test_is_creatable(self):
        resource = stripe.ApplePayDomain.create(
            domain_name='test.com',
        )
        self.assert_requested(
            'post',
            '/v1/apple_pay/domains'
        )
        self.assertIsInstance(resource, stripe.ApplePayDomain)

    def test_is_deletable(self):
        resource = stripe.ApplePayDomain.retrieve('apwc_123')
        resource.delete()
        self.assert_requested(
            'delete',
            '/v1/apple_pay/domains/%s' % resource.id
        )
        self.assertIsInstance(resource, stripe.ApplePayDomain)
