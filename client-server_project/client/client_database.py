from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


class ClientDB:
    Base = declarative_base()

    class KnownUser(Base):
        __tablename__ = 'known_users'
        id = Column(Integer, primary_key=True)
        username = Column(String(24), unique=True)

        def __init__(self, username):
            self.username = username

    class MessageHistory(Base):
        __tablename__ = 'message_history'
        id = Column(Integer, primary_key=True)
        from_user = Column(String(24))
        to_user = Column(String(24))
        message_text = Column(Text)
        datetime = Column(DateTime)

        def __init__(self, from_user, to_user, message_text):
            self.from_user = from_user
            self.to_user = to_user
            self.message_text = message_text
            self.datetime = datetime.now()

    class UserContact(Base):
        __tablename__ = 'user_contacts'
        id = Column(Integer, primary_key=True)
        username = Column(String(24), unique=True)

        def __init__(self, username):
            self.username = username

    def __init__(self, username):
        self.engine = create_engine(
            f'sqlite:///db_client_{username}.sqlite',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )
        self.Base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)()

        self.session.query(self.UserContact).delete()
        self.session.commit()

    def add_contact(self, contact_username):
        if not self.session.query(self.UserContact).filter_by(username=contact_username).count():
            new_contact = self.UserContact(contact_username)
            self.session.add(new_contact)
            self.session.commit()

    def remove_contact(self, contact_username):
        self.session.query(self.UserContact).filter_by(username=contact_username).delete()
        self.session.commit()

    def refresh_known_users(self, users_list):
        self.session.query(self.KnownUser).delete()
        for username in users_list:
            new_known_user = self.KnownUser(username)
            self.session.add(new_known_user)
        self.session.commit()

    def save_message(self, from_user, to_user, message):
        new_message = self.MessageHistory(from_user, to_user, message)
        self.session.add(new_message)
        self.session.commit()

    def get_contacts(self):
        return [username for (username,) in self.session.query(self.UserContact.username).all()]

    def get_known_users(self):
        return [username for (username,) in self.session.query(self.KnownUser.username).all()]

    def check_user_is_known(self, username):
        if self.session.query(self.KnownUser).filter_by(username=username).count():
            return True
        return False

    def check_user_is_a_contact(self, username):
        if self.session.query(self.UserContact).filter_by(username=username).count():
            return True
        return False

    def get_user_message_history(self, username, contact_name=None):
        message_history = self.session.query(self.MessageHistory)
        if contact_name:
            message_history = message_history.filter(
                or_(
                    and_(self.MessageHistory.from_user == username, self.MessageHistory.to_user == contact_name),
                    and_(self.MessageHistory.from_user == contact_name, self.MessageHistory.to_user == username)
                )
            )
        else:
            message_history = message_history.filter(
                or_(self.MessageHistory.from_user == username, self.MessageHistory.to_user == username)
            )
        return [(message.from_user,
                 message.to_user,
                 message.message_text,
                 message.datetime) for message in message_history.all()]


if __name__ == '__main__':
    test_db = ClientDB('test1')
    # for i in ['test3', 'test4', 'test5']:
    #     test_db.add_contact(i)
    # test_db.add_contact('test4')
    # test_db.refresh_known_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    # test_db.save_message('test1', 'test3', 'test_text_1')
    # test_db.save_message('test2', 'test3', 'test_text_2')
    # test_db.save_message('test1', 'test2', 'test_text_3')
    # test_db.save_message('test2', 'test1', 'test_text_4')
    print(test_db.get_contacts())
    print(test_db.get_known_users())
    print(test_db.check_user_is_known('test1'))
    print(test_db.check_user_is_known('test10'))
    print(test_db.get_user_message_history('test1'))
    print(test_db.get_user_message_history('test1', 'test2'))
    # test_db.remove_contact('test4')
    print(test_db.get_contacts())
