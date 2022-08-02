from flask import flash
from sqlalchemy.dialects.mysql import BOOLEAN
from flask_login import current_user

from hashkart.database import Column, Model, db
from hashkart.product.models import ProductVariant
from hashkart.discount.models import Voucher

MC_KEY_CART_BY_USER = "checkout:cart:user_id:{}"


class Cart(Model):
    __tablename__ = "checkout_cart"
    user_id = Column(db.Integer())
    voucher_code = Column(db.String(255))
    quantity = Column(db.Integer())
    shipping_address_id = Column(db.Integer())
    shipping_method_id = Column(db.Integer())

    @property
    def subtotal(self):
        return sum(line.subtotal for line in self)

    @property
    def total(self):
        return self.subtotal + self.shipping_method_price - self.discount_amount

    @property
    def discount_amount(self):
        return self.voucher.get_vouchered_price(self) if self.voucher_code else 0

    @classmethod
    def get_current_user_cart(cls):
        if current_user.is_authenticated:
            cart = cls.get_cart_by_user_id(current_user.id)
        else:
            cart = None
        return cart

    def get_product_price(self, product_id):
        price = 0
        for line in self:
            if line.product.id == product_id:
                price += line.subtotal
        return price

    def get_category_price(self, category_id):
        price = 0
        for line in self:
            if line.category.id == category_id:
                price += line.subtotal
        return price

    @property
    def voucher(self):
        if self.voucher_code:
            return Voucher.get_by_code(self.voucher_code)
        return None

    def __repr__(self):
        return f"Cart(quantity={self.quantity})"

    def __iter__(self):
        return iter(self.lines)

    def __len__(self):
        return len(self.lines)

    def update_quantity(self):
        self.quantity = sum(line.quantity for line in self)
        if self.quantity == 0:
            self.delete()
        else:
            self.save()
        return self.quantity


class ShippingMethod(Model):
    __tablename__ = "checkout_shippingmethod"
    title = Column(db.String(255), nullable=False)
    price = Column(db.DECIMAL(10, 2))

    def __str__(self):
        return self.title + "   $" + str(self.price)