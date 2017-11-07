from __future__ import absolute_import, division, print_function

import stripe
from tests.helper import StripeMockTestCase


class CouponTest(StripeMockTestCase):
    def test_is_listable(self):
        resources = stripe.Coupon.list()
        self.assert_requested(
            'get',
            '/v1/coupons'
        )
        self.assertIsInstance(resources.data, list)
        self.assertIsInstance(resources.data[0], stripe.Coupon)

    def test_is_retrievable(self):
        resource = stripe.Coupon.retrieve('25OFF')
        self.assert_requested(
            'get',
            '/v1/coupons/25OFF'
        )
        self.assertIsInstance(resource, stripe.Coupon)

    def test_is_creatable(self):
        resource = stripe.Coupon.create(
            percent_off=25,
            duration='repeating',
            duration_in_months=3,
            id='250FF'
        )
        self.assert_requested(
            'post',
            '/v1/coupons'
        )
        self.assertIsInstance(resource, stripe.Coupon)

    def test_is_saveable(self):
        resource = stripe.Coupon.retrieve('25OFF')
        resource.metadata['key'] = 'value'
        resource.save()
        self.assert_requested(
            'post',
            '/v1/coupons/%s' % resource.id
        )

    def test_is_modifiable(self):
        resource = stripe.Coupon.modify('25OFF', metadata={'key': 'value'})
        self.assert_requested(
            'post',
            '/v1/coupons/25OFF'
        )
        self.assertIsInstance(resource, stripe.Coupon)

    def test_is_deletable(self):
        resource = stripe.Coupon.retrieve('25OFF')
        resource.delete()
        self.assert_requested(
            'delete',
            '/v1/coupons/%s' % resource.id
        )
        self.assertIsInstance(resource, stripe.Coupon)
