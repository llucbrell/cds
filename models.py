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
    request_template = Column(String, nullable=True)
    prompt_template = Column(String, nullable=True)
    test = relationship('Test', back_populates='data')

class Values(Base):
    __tablename__ = 'values'
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    value_key = Column(String, nullable=True)
    value_value = Column(String, nullable=True)
    value_type = Column(String, nullable=True)  # fixed, iterable, array
    iterable_index = Column(Integer, nullable=True)  # Used for iterable types

    def to_dict(self):
        return {
            'id': self.id,
            'value_key': self.value_key,
            'value_value': self.value_value,
            'value_type': self.value_type,
            'iterable_index': self.iterable_index
        }

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

    def save_data(self, test_id, auth_url=None, api_key=None, target_url=None, request_template=None, prompt_template=None):
        data = self.session.query(Data).filter_by(test_id=test_id).first()
        if not data:
            data = Data(test_id=test_id, auth_url=auth_url, api_key=api_key, target_url=target_url, request_template=request_template, prompt_template=prompt_template)
            self.session.add(data)
        else:
            if auth_url is not None:
                data.auth_url = auth_url
            if api_key is not None:
                data.api_key = api_key
            if target_url is not None:
                data.target_url = target_url
            if request_template is not None:
                data.request_template = request_template
            if prompt_template is not None:
                data.prompt_template = prompt_template
        self.session.commit()


    def add_value(self, test_id, value_key, value_value, value_type, iterable_index=None):
        print("saving")
        existing_value = self.session.query(Values).filter_by(test_id=test_id, value_key=value_key, value_type=value_type).first()
        if existing_value:
            return {'status': 'error', 'message': 'Value with this key already exists.'}
        new_value = Values(test_id=test_id, value_key=value_key, value_value=value_value, value_type=value_type, iterable_index=iterable_index)
        self.session.add(new_value)
        self.session.commit()
        return {'status': 'success', 'message': 'Value added successfully.'}
        
    def get_value(self, value_id):
        return self.session.query(Values).get(value_id)

    def update_value(self, value_id, value_key=None, value_value=None, value_type=None, iterable_index=None):
        value = self.session.query(Values).get(value_id)
        if value_key is not None:
            value.value_key = value_key
        if value_value is not None:
            value.value_value = value_value
        if value_type is not None:
            value.value_type = value_type
        if iterable_index is not None:
            value.iterable_index = iterable_index
        self.session.commit()

    def delete_value(self, value_id):
        value = self.session.query(Values).get(value_id)
        self.session.delete(value)
        self.session.commit()

    def get_values(self, test_id):
        return self.session.query(Values).filter_by(test_id=test_id).all()

