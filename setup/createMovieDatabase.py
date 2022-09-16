from typing import Collection
from arango import ArangoClient
import env

# Initialize the ArangoDB client and Main Database.
client = ArangoClient(hosts=env.MYHOST)
# Connect to the database as root user.

sys_db = client.db('_system', username='root', password=env.MYROOTPASSWORD)

# Create a new database named "Movies" if it does not exist.
# Only root user has access to it at time of its creation.
if not sys_db.has_database('Movies'):
    sys_db.create_database('Movies')


#Add Super User to Movies

# Check if a user exists.
if not sys_db.has_user(env.MYUSERNAME):
    # Create a new user.
    sys_db.create_user(
        username=env.MYUSERNAME,
        password=env.MYPASSWORD,
        active=True
    )
else:    
    sys_db.update_permission(
        username=env.MYUSERNAME,
        permission='rw',
        database='Movies'
    )
