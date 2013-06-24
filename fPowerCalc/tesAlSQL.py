from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Date, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

engine = create_engine("mysql://lsxliron@192.168.1.32/al", isolation_level="READ UNCOMMITTED")
Base = declarative_base()

class Artist(Base):
	__tablename__ = "artists"

	id = Column(Integer, primary_key=True)
	name = Column(String(20))
	phone = Column(String(20))

	def __init__(self, name, phone):
		self.name = name
		self.phone = phone


Base.metadata.create_all(engine)		



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
res=session.query(Artist).filter(Artist.name=="paty").first()
print res.name + ' | ' + res.phone