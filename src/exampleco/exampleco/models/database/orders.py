from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship

from . import Base
from ..mixin_models import JsonModelMixin


class Order(Base, JsonModelMixin):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    description = Column(String(256))
    status = Column(String(64), nullable=True)
    created_on = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    modified_on = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text(
            'CURRENT_TIMESTAMP'),
        server_onupdate=text('CURRENT_TIMESTAMP')
    )
    service = relationship("OrderItem", back_populates="order")

    json_fields = ("id", "description", "created_on", "modified_on", "service", "status")

    def __repr__(self) -> str:
        return "<Order(id='{}', description='{}', service='{}', created_on='{}')>".format(self.id, self.description, self.service, self.created_on)


class OrderSchema(SQLAlchemySchema):
    class Meta:
        model = Order
        load_instance = True

    id = fields.Integer()
    description = fields.String()
    # status = fields.String()
    created_on = fields.DateTime()
    modified_on = fields.DateTime()
