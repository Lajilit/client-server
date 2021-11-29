import inspect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SingletonMeta(type):
    """Реализация Singleton"""

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class Singleton(metaclass=SingletonMeta):
    """Базовый класс Singleton"""
    pass


class ServerDBError(Exception):
    """Класс-исключение для ServerDB"""
    pass


class ServerDB(Singleton):
    """Класс для управления базой данных сервера"""

    def __init__(self, base, db_name=None):
        if db_name:
            db_name = f'sqlite:///{db_name}'
        else:
            db_name = 'sqlite:///:memory:'

        self.engine = create_engine(
            db_name,
            echo=True,
            connect_args={'check_same_thread': False}
            # https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#using-a-memory-database-in-multiple-threads
        )
        self.base = base
        self.session = None

    def setup(self):
        """Загрузка базы данных"""
        self.base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def close(self):
        """Закрытие базы данных"""

        print('Database closed')
        if self.session:
            self.session.close()
            self.session = None


# https://pythonist.ru/kontekstnye-menedzhery-v-python/
class SessionContextManager:
    """Контекстный менеджер для операций с базой данных"""

    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_traceback):
        if not exc_type:
            self.session.commit()
        else:
            self.session.rollback()
            method_name = inspect.stack()[1][3]
            raise ServerDBError(f'Error in {method_name}')
