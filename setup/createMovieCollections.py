import time
from arango import ( ArangoClient,AQLQueryExecuteError,AsyncJobCancelError,AsyncJobClearError)
import env

# Initialize the ArangoDB client and Main Database.
client = ArangoClient(hosts=env.MYHOST)
# Connect to the database as root user.
db = client.db('Movies', username='root', password=env.MYROOTPASSWORD)

#Function to Create Collection if it does not exist
#Delete and recreate since truncating takes forever
def createCollections(CollectionName):
    if db.has_collection(CollectionName):
        movie_nodes = db.collection(CollectionName)
        movie_nodes.delete
        movie_nodes = db.create_collection(CollectionName)
    else:
        movie_nodes = db.create_collection(CollectionName)

#Function to Create Edge Collection if it does not exist

def createEdgeCollections(CollectionName):
    if db.has_collection(CollectionName):
        movie_edges = db.collection(CollectionName)
        movie_edges.delete
        movie_edges = db.create_collection(CollectionName,edge=True)
    else:
        movie_edges = db.create_collection(CollectionName,edge=True)


# Create Graph for Collection if it does not exist
def createGraph(GraphName):
    if db.has_graph(GraphName):
        movie_graph = db.graph(GraphName)
    else:
        movie_graph = db.create_graph(GraphName)

# Each Create is a separate Function so they can be easily commented out

#Create and update movie Nodes 

def CreateMovieNodes():
    #Create initial collection 
    newcollection=createCollections('movie_nodes')

    #Append TitleData to "movie_nodes" 
    file_pointer = open("./createTitleNodes.aql", "r")
    createTitleNodeQuery = file_pointer.read()
    file_pointer.close
    titles_async_db = db.begin_async_execution(return_result=True)
    async_aql_titles = titles_async_db.aql
    mytitles = async_aql_titles.execute(createTitleNodeQuery)

    #Append Name Data to "movie_nodes" 
    file_pointer = open("./createNameNodes.aql", "r")
    createNameNodeQuery = file_pointer.read()
    file_pointer.close
    names_async_db = db.begin_async_execution(return_result=True)
    async_aql_names = names_async_db.aql
    mynames = async_aql_names.execute(createNameNodeQuery)
    myjobs=[mytitles,mynames]
    return(myjobs) 

#Comment out to not run


#create Movie Edges
def CreateMovieEdges():
    createEdgeCollections('movie_edges')

    #Create Edges 
    file_pointer = open("./Create_Movie_Edges.aql", "r")
    createMovieEdgesQuery = file_pointer.read()
    file_pointer.close
    edges_async_db = db.begin_async_execution(return_result=True)
    async_aql_edges = edges_async_db.aql   
    myedgejob = async_aql_edges.execute(createMovieEdgesQuery)


def Create_OneHitWonders():
    #Create One Hit Wonders Collection
    createCollections('OneHitWonders')
    file_pointer = open("./CreateOneHitWondersBase.aql", "r")
    createOneHitCollection = file_pointer.read()
    file_pointer.close
    onehit_async_db = db.begin_async_execution(return_result=True)
    async_aql_onehit = onehit_async_db.aql
    myonehits = async_aql_onehit.execute(createOneHitCollection)
    return(myonehits) 

def Create_OneHitWonders_edges():
    #Add One hit wonders "movie_edges" 
    file_pointer = open("./Create_Movie_Edges_OneHitWonders.aql", "r")
    createMovieEdgesQuery_onehit= file_pointer.read()
    file_pointer.close
    edges_async_db_onehit = db.begin_async_execution(return_result=True)
    async_aql_edges_onehit = edges_async_db_onehit.aql
    myedgejob_onehit = async_aql_edges_onehit.execute(createMovieEdgesQuery_onehit)
    return(myedgejob_onehit) 

onehitedgecollection_job=Create_OneHitWonders_edges()

def createMovieGraph(GraphName):
    if db.has_graph(GraphName):
        db.delete_graph(GraphName)
        moviegraph = db.create_graph(GraphName)
    else:
        moviegraph = db.create_graph(GraphName)

    allnodes = moviegraph.create_edge_definition(
            edge_collection='movie_edges',
            from_vertex_collections=['movie_nodes'],
            to_vertex_collections=['movie_nodes']
        )
    return(allnodes)  