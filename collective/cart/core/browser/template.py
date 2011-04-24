from Acquisition import aq_inner
from zope.component import getMultiAdapter, getUtility
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from collective.cart.core.interfaces import (
    IPortal,
    IProduct,
    IRegularExpression,
)
from collective.cart.core import CartMessageFactory as _


class CartFolderView(BrowserView):

    __call__ = ViewPageTemplateFile('templates/cart_folder.pt')


class CartTypeView(BrowserView):

    __call__ = ViewPageTemplateFile('templates/cart_type.pt')


class CartConfigView(BrowserView):

    template = ViewPageTemplateFile('templates/cart_config.pt')

    def __call__(self):
        self.request.set('disable_border', True)
        if not self.has_cart_folder:
            message = _(u"Please add CartFolder first.")
            IStatusMessage(self.request).addStatusMessage(message, type='warn')
        return self.template()

    @property
    def has_cart_folder(self):
        context = aq_inner(self.context)
        return IPortal(context).cart_folder
#        try:
#            return IPortal(context).cart_folder
#        except AttributeError:
#            return None
#        portal = getToolByName(context, 'portal_url').getPortalObject()
#        catalog = getToolByName(context, 'portal_catalog')
#        return getMultiAdapter((portal, catalog), IPortalCatalog).cart_folder

class EditProductView(BrowserView):
    template = ViewPageTemplateFile('templates/edit_product.pt')

    def __call__(self):
        form = self.request.form
        if form.get('form.button.save', None) is not None:
            context = aq_inner(self.context)
            product = IProduct(context)
            re = getUtility(IRegularExpression)
#            fields = ['price', 'weight', 'height', 'width', 'depth']
            price = form.get('price')
            if re.float(price):
                product.price = IPortal(context).decimal_price(price)
#            fields = ['price']
#            self.set_floats(form, fields, product)
            unlimited_stock = form.get('unlimited_stock')
            if unlimited_stock == 'on':
                product.unlimited_stock = True
            if unlimited_stock != 'on':
                product.unlimited_stock = False
            stock = form.get('stock')
            if re.integer(stock):
                product.stock = int(stock)
            max_addable_quantity = form.get('max_addable_quantity')
            if re.integer(max_addable_quantity):
                product.max_addable_quantity = int(max_addable_quantity)
#            product.weight_unit = form.get('weight_unit')
        return self.template()

#    def set_floats(self, form, fields, product):
#        re = getUtility(IRegularExpression)
#        for field in fields:
#            value = form.get(field)
#            if re.float(value):
#                setattr(product, field, value)

    def fields(self):
        context = aq_inner(self.context)
        product = IProduct(context)
        res = []
        price = dict(
            label = _(u'Price'),
            description = 'Input Price.',
            field = '<input type="text" name="price" id="price" value="%s" size="6" />' %product.price,
        )
        res.append(price)
        unlimited_stock_field = '<input type="checkbox" name="unlimited_stock" id="unlimited_stock" value="on" />'
        if product.unlimited_stock == True:
            unlimited_stock_field = '<input type="checkbox" name="unlimited_stock" id="unlimited_stock" value="on" checked="checked" />'
        unlimited_stock = dict(
            label = _(u'Unlimited Stock'),
            description = _(u'Check this if you have unlimited amount of stock.'),
            field = unlimited_stock_field,
        )
        res.append(unlimited_stock)
        stock = dict(
            label = _(u'Stock'),
            description = 'Input Stock.',
            field = '<input type="text" name="stock" id="stock" value="%s" size="5" />' %product.stock,
        )
        res.append(stock)
        max_addable_quantity = dict(
            label = _(u'Maximum Addable Quantity'),
            description = _('You need to specify this if you checked Unlimited Stock.'),
            field = '<input type="text" name="max_addable_quantity" id="max_addable_quantity" value="%s" size="5" />' % product.max_addable_quantity,
        )
        res.append(max_addable_quantity)
#        weight_unit = dict(
#            label = _(u'Weight Unit'),
#            description = _('Select Weight Unit.'),
#            field = self.select_weight_unit(product),
#        )
#        res.append(weight_unit)
#        weight =dict(
#            label = _('Weight'),
#            description = _('Input Weight.'),
#            field = '<input type="text" name="weight" id="weight" value="%s" size="5" />' % product.weight,
#        )
#        res.append(weight)
#        height =dict(
#            label = _('Height'),
#            description = _('Input Height in cm unit.'),
#            field = '<input type="text" name="height" id="height" value="%s" size="5" />' % product.height,
#        )
#        res.append(height)
#        width = dict(
#            label = _('Width'),
#            description = _('Input Width in cm unit.'),
#            field = '<input type="text" name="width" id="width" value="%s" size="5" />' % product.width,
#        )
#        res.append(width)
#        depth = dict(
#            label = _('Depth'),
#            description = _('Input Depth in cm unit.'),
#            field = '<input type="text" name="depth" id="depth" value="%s" size="5" />' % product.depth,
#        )
#        res.append(depth)
        return res

#    def select_weight_unit(self, product):
#        html = '<select name="weight_unit" id="weight_unit">'
#        keys = ['g', 'kg']
#        for key in keys:
#            if product.weight_unit == key:
#                html += '<option value="%s" selected="selected">%s</option>' % (key, key)
#            else:
#                html += '<option value="%s">%s</option>' % (key, key)
#        html += '</select>'
#        return html

    @property
    def current_url(self):
        """Returns current url"""
        context_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_context_state')
        return context_state.current_page_url()

class CartView(BrowserView):
    __call__ = ViewPageTemplateFile('templates/cart.pt')

    def has_contents(self):
        context = aq_inner(self.context)
#        return context.restrictedTraverse('has-cart-contents')()
        return context.restrictedTraverse('products')()
