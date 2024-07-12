from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    tests = relationship('Test', back_populates='collection', cascade='all, delete-orphan')

class Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=False)
    name = Column(String, nullable=False)
    executions = relationship('Execution', back_populates='test', cascade='all, delete-orphan')
    data = relationship('Data', back_populates='test', uselist=False, cascade='all, delete-orphan')
    collection = relationship('Collection', back_populates='tests')

class Execution(Base):
    __tablename__ = 'executions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    result = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    test = relationship('Test', back_populates='executions')

class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    auth_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    target_url = Column(String, nullable=True)
    test = relationship('Test', back_populates='data')

DATABASE_URL = "sqlite:///tests.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class Database:
    def __init__(self):
        self.session = Session()

    def add_collection(self, name):
        new_collection = Collection(name=name)
        self.session.add(new_collection)
        self.session.commit()

    def delete_collection(self, collection_id):
        collection = self.session.query(Collection).get(collection_id)
        self.session.delete(collection)
        self.session.commit()

    def update_collection(self, collection_id, new_name):
        collection = self.session.query(Collection).get(collection_id)
        collection.name = new_name
        self.session.commit()

    def get_collection(self, collection_id):
        return self.session.query(Collection).get(collection_id)

    def get_collections(self):
        return self.session.query(Collection).all()

    def add_test(self, collection_id, name):
        new_test = Test(collection_id=collection_id, name=name)
        self.session.add(new_test)
        self.session.commit()

    def get_test(self, test_id):
        return self.session.query(Test).get(test_id)

    def delete_test(self, test_id):
        test = self.session.query(Test).get(test_id)
        self.session.delete(test)
        self.session.commit()

    def add_execution(self, test_id, result):
        new_execution = Execution(test_id=test_id, result=result)
        self.session.add(new_execution)
        self.session.commit()

    def get_tests(self, collection_id):
        return self.session.query(Test).filter_by(collection_id=collection_id).all()

    def get_executions(self, test_id):
        return self.session.query(Execution).filter_by(test_id=test_id).all()

    def get_data(self, test_id):
        return self.session.query(Data).filter_by(test_id=test_id).first()

    def save_data(self, test_id, auth_url=None, api_key=None, target_url=None):
        data = self.session.query(Data).filter_by(test_id=test_id).first()
        if not data:
            data = Data(test_id=test_id, auth_url=auth_url, api_key=api_key, target_url=target_url)
            self.session.add(data)
        else:
            if auth_url is not None:
                data.auth_url = auth_url
            if api_key is not None:
                data.api_key = api_key
            if target_url is not None:
                data.target_url = target_url
        self.session.commit()
