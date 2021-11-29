from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Table
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from db_config import SessionContextManager
Base = declarative_base()


class Core:
    """Общее ядро для таблиц базы данных"""

    # https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/api.html#sqlalchemy.ext.declarative.declared_attr
    # https://docs.sqlalchemy.org/en/14/orm/declarative_mixins.html

    @declared_attr
    def __tablename__(cls):
        return f'{cls.__name__.lower()}s'

    id = Column(Integer, primary_key=True)
    created_datetime = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated_datetime = Column(DateTime, default=datetime.utcnow(), nullable=False, onupdate=datetime.utcnow())

    @classmethod
    def all(cls, session):
        """Получить все объекты модели"""

        with SessionContextManager(session) as _session:
            return _session.query(cls).all()

    @classmethod
    def add(cls, session, *args, **kwargs):
        """ Добавить объект в базу"""
        with SessionContextManager(session) as session:
            obj = cls(*args, **kwargs)
            session.add(obj)
        return obj

    @classmethod
    def get(cls, session, obj_id):
        """ Получить объект класса cls из базы
        Если объекта с obj_id в базе не существует, возвращается None"""
        obj = session.querry(cls).filter(cls.id == obj_id).first()
        return obj

    def update(self, session, **kwargs):
        """Обновление данных экземпляра"""
        with SessionContextManager(session) as session:
            for key, value in kwargs.items():
                setattr(self, key, value)
            session.add(self)

    def delete(self, session):
        """Удаление записи из базы данных"""
        with SessionContextManager(session) as session:
            session.delete(self)



associated_table_userchat = Table(
    'association_UserChat',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('clients.id')),
    Column('chat_id', Integer, ForeignKey('chats.id'))
)


class Client(Core, Base):
    """Модель пользователя"""

    username = Column(String(24), unique=True, nullable=False)
    first_name = Column(String(32))
    last_name = Column(String(32))
    info = Column(String(128))
    password = Column(String(32))

    chat = relationship('Chat', secondary=associated_table_userchat, backref='user')
    message = relationship('Message', backref='owner')
    history = relationship('UserHistory', backref='owner')

    def __init__(self, client):
        self.username = client.get('username')
        self.first_name = client.get('first_name')
        self.last_name = client.get('last_name')
        self.password = client.get('password')
        self.info = client.get('info')

    def __repr__(self):
        return f'<User(id={self.id}, username={self.username}, first_name={self.first_name})>'

    @classmethod
    def get_client_by_username(cls, session, username):
        """
        Получение люъекта класса из базы
        Если объекта с указанным username в базе не существует, возвращается None
        """
        obj = session.query(cls).filter(cls.username == username).first()
        return obj


class Chat(Core, Base):
    """Модель для чата"""

    title = Column(String(32), nullable=False)

    message = relationship('Message', backref='chat')

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return f'<Chat(id={self.id}, title={self.title})>'


class Contact(Core, Base):
    """Модель списка контактов"""

    owner_id = Column(Integer, ForeignKey('clients.id'))
    contact_id = Column(Integer, ForeignKey('clients.id'))

    def __init__(self, owner_id, contact_id):
        self.owner_id = owner_id
        self.contact_id = contact_id

    def __repr__(self):
        return f'<Contact(user_id={self.owner_id}, contact_id={self.contact_id})>'

    @classmethod
    def get_all_user_contacts(cls, session, owner_id):
        """
        Получить все контакты пользователя с id=owner_id
        Если объектов в базе не существует, возвращается None
        """
        return session.querry(cls).filter_by(owner_id=owner_id).all()


class UserHistory(Core, Base):
    """Модель истории пользователя"""

    owner_id = Column(Integer, ForeignKey('clients.id'))
    ip_address = Column(String)

    def __init(self, owner_id, ip_address):
        self.owner_id = owner_id
        self.ip_address = f'{ip_address}'  # '{}:{}'.format(*ip_address)

    def __repr__(self):
        return f'<UserHistory(user_id={self.owner_id})>'


class Message(Core, Base):
    """Модель сообщений пользователя"""

    owner_id = Column(Integer, ForeignKey('clients.id'))
    chat_id = Column(Integer, ForeignKey('chats.id'))
    text = Column(Text)

    def __init__(self, owner_id, chat_id, text):
        self.owner_id = owner_id
        self.chat_id = chat_id
        self.text = text

    def __repr__(self):
        return f'<Contact(user_id={self.owner_id}, contact_id={self.contact_id})>'
