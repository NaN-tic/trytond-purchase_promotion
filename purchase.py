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
    promotion = fields.Function(fields.Char('Promotion',
        'on_change_with_promotion'))

    @fields.depends('product', 'purchase')
    def on_change_with_promotion(self, name=None):
        Promotion = Pool().get('purchase.promotion')

        if not self.product or not self.purchase or not self.purchase.party:
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
    def get_promotions(cls, line, pattern=None):
        company = Transaction().context.get('company')
        promotions = cls.search([
            ('company', '=', company)
            ])

        if pattern == None:
            pattern = {}
        pattern = pattern.copy()
        pattern.update(cls.get_pattern(line))

        for promotion in promotions:
            if promotion.match(pattern):
                return promotion

    @classmethod
    def get_pattern(cls, line):
        pattern = {}
        pattern['product'] = line.product.id
        pattern['supplier'] = line.purchase.party.id
        return pattern
