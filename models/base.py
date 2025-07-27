"""
Base database setup
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class TimestampMixin:
    """Mixin for adding timestamp fields"""
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class BaseModel(db.Model, TimestampMixin):
    """Base model with common fields"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def save(self):
        """Save model to database"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete model from database"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_or_404(cls, id):
        """Get model by ID or raise 404"""
        return cls.query.get_or_404(id)