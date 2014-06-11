# -*- coding: utf8 -*-

from __future__ import absolute_import

from decimal import Decimal
from braspag.consts import PAYMENT_METHODS
from .base import BraspagTestCase


class AuthorizeCaptureRefundTest(BraspagTestCase):

    def test_authorize_capture_refund(self):
        self.braspag.authorize(self._authorize_callback, **{
            'request_id': '782a56e2-2dae-11e2-b3ee-080027d29772',
            'order_id': '2cf84e51-c45b-45d9-9f64-554a6e088668',
            'customer_id': '12345678900',
            'customer_name': u'José da Silva',
            'customer_email': 'jose123@dasilva.com.br',
            'transactions': [{
                'amount': Decimal(1000),
                'card_holder': 'Jose da Silva',
                'card_number': '0000000000000001',
                'card_security_code': '123',
                'card_exp_date': '05/2018',
                'save_card': True,
                'payment_method': PAYMENT_METHODS['Simulated']['BRL'],
            }],
        })
        self.wait(timeout=20)

    def _authorize_callback(self, response):
        assert response.success == True
        assert response.transactions[0]['amount'] == Decimal('1000.00')
        assert response.order_id == u'2cf84e51-c45b-45d9-9f64-554a6e088668'
        assert response.correlation_id == u'782a56e2-2dae-11e2-b3ee-080027d29772'
        assert response.transactions[0]['payment_method'] == 997
        assert response.transactions[0]['return_code'] == '4'
        assert response.transactions[0]['return_message'] == u'Operation Successful'
        assert response.transactions[0]['status'] == 1  # TODO: transformar em constante, tabela 13.10.1 do manual do pagador
        assert response.transactions[0]['status_message'] == 'Authorized'

        self.braspag.capture(self._capture_callback,
                          transaction_id=response.transactions[0]['braspag_transaction_id'],
                          amount=response.transactions[0]['amount'],
                          request_id=response.correlation_id,
                          )

    def _capture_callback(self, response):
        assert response.success == True
        assert response.transactions[0]['amount'] == Decimal('1000.00')
        assert response.correlation_id == u'782a56e2-2dae-11e2-b3ee-080027d29772'
        assert response.transactions[0]['return_code'] == '6' # TODO: transformar em constante
        assert response.transactions[0]['return_message'] == u'Operation Successful'
        assert response.transactions[0]['status'] == 0  # TODO: transformar em constante
        assert response.transactions[0]['status_message'] == 'Captured'

        self.braspag.refund(self._refund_callback,
                          transaction_id=response.transactions[0]['braspag_transaction_id'],
                          amount=response.transactions[0]['amount'],
                          request_id=response.correlation_id,
                          )

    def _refund_callback(self, response):
        assert response.success == True
        assert response.transactions[0]['amount'] == Decimal('1000.00')
        assert response.correlation_id == u'782a56e2-2dae-11e2-b3ee-080027d29772'
        assert response.transactions[0]['return_code'] == '0' # TODO: transformar em constante
        assert response.transactions[0]['return_message'] == u'Operation Successful - 1,000.00'
        assert response.transactions[0]['status'] == 0  # TODO: transformar em constante
        assert response.transactions[0]['status_message'] == 'Refund Confirmed'
        self.stop()
