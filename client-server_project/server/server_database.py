import os
import sys
from pprint import pprint

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from common.errors import ServerError


class ServerDB:
    Base = declarative_base()

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        username = Column(String(24), unique=True)
        last_connection = Column(DateTime)

        def __init__(self, username):
            self.username = username
            self.last_connection = datetime.now()

    class ActiveUser(Base):
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'), unique=True)
        ip_address = Column(String)
        port = Column(Integer)
        connection_time = Column(DateTime)

        def __init__(self, user, ip_address, port, connection_time):
            self.user = user
            self.ip_address = ip_address
            self.port = port
            self.connection_time = connection_time

    class LoginHistory(Base):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(Integer, ForeignKey('users.id'))
        ip_address = Column(String)
        port = Column(Integer)
        last_connection = Column(DateTime)

        def __init__(self, user, ip_address, port, last_connection):
            self.user = user
            self.ip_address = ip_address
            self.port = port
            self.last_connection = last_connection

    class UserContact(Base):
        __tablename__ = 'user_contacts'
        id = Column(Integer, primary_key=True)
        user = Column(Integer, ForeignKey('users.id'))
        contact = Column(Integer, ForeignKey('users.id'))

        def __init__(self, user, contact):
            self.user = user
            self.contact = contact

    class UserMessageHistory(Base):
        __tablename__ = 'user_message_history'
        id = Column(Integer, primary_key=True)
        user = Column(Integer, ForeignKey('users.id'))
        sent = Column(Integer)
        accepted = Column(Integer)

        def __init__(self, user):
            self.user = user
            self.sent = 0
            self.accepted = 0

        def __str__(self):
            return f'sent {self.sent}, accepted {self.accepted}'

    def __init__(self, db_path):
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )
        self.Base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.session.query(self.ActiveUser).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        user_query_result = self.session.query(self.User).filter_by(username=username)
        if user_query_result.count():
            user = user_query_result.first()
            user.last_connection = datetime.now()
        else:
            user = self.User(username)
            self.session.add(user)
            self.session.commit()
        new_active_user = self.ActiveUser(user.id, ip_address, port, datetime.now())
        self.session.add(new_active_user)
        new_login_history = self.LoginHistory(user.id, ip_address, port, datetime.now())
        self.session.add(new_login_history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.User).filter_by(username=username).first()
        self.session.query(self.ActiveUser).filter_by(user=user.id).delete()
        self.session.commit()

    def get_all_users(self):
        users = self.session.query(
            self.User.username,
            self.User.last_connection,
        )
        return users.all()

    def get_active_users(self):
        users = self.session.query(
            self.User.username,
            self.ActiveUser.ip_address,
            self.ActiveUser.port,
            self.ActiveUser.connection_time
        ).join(self.User)
        return users.all()

    def login_history(self, username=None):
        history = self.session.query(self.User.username,
                                     self.LoginHistory.last_connection,
                                     self.LoginHistory.ip_address,
                                     self.LoginHistory.port
                                     ).join(self.User)

        if username:
            history = history.filter(self.User.username == username)
        return history.all()

    def add_contact(self, username, contact_name):
        user = self.session.query(self.User).filter_by(username=username).first()
        contact = self.session.query(self.User).filter_by(username=contact_name).first()
        if contact and not self.session.query(self.UserContact).filter_by(user=user.id, contact=contact.id).count():
            new_user_contact = self.UserContact(user.id, contact.id)
            self.session.add(new_user_contact)
            self.session.commit()
        else:
            raise ServerError(f'{contact_name} is not a user')

    def remove_contact(self, username, contact_name):
        user = self.session.query(self.User).filter_by(username=username).first()
        contact = self.session.query(self.User).filter_by(username=contact_name).first()
        if contact:
            self.session.query(self.UserContact).filter(
                self.UserContact.user == user.id,
                self.UserContact.contact == contact.id
            ).delete()
            self.session.commit()

    def get_contacts(self, user):
        user = self.session.query(self.User).filter_by(username=user).first()
        user_contacts = self.session.query(self.UserContact, self.User.username).\
            filter_by(user=user.id).\
            join(self.User, self.UserContact.contact == self.User.id).all()
        return [username for contact, username in user_contacts]

    def database_handle_message(self, sender, recipient):
        sender = self.session.query(self.User).filter_by(username=sender).first().id
        recipient = self.session.query(self.User).filter_by(username=recipient).first().id
        sender_history = self.session.query(self.UserMessageHistory).filter_by(user=sender).first()
        if not sender_history:
            sender_history = self.UserMessageHistory(sender)
            self.session.add(sender_history)
            self.session.commit()
        sender_history.sent += 1
        recipient_history = self.session.query(self.UserMessageHistory).filter_by(user=recipient).first()
        if not recipient_history:
            recipient_history = self.UserMessageHistory(recipient)
            self.session.add(recipient_history)
            self.session.commit()
        recipient_history.accepted += 1
        self.session.commit()

    def get_client_statistics(self, username=None):
        message_history = self.session.query(
            self.User.username,
            self.User.last_connection,
            self.UserMessageHistory.sent,
            self.UserMessageHistory.accepted
        ).join(self.User)
        if username:
            message_history = message_history.filter(self.User.username == username)
        return message_history.all()


if __name__ == '__main__':
    db = ServerDB('db_server.sqlite')
    db.user_login('lajil', '192.168.1.4', 8888)
    db.user_login('lajil2', '192.168.1.6', 7777)
    print(db.get_all_users())
    print(db.get_active_users())
    db.user_logout('lajil')
    print(db.get_all_users())
    print(db.get_active_users())
    pprint(db.login_history('lajil'))
    pprint(db.login_history())
    db.add_contact('lajil', 'lajil2')
    print(db.get_contacts('lajil'))
    db.remove_contact('lajil', 'lajil2')
    print(db.get_contacts('lajil'))
    db.database_handle_message('lajil', 'lajil2')
    print(db.get_client_statistics())
