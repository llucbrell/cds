from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import time

Base = declarative_base()

class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    model_name = Column(String, nullable=True)
    auth_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    target_url = Column(String, nullable=True)
    request_template = Column(String, nullable=True)
    prompt_template = Column(String, nullable=True)
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
    responses = relationship('Response', back_populates='execution', cascade='all, delete-orphan')


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id'), nullable=False)
    model_name = Column(String, nullable=True)
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

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey('executions.id'), nullable=False)
    response_data = Column(String, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    date = Column(DateTime, default=func.now())
    model_name = Column(String, nullable=False)
    target_url = Column(String, nullable=False)
    execution = relationship('Execution', back_populates='responses')
    def to_dict(self):
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'response_data': self.response_data,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'date': self.date, 
            'model_name': self.model_name,
            'target_url': self.target_url,
        } 


class ScrapingConfig(Base):
    __tablename__ = 'scraping_configs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    levels = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=func.now())
    results = relationship('ScrapingResult', back_populates='config', cascade='all, delete-orphan')

class ScrapingResult(Base):
    __tablename__ = 'scraping_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(Integer, ForeignKey('scraping_configs.id'), nullable=False)
    result_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    config = relationship('ScrapingConfig', back_populates='results')


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

    def update_collection(self, collection_id, collection_name, model_name=None, auth_url=None, api_key=None, target_url=None, request_template=None, prompt_template=None):
        collection = self.session.query(Collection).get(collection_id)
        if collection_name is not None:
            collection.name = collection_name
        if model_name is not None:
            collection.model_name = model_name
        if auth_url is not None:
            collection.auth_url = auth_url
        if api_key is not None:
            collection.api_key = api_key
        if target_url is not None:
            collection.target_url = target_url
        if request_template is not None:
            collection.request_template = request_template
        if prompt_template is not None:
            collection.prompt_template = prompt_template
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

    def save_data(self, test_id, model_name=None, auth_url=None, api_key=None, target_url=None, request_template=None, prompt_template=None):
        data = self.session.query(Data).filter_by(test_id=test_id).first()
        if not data:
            data = Data(test_id=test_id, model_name=model_name, auth_url=auth_url, api_key=api_key, target_url=target_url, request_template=request_template, prompt_template=prompt_template)
            self.session.add(data)
        else:
            if model_name is not None:
                data.model_name = model_name
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


    def add_iterable_value(self, test_id, value_key, value_value, value_type, iterable_index=None):
        print("saving")
        print(value_value)
        new_value = Values(test_id=test_id, value_key=value_key, value_value=value_value, value_type=value_type, iterable_index=iterable_index)
        self.session.add(new_value)
        self.session.commit()
        return {'status': 'success', 'message': 'Value added successfully.'}
 
    def add_value(self, test_id, value_key, value_value, value_type, iterable_index=None):
        print("saving")
        print(value_value)
        existing_value = self.session.query(Values).filter_by(test_id=test_id, value_key=value_key, value_type=value_type).first()
        if existing_value:
            print("existe")
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

    def delete_values_by_key(self, test_id, value_key):
        values_to_delete = self.session.query(Values).filter_by(test_id=test_id, value_key=value_key, value_type='array').all()
        for value in values_to_delete:
            self.session.delete(value)
        self.session.commit()
        return len(values_to_delete)

    def delete_iterable_values_by_key(self, test_id, value_key):
        values_to_delete = self.session.query(Values).filter_by(test_id=test_id, value_key=value_key, value_type='iterable').all()
        for value in values_to_delete:
            self.session.delete(value)
        self.session.commit()
        return len(values_to_delete)

    def get_execution(self, execution_id):
        return self.session.query(Execution).get(execution_id)
    
    def add_execution(self, test_id, result="In Progress"):
        new_execution = Execution(test_id=test_id, result=result)
        self.session.add(new_execution)
        self.session.commit()
    
    def update_execution_status(self, execution_id, status):
        execution = self.get_execution(execution_id)
        execution.result = status
        self.session.commit()

    def add_response(self, execution_id, response_data, start_time, end_time, duration, model_name, target_url):
        new_response = Response(execution_id=execution_id, response_data=response_data, start_time=start_time, end_time=end_time, duration=duration, model_name=model_name, target_url=target_url)
        self.session.add(new_response)
        self.session.commit()

    def get_responses(self, execution_id):
        return self.session.query(Response).filter_by(execution_id=execution_id).all()

    def delete_response(self, response_id):
        response = self.session.query(Response).get(response_id)
        self.session.delete(response)
        self.session.commit()

    def get_responses(self, execution_id):
        return self.session.query(Response).filter_by(execution_id=execution_id).all()

    def add_scraping_config(self, name, url, levels):
        new_config = ScrapingConfig(name=name, url=url, levels=levels)
        self.session.add(new_config)
        self.session.commit()

    def get_scraping_configs(self):
        return self.session.query(ScrapingConfig).all()

    def get_scraping_config(self, config_id):
        return self.session.query(ScrapingConfig).get(config_id)

    def delete_scraping_config(self, config_id):
        config = self.session.query(ScrapingConfig).get(config_id)
        self.session.delete(config)
        self.session.commit()

    def add_scraping_result(self, config_id, result_text):
        new_result = ScrapingResult(config_id=config_id, result_text=result_text)
        self.session.add(new_result)
        self.session.commit()