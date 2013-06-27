from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import MetaData
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
metadata = MetaData()

class Client(Base):
	'''
	This class represents the clients computers
	'''
	__tablename__='Client'
	
	name = Column(String(50), primary_key=True)
	username = Column(String(50))
	password = Column(String(50))
	IP = Column(String(16), unique=True)
	port = Column(Integer)
	OS = Column(String(8))

	def __init__(self, name, username, password, IP, port, OS):
		self.name = name
		self.username = username
		self.password = password
		self.IP = IP
		self.port = port
		self.OS =OS

	@hybrid_property
	def get_client_name_and_ip(self):
		return self.name + " (" + self.IP + ")"

	@hybrid_property
	def get_client_name(self):
		return self.name

	@hybrid_property
	def get_os(self):
		return self.OS

	

class Software(Base):
	'''
	This class represents the software which runs on a client computer.
	'''

	__tablename__ = 'Software'

	name = Column(String(50), primary_key=True)
	client_name = Column(String(50), primary_key=True)
	path = Column(String(100),primary_key=True)

	def __init__(self,name,my_client,path):
		self.name = name
		self.client_name = my_client
		self.path = path

	




def create_db_if_not_exists():
	'''
	Create the database when the user goes to the homepage (if it doesn't exists).
	Return types:
		0 - OK
		1 = Duplicate entry
	'''
	engine = create_engine("mysql://lsxliron@localhost", isolation_level="READ_UNCOMMITTED", echo=True)
	engine.execute("CREATE DATABASE IF NOT EXISTS PowerCalc")
	engine = create_engine("mysql://lsxliron@localhost/PowerCalc", isolation_level="READ_UNCOMMITTED", echo=True)
	Base.metadata.create_all(engine)



def insert_client_to_database(name, username, password, IP, port, OS):
	'''
	Adds a client computer to the database
	'''
	try:
		session = get_session()
		new_entry = Client(name, username, password, IP, int(port), OS)

		session.add(new_entry)
		session.commit()
		return 0
	
	except IntegrityError:
		return 1


def get_clients():
	'''
	This function returns a list of all the clients which are in the database
	'''
	session = get_session()
	clients_list = list()
	for row in session.query(Client).all():
		clients_list.append(row.get_client_name)

	return clients_list

def get_clients_and_ip():
	'''
	Returns a list of strings with all the clients and their corresponding ip addresses
	'''
	session = get_session()
	client_and_ip_list = list()
	for row in session.query(Client).all():
		client_and_ip_list.append(row.get_client_name_and_ip)

	return client_and_ip_list

def get_client_os(client):
	'''
	Returns a list with the client's OS
	'''
	session = get_session()
	clientOS=str()
	for row in  session.query(Client).filter(Client.name == client):
		clientOS = row.get_os

	return clientOS


def add_software_to_database(sw_name, client_name, sw_path):
	'''
	Insert a software to the database database
	'''
	try:
		session = get_session()


		new_entry = Software(sw_name, str(client_name), sw_path)
		session.add(new_entry)
		session.commit()
		return 0

	except IntegrityError:
		return 1




def get_session():
	'''
	Returns a session for the database
	'''
	engine = get_engine()
	Session = sessionmaker(bind=engine)
	session = Session()
	return session

def get_engine():
	'''
	Returns engine for connection with the database
	'''
	return  create_engine("mysql://lsxliron@localhost/PowerCalc", isolation_level="READ_UNCOMMITTED", echo=True)

	