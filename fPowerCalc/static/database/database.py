from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker


def create_database_if_not_exists():
	engine = create_engine("mysql://lsxliron@192.168.1.32/al1", isolation_level="READ_UNCOMMITTED")
	Base=declarative_base
	Base.metadata.create_all(engine)

def t():
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"