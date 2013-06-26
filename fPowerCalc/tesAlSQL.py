from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Date, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

from sqlalchemy.ext.hybrid import hybrid_property


engine = create_engine("mysql://lsxliron@192.168.1.32/PowerCalc", isolation_level="READ UNCOMMITTED")
Base = declarative_base()

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
	def get_name(self):
		return self.name


Session = sessionmaker(bind=engine)
session = Session()

# newEntry = Artist("liron","9174002767")
# session.add(newEntry)
# session.commit()

# ents = [Artist("paty","347"),
#         Artist("yonatan","516"),
#         Artist("me","91")]

# session.add_all(ents)
# session.commit()

#SELECT
res=session.query(Client).all()
for i in range(0,len(res)):
	print res[i].get_name