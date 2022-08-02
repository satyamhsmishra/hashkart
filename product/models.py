import itertools

from flask import url_for, request, current_app
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import desc
from hashkart.database import Column, Model, db


class Product(Model):
    __tablename__ = "product_product"
    title = Column(db.String(255), nullable=False)
    on_sale = Column(db.Boolean(), default=True)
    rating = Column(db.DECIMAL(8, 2), default=5.0)
    sold_count = Column(db.Integer(), default=0)
    review_count = Column(db.Integer(), default=0)
    basic_price = Column(db.DECIMAL(10, 2))
    category_id = Column(db.Integer())
    is_featured = Column(db.Boolean(), default=False)
    product_type_id = Column(db.Integer())
    attributes = Column(MutableDict.as_mutable(db.JSON()))
    description = Column(db.Text())


    def __str__(self):
        return self.title

    def __iter__(self):
        return iter(self.variants)

    def get_absolute_url(self):
        return url_for("product.show", id=self.id)


   
    def delete(self):
        need_del_collection_products = ProductCollection.query.filter_by(
            product_id=self.id
        ).all()
        for item in itertools.chain(
            self.images, self.variant, need_del_collection_products
        ):
            item.delete(commit=False)
        db.session.delete(self)
        db.session.commit()


class Category(Model):
    __tablename__ = "product_category"
    title = Column(db.String(255), nullable=False)
    parent_id = Column(db.Integer(), default=0)
    background_img = Column(db.String(255))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return url_for("product.show_category", id=self.id)


class ProductVariant(Model):
    __tablename__ = "product_variant"
    sku = Column(db.String(32), unique=True)
    title = Column(db.String(255))
    price_override = Column(db.DECIMAL(10, 2), default=0.00)
    quantity = Column(db.Integer(), default=0)
    quantity_allocated = Column(db.Integer(), default=0)
    product_id = Column(db.Integer(), default=0)
    attributes = Column(MutableDict.as_mutable(db.JSON()))

    def __str__(self):
        return self.title or self.sku

    def display_product(self):
        return f"{self.product} ({str(self)})"

    def get_absolute_url(self):
        return url_for("product.show", id=self.product.id)

   
class ProductAttribute(Model):
    __tablename__ = "product_attribute"
    title = Column(db.String(255), nullable=False)

    def __str__(self):
        return self.title

    def update_values(self, new_values):
        origin_values = list(value.title for value in self.values)
        need_del = set()
        need_add = set()
        for value in self.values:
            if value.title not in new_values:
                need_del.add(value)
        for value in new_values:
            if value not in origin_values:
                need_add.add(value)
        for value in need_del:
            value.delete(commit=False)
        for value in need_add:
            new = AttributeChoiceValue(title=value, attribute_id=self.id)
            db.session.add(new)
        db.session.commit()


class AttributeChoiceValue(Model):
    __tablename__ = "product_attribute_value"
    title = Column(db.String(255), nullable=False)
    attribute_id = Column(db.Integer())

    def __str__(self):
        return self.title


class ProductImage(Model):
    __tablename__ = "product_image"
    image = Column(db.String(255))
    order = Column(db.Integer())
    product_id = Column(db.Integer())

    def __str__(self):
        return url_for("static", filename=self.image, _external=True)


class Collection(Model):
    __tablename__ = "product_collection"
    title = Column(db.String(255), nullable=False)
    background_img = Column(db.String(255))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return url_for("product.show_collection", id=self.id)


    def update_products(self, new_products):
        origin_ids = (
            ProductCollection.query.with_entities(ProductCollection.product_id)
            .filter_by(collection_id=self.id)
            .all()
        )
        origin_ids = set(i for i, in origin_ids)
        new_products = set(int(i) for i in new_products)
        need_del = origin_ids - new_products
        need_add = new_products - origin_ids
        for id in need_del:
            ProductCollection.query.filter_by(
                collection_id=self.id, product_id=id
            ).first().delete(commit=False)
        for id in need_add:
            new = ProductCollection(collection_id=self.id, product_id=id)
            db.session.add(new)
        db.session.commit()

    def delete(self):
        need_del = ProductCollection.query.filter_by(collection_id=self.id).all()
        for item in need_del:
            item.delete(commit=False)
        db.session.delete(self)
        db.session.commit()
        if self.background_img:
            image = current_app.config["STATIC_DIR"] / self.background_img
            if image.exists():
                image.unlink()


class ProductCollection(Model):
    __tablename__ = "product_collection_product"
    product_id = Column(db.Integer())
    collection_id = Column(db.Integer())


def get_product_list_context(query, obj):
    """
    obj: collection or category, to get it`s attr_filter.
    """
    args_dict = {}
    price_from = request.args.get("price_from", None, type=int)
    price_to = request.args.get("price_to", None, type=int)
    if price_from:
        query = query.filter(Product.basic_price > price_from)
    if price_to:
        query = query.filter(Product.basic_price < price_to)
    args_dict.update(price_from=price_from, price_to=price_to)

    sort_by_choices = {"title": "title", "price": "price"}
    arg_sort_by = request.args.get("sort_by", "")
    is_descending = False
    if arg_sort_by.startswith("-"):
        is_descending = True
        arg_sort_by = arg_sort_by[1:]
    if arg_sort_by in sort_by_choices:
        if is_descending:
            query = query.order_by(desc(getattr(Product, arg_sort_by)))
        else:
            query = query.order_by(getattr(Product, arg_sort_by))
    now_sorted_by = arg_sort_by or "title"
    args_dict.update(
        sort_by_choices=sort_by_choices,
        now_sorted_by=now_sorted_by,
        is_descending=is_descending,
    )

    args_dict.update(default_attr={})
    attr_filter = obj.attr_filter
    for attr in attr_filter:
        value = request.args.get(attr.title)
        if value:
            query = query.filter(Product.attributes.__getitem__(str(attr.id)) == value)
            args_dict["default_attr"].update({attr.title: int(value)})
    args_dict.update(attr_filter=attr_filter)

    if request.args:
        args_dict.update(clear_filter=True)

    return args_dict, query
