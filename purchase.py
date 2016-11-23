#This file is part mifarma module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, MatchMixin, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, If
from trytond.transaction import Transaction

__all__ = ['PurchaseLine', 'PurchasePromotion']
__metaclass__ = PoolMeta


class PurchaseLine:
    __name__ = 'purchase.line'

    promotion = fields.Char('Promotion', states={
        'readonly': True,
        })

    def on_change_product(self):
        super(PurchaseLine, self).on_change_product()
        if not self.product:
            self.promotion = None
            return
        pool = Pool()
        Promotion = pool.get('purchase.promotion')
        promotion = Promotion.get_promotions(self)
        self.promotion = promotion.rec_name


class PurchasePromotion(ModelSQL, ModelView, MatchMixin):
    'Promotions for purchases'
    __name__ = 'purchase.promotion'
    _rec_name = 'promotion'

    supplier = fields.Many2One('party.party', 'Supplier')
    sequence = fields.Integer('Sequence')
    product = fields.Many2One('product.product', 'Product')
    promotion = fields.Char('Promotion', required=True)
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
        ])

    @classmethod
    def __setup__(cls):
        super(PurchasePromotion, cls).__setup__()
        cls._order = [('sequence', 'ASC')]

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @classmethod
    def get_promotions(cls, purchase, pattern=None):
        current_company = Transaction().context.get('company')
        promotions = cls.search([
            ('product', '=', purchase.product.id),
            ('company', '=', current_company)
            ])
        if pattern == None:
            pattern = {}
        pattern = pattern.copy()
        for promotion in promotions:
            pattern.update(promotion.get_pattern(purchase))
            if promotion.match(pattern):
                return promotion

    def get_pattern(self, purchase):
        pattern = {}
        if not self.product:
            return pattern
        pattern['product'] = purchase.product
        return pattern

    def match(self, pattern):
        if 'product' in pattern:
            pattern = pattern.copy()
            if self.product != pattern.pop('product'):
                return False
        return super(PurchasePromotion, self).match(pattern)
