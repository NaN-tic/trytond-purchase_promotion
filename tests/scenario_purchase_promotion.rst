===========================
Scenario Purchase Promotion
===========================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> today = datetime.date.today()

Create config::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install Purchase Promotion::

	>>> Module = Model.get('ir.module')
    >>> module, = Module.find([('name', '=', 'purchase_promotion')])
    >>> Module.install ([module.id], config.context)
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> expense = accounts['expense']

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create supplier::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier', supplier=True)
    >>> supplier.save()

Create Product::

    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> UOM = Model.get('product.uom')
    >>> product_template = ProductTemplate()
    >>> product_template.name = 'Test product'
    >>> product_template.type = 'goods'
    >>> product_template.purchasable = True
    >>> product_template.account_expense = expense
    >>> product_template.list_price = Decimal('10.00')
    >>> product_template.cost_price = Decimal('08.00')
    >>> product_template.default_uom, = UOM.find([('name', '=', 'Unit')])
    >>> product_template.save()
    >>> product, = Product.find([('name', '=', product_template.name)])

Create promotion::

    >>> PurchasePromotion = Model.get('purchase.promotion')
    >>> purchase_promotion = PurchasePromotion()
    >>> purchase_promotion.promotion = 'Test promotion'
    >>> purchase_promotion.product = product
    >>> purchase_promotion.supplier = supplier
    >>> purchase_promotion.sequence = 20
    >>> purchase_promotion.save()

Create purchase::

    >>> Purchase = Model.get('purchase.purchase')
    >>> purchase = Purchase()
    >>> purchase.party = supplier
    >>> purchase.description = "Test purchase for promotions"
    >>> purchase_line = purchase.lines.new()
    >>> purchase_line.product = product
    >>> purchase_line.description = "Purchase line with promotion"
    >>> purchase_line.quantity = 2
    >>> purchase_line.promotion
    u'Test promotion'
    >>> purchase.save()

Create second promotion with higher sequence::

    >>> purchase_promotion2 = PurchasePromotion()
    >>> purchase_promotion2.promotion = 'Promotion 2'
    >>> purchase_promotion2.product = product
    >>> purchase_promotion2.supplier = supplier
    >>> purchase_promotion2.sequence = 10
    >>> purchase_promotion2.save()

    >>> promotions = PurchasePromotion.find([])
    >>> len(promotions)
    2

Create purchase::

    >>> purchase2 = Purchase()
    >>> purchase2.party = supplier
    >>> purchase2.description = "Second purchase"
    >>> purchase2_line = purchase.lines.new()
    >>> purchase2_line.product = product
    >>> purchase2_line.description = "Second purchase with second promotion"
    >>> purchase2_line.quantity = 2
    >>> purchase2_line.promotion
    u'Promotion 2'
    >>> purchase.save()

Create purchase with no product::

    >>> purchase3 = Purchase()
    >>> purchase3.party = supplier
    >>> purchase3.description = "Third purchase"
    >>> purchase3_line = purchase.lines.new()
    >>> purchase3_line.description = "Third purchase with no promotion"
    >>> purchase3_line.quantity = 2
    >>> purchase3_line.unit_price = Decimal('00.00')
    >>> purchase3_line.promotion
    >>> purchase3.save()
