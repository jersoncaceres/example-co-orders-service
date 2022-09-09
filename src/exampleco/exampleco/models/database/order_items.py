from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from . import Base
from .orders import OrderSchema
from .services import ServiceSchema


class OrderItem(Base):
    __tablename__ = 'order_items'

    order_id = Column(ForeignKey("order.id"), primary_key=True)
    service_id = Column(ForeignKey("services.id"), primary_key=True)
    service = relationship("Service")

    order = relationship(
        "Order",
        foreign_keys=[order_id],
        primaryjoin="OrderItem.order_id == Order.id",
        cascade="all,delete",
    )

    def __repr__(self) -> str:
        return "<OrderItem(order_id='{}', service='{}')>".format(self.order_id, self.service)


class OrderItemSchema(SQLAlchemySchema):
    class Meta:
        model = OrderItem
        load_instance = True

    id = fields.Integer()
    order = fields.Nested(OrderSchema)
    service = fields.Nested(ServiceSchema)
