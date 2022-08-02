from .extensions import db

Column = db.Column
MC_KEY_GET_BY_ID = "global:{}:{}"


class CRUDMixin:
    @classmethod
    def create(cls, **kwargs):
        props = cls.get_db_props(kwargs)
        obj = cls(**kwargs)
        obj.save()
        cls.update_db_props(obj, props)
        return obj

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()

   
    @classmethod
    def get_or_create(cls, **kwargs):
        props = cls.get_db_props(kwargs)
        if not kwargs:
            return None, False
        obj = cls.query.filter_by(**kwargs).first()
        if obj:
            return obj, False
        obj = cls(**kwargs)
        obj.save()
        cls.update_db_props(obj, props)
        return obj, True


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True