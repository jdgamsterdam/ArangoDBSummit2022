import functions_framework
import json
from arango import ArangoClient

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
       request (flask.Request): The request object.
       <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
       The response text, or any set of values that can be turned into a
       Response object using `make_response`
       <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    #request_json = request.get_json(silent=True)
    request_args = request.args
    try:
      QueryText = request_args['AQL']
    except:
      #No AQL
      QueryText = 'FOR name in name_basics LIMIT 1 RETURN name'
    try:
      my_bind_vars = request_args['BindVars']
    except:
      #No Bind Vars
      my_bind_vars = {}
  
    # Make it standard Json with double quotes
    my_bind_vars = my_bind_vars.replace("'", "\"" )
    my_bind_vars_json=json.loads(my_bind_vars)

    #Setup Query API Wrapper
    client = ArangoClient(hosts='YOURARANGOSERVER')
    # Connect to the database as Super user.
    db = client.db('Movies', username='YOURUSERNAME', password='YOURPASSWORD')
    myaql = db.aql
    #As we know it will be a small query we can make the batch size 1
    mycursor = myaql.execute(QueryText,bind_vars=my_bind_vars_json, batch_size=1)
    #Convert the Results to a Python List object
    mylist_fromarango = [doc for doc in mycursor]
    return repr(mylist_fromarango)