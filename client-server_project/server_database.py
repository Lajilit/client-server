from pprint import pprint

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


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

    def __init__(self):
        self.engine = create_engine(
            'sqlite:///db_server.sqlite',
            echo=False,
            pool_recycle=7200
        )
        self.Base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.session.query(self.User).delete()
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


if __name__ == '__main__':
    db = ServerDB()
    db.user_login('lajil', '192.168.1.4', 8888)
    db.user_login('lajil2', '192.168.1.6', 7777)
    print(db.get_all_users())
    db.user_logout('lajil')
    print(db.get_all_users())
    print(db.get_active_users())
    db.user_logout('lajil2')
    print(db.get_all_users())
    print(db.get_active_users())

    pprint(db.login_history('lajil'))
    pprint(db.login_history())

    print(db.get_all_users())
