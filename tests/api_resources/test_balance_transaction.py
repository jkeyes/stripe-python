from __future__ import absolute_import, division, print_function

import stripe
from tests.helper import StripeMockTestCase


TEST_RESOURCE_ID = 'txn_123'


class BalanceTransactionTest(StripeMockTestCase):
    def test_is_listable(self):
        resources = stripe.BalanceTransaction.list()
        self.assert_requested(
            'get',
            '/v1/balance/history',
        )
        self.assertIsInstance(resources.data, list)
        self.assertIsInstance(resources.data[0], stripe.BalanceTransaction)
