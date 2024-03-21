import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'messages'

    sender_name = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    recipient_name = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    message = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    send_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                     default=datetime.datetime.now)