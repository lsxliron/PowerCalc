from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import MetaData

Base = declarative_base()
metadata = MetaData()

class Client(Base):
	'''
	This class represents the clients computers
	'''
	__tablename__='Client'
	
	name = Column(String(50))
	username = Column(String(50))
	password = Column(String(50))
	IP = Column(String(16), primary_key=True)
	port = Column(Integer)
	OS = Column(String(8))

	def __init__(self, name, username, password, IP, port, OS):
		self.name = name
		self.username = username
		self.password = password
		self.IP = IP
		self.port = port
		self.OS =OS


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
	Adds a client computer to the datbase
	'''
	try:
		engine = create_engine("mysql://lsxliron@localhost/PowerCalc", isolation_level="READ_UNCOMMITTED", echo=True)
		Session = sessionmaker(bind=engine)
		session = Session()
		conn = engine.connect()
		new_entry = Client(name, username, password, IP, int(port), OS)

		session.add(new_entry)
		session.commit()
		return 0
	
	except IntegrityError:
		return 1
	