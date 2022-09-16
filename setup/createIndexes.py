from arango import ArangoClient
import env


# Initialize the ArangoDB client and Main Database.

client = ArangoClient(hosts=env.MYHOST)
# Connect to the database as root user.
db = client.db('Movies', username='root', password=env.MYROOTPASSWORD)
async_db = db.begin_async_execution(return_result=True)

def createAnalyzer(AnalyzerName):
    db.create_analyzer(
        name=AnalyzerName,
        analyzer_type='ngram',
        properties={'min':3,'max':5,'preserveOriginal':True,'streamType':"utf8"},
        features=[]
    )
 
# Create a view.  Basically the Type is always arangosearch


def createView(ViewName,CollectionName,FieldsForView,AnalyzerType2):
    db.create_view(
        name=ViewName,
        view_type='arangosearch',
        properties={
            'consolidationIntervalMsec': 1000,
            'links': {
                CollectionName: {
                    "analyzers": [
                        AnalyzerType2, "identity"
                        ],                    
                        'fields': { FieldsForView : {} },
                    'includeAllFields': False,
                    'storeValues': 'none',
                    'trackListPositions': False,
                    'inBackground': True
                    }
                }
            }
    )


def createFullTextIndex(CollectionToIndex):
    minlength = 3
    IndexName = 'MetaOverview'
    if db.has_collection(CollectionToIndex):
        movies_meta_collection = db.collection(CollectionToIndex)

    #Get JSON List of Indexes on File
    myindexes=movies_meta_collection.indexes()
    json_data = myindexes
    AlreadyIndex=False
    for item in json_data:
        print(item['name'])
        if item['name'] == IndexName:
            AlreadyIndex = True
    print('Already Indexed:' +str(AlreadyIndex))
    CreatedIndex=movies_meta_collection.add_fulltext_index(fields=['overview'],min_length=minlength,name=IndexName, in_background=True)
    print(CreatedIndex)

#createFullTextIndex('movies_metadata')

#Create Index on Movie_Edge job
def createPersistentIndex(CollectionToIndex):
    IndexPointer = db.collection(CollectionToIndex)
    #Get JSON List of Indexes on File
    myindexes=IndexPointer.indexes()
    IndexName="Job"
    for item in myindexes:
        if item['name'] == IndexName:
            print(IndexName + ' Already Indexed:')
            CreatedIndex=None
        else:
            CreatedIndex = IndexPointer.add_persistent_index(fields=['job'], unique=False, sparse=False, in_background=True, name="Job")
    return(CreatedIndex)

IndexJob=createPersistentIndex('movie_edges_test')

#print(db.async_jobs(status='done', count=100))
#print(db.async_jobs(status='pending', count=100))