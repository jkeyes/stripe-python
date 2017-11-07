from __future__ import absolute_import, division, print_function

import stripe
from tests.helper import StripeMockTestCase


class BalanceTest(StripeMockTestCase):
    def test_is_retrievable(self):
        resource = stripe.Balance.retrieve()
        self.assert_requested(
            'get',
            '/v1/balance'
        )
        self.assertIsInstance(resource, stripe.Balance)
