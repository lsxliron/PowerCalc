import database
from database import Client as Client
from database import Software as Software
engine = database.get_engine()
session = database.get_session()
ip = None
for client in session.query(Client).filter(Client.IP == '192.168.1.68'):
	ip=client.name

print ip

print 