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
    collection = relationship('Collection', back_populates='tests')

class Execution(Base):
    __tablename__ = 'executions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    result = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    test = relationship('Test', back_populates='executions')

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

    def add_test(self, collection_id, name):
        new_test = Test(collection_id=collection_id, name=name)
        self.session.add(new_test)
        self.session.commit()

    def delete_test(self, test_id):
        test = self.session.query(Test).get(test_id)
        self.session.delete(test)
        self.session.commit()

    def add_execution(self, test_id, result):
        new_execution = Execution(test_id=test_id, result=result)
        self.session.add(new_execution)
        self.session.commit()

    def get_collections(self):
        return self.session.query(Collection).all()

    def get_tests(self, collection_id):
        return self.session.query(Test).filter_by(collection_id=collection_id).all()

    def get_executions(self, test_id):
        return self.session.query(Execution).filter_by(test_id=test_id).all()
