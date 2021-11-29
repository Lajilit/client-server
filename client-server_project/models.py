from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Table
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

from db_config import SessionContextManager


class CoreMixin:
    """Общее ядро для таблиц базы данных"""

    # https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/api.html#sqlalchemy.ext.declarative.declared_attr
    # https://docs.sqlalchemy.org/en/14/orm/declarative_mixins.html

    @declared_attr
    def __tablename__(self):
        return f'{self.__name__.lower()}s'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow(), nullable=False, onupdate=datetime.utcnow())

    @classmethod
    def all(cls, session):
        """Получить все объекты модели"""

        with SessionContextManager(session) as _session:
            return _session.query(cls).all()

    @classmethod
    def create(cls, session, *args, **kwargs):
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


Base = declarative_base(cls=CoreMixin)

associated_table_user_chat = Table(
    'clientchats',
    Base.metadata,
    Column('client_id', Integer, ForeignKey('clients.id')),
    Column('chat_id', Integer, ForeignKey('chats.id'))
)


class Client(Base):
    """Модель клиента"""

    username = Column(String(24), unique=True, nullable=False)
    first_name = Column(String(32))
    last_name = Column(String(32))
    info = Column(String(128))
    password = Column(String(32))

    chat = relationship('Chat', secondary=associated_table_user_chat, backref='user')
    message = relationship('Message', backref='owner')
    history = relationship('UserHistory', backref='owner')

    def __init__(self, client):
        self.username = client.get('username')
        self.first_name = client.get('first_name')
        self.last_name = client.get('last_name')
        self.password = client.get('password')
        self.info = client.get('info')

    def __repr__(self):
        return f'<Client(id={self.id}, username={self.username}, first_name={self.first_name})>'

    @classmethod
    def get_client_by_username(cls, session, username):
        """
        Получение объекта класса из базы
        Если объекта с указанным username в базе не существует, возвращается None
        """
        obj = session.query(cls).filter(cls.username == username).first()
        return obj


class Chat(Base):
    """Модель для чата"""

    title = Column(String(32), nullable=False)

    message = relationship('Message', backref='chat')

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return f'<Chat(id={self.id}, title={self.title})>'


class Contact(Base):
    """Модель контактов"""

    owner_id = Column(Integer, ForeignKey('clients.id'))
    contact_id = Column(Integer, ForeignKey('clients.id'))

    def __init__(self, owner_id, contact_id):
        self.owner_id = owner_id
        self.contact_id = contact_id

    def __repr__(self):
        return f'<Contact(client_id={self.owner_id}, contact_id={self.contact_id})>'

    @classmethod
    def get_all_user_contacts(cls, session, owner_id):
        """
        Получить все контакты клиента с id=owner_id
        Если объектов в базе не существует, возвращается None
        """
        return session.querry(cls).filter_by(owner_id=owner_id).all()


class ClientLogin(Base):
    """Модель истории подключений клиента"""

    owner_id = Column(Integer, ForeignKey('clients.id'))
    ip_address = Column(String)

    def __init(self, owner_id, ip_address):
        self.owner_id = owner_id
        self.ip_address = f'{ip_address}'  # '{}:{}'.format(*ip_address)

    def __repr__(self):
        return f'<ClientHistory(client_id={self.owner_id})>'


class Message(Base):
    """Модель сообщений клиента"""

    owner_id = Column(Integer, ForeignKey('clients.id'))
    chat_id = Column(Integer, ForeignKey('chats.id'))
    text = Column(Text)

    def __init__(self, owner_id, chat_id, text):
        self.owner_id = owner_id
        self.chat_id = chat_id
        self.text = text

    def __repr__(self):
        return f'<Contact(client_id={self.owner_id}, contact_id={self.contact_id})>'
