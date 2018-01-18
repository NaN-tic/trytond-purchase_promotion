# This file is part of the purchase_promotion module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import fields

__all__ = ['PurchaseRequest']


class PurchaseRequest:
    __metaclass__ = PoolMeta
    __name__ = 'purchase.request'
    promotion = fields.Function(fields.Char('Promotion'), 'get_promotion')

    @classmethod
    def get_promotion(cls, requests, names):
        Promotion = Pool().get('purchase.promotion')

        result = {n: {r.id: None for r in requests} for n in names}
        for name in names:
            for request in requests:
                promotion = Promotion.get_promotions(request)
                if promotion:
                    result[name][request.id] = promotion.rec_name
        return result
