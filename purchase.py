#This file is part mifarma module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, MatchMixin, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, If
from trytond.transaction import Transaction

__all__ = ['PurchaseLine', 'PurchasePromotion']


class PurchaseLine:
    __metaclass__ = PoolMeta
    __name__ = 'purchase.line'
    promotion = fields.Function(fields.Char('Promotion', states={
            'readonly': True,
            }),
        'on_change_with_promotion')

    @fields.depends('product', 'purchase')
    def on_change_with_promotion(self, name=None):
        pool = Pool()
        Promotion = pool.get('purchase.promotion')
        if not self.product or not self.purchase.party:
            return
        promotion = Promotion.get_promotions(self)
        if promotion and promotion.rec_name:
            return promotion.rec_name


class PurchasePromotion(ModelSQL, ModelView, MatchMixin):
    'Promotions for purchases'
    __name__ = 'purchase.promotion'
    _rec_name = 'promotion'
    supplier = fields.Many2One('party.party', 'Supplier',
        domain=[
            ('supplier', '=', True)
        ])
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
        if not self.product and not self.supplier:
            return pattern
        pattern['product'] = purchase.product
        pattern['supplier'] = purchase.purchase.party
        return pattern

    def _does_pattern_match(self, pattern):
        return self.product == pattern.get('product') or \
            self.supplier == pattern.get('supplier')

    def match(self, pattern):
        pattern = pattern.copy()
        if self._does_pattern_match(pattern):
            return True
        return super(PurchasePromotion, self).match(pattern)
