from dash import dash_table, dcc, html, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform, html
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import dash_daq as daq
import json as json
import pandas as pd
import bs4 as bs
import re as re
import dash,json,math,requests,ast

#Get Environment Variables from Seperate file
from importlib.machinery import SourceFileLoader

# imports the module from the given path
env = SourceFileLoader("main", "setup/env.py").load_module()

# General Utility Functions

def return_ducument(TextToParse):
    html_doc = TextToParse
    return convert_html_to_dash(html_doc)

def convert_html_to_dash(el,style = None):
    TAGS_PERMITTED =  {'div','span','a','hr','br','p','b','i','u','s','h1','h2','h3','h4','h5','h6','ol','ul','li',
                        'em','strong','cite','tt','pre','small','big','center','blockquote','address','font','img',
                        'table','tr','td','caption','th','textarea','option'}
    def __extract_style(el):
        if not el.attrs.get("style"):
            return None
        return {k.strip():v.strip() for k,v in [x.split(": ") for x in el.attrs["style"].split(";")]}

    if type(el) is str:
        return convert_html_to_dash(bs.BeautifulSoup(el,'html.parser'))
    if type(el) == bs.element.NavigableString:
        return str(el)
    else:
        name = el.name
        style = __extract_style(el) if style is None else style
        contents = [convert_html_to_dash(x) for x in el.contents]
        if name.title().lower() not in TAGS_PERMITTED:        
            return contents[0] if len(contents)==1 else html.Div(contents)
        return getattr(html,name.title())(contents,style = style)

# Setup Default Styles for  CytoScape Graphing
default_inline={'display':'inline-block', 'padding-left': '10px'}
default_inline_dropdown={'display':'inline-block', 'padding-left': '10px', 'width': '150px'}
cyto_layout={'name': 'circle'}
cyto_style={'width': '100%', 'height': '500px'}
cyto_stylesheet=[
            {
                'selector': 'node',
                'style': {
                'background-color': '#BFD7B5',
                'label': 'data(label)'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'label': 'data(job)',
                    'line-color': 'red'
                }
            },
            {
                #Title Selector e.g. contains tt
                'selector': '[id *= "tt"]',
                'style': {
                    'shape': 'rectangle',
                    'background-color': '#BFD7B5'
                }
            },
            {
                #Name Selector e.g. contains nm
                'selector': '[id *= "nm"]',
                'style': {
                    'shape': 'circle',
                    'background-color': '#BFD7B5'
                }
            }


        ]

#Set  Initial Text for Divs
person1Name = 'Kevin Bacon'
person1nconst = 'nm0000102'

person2Name = 'Sissy Spacek'
person2nconst = 'nm0000651'

#InitialCenterNode=[ {'data': {'id': 'movie_nodes/'+person1nconst, 'label': person1Name}} ]
InitialCenterNode=[ {'data': {'id': 'name_basics/'+person1nconst, 'label': person1Name}} ]

CenterNode=InitialCenterNode

# Setup Database Connection

#client = ArangoClient(hosts=env.MYHOST)
# Connect to the database.
#db = client.db('Movies', username=env.MYUSERNAME, password=env.MYPASSWORD)

# Query- For KnownForTitles Need to group and substitute to convert that field to plain text or will screw up the table
# Also the order of the Filter Sort and LIMIT is very important 

def getQuery(queryfile):

    file_pointer = open(queryfile, "r")
    createTitleNodeQuery = file_pointer.read()
    file_pointer.close
    return createTitleNodeQuery

MoviesPersonsQuery=getQuery("./MoviesPersonsQuery_lev.aql")
#PersonRelationshipQuery=getQuery("./PersonRelationshipQuery.aql")
PersonRelationshipQuery=getQuery("./PersonRelationshipQuery_Direct.aql")
#NodesForPersonAtCenterForCyto=getQuery("./NodesForPersonAtCenterForCyto.aql")
NodesForPersonAtCenterForCyto=getQuery("./NodesForPersonAtCenterForCyto_Direct.aql")
#EdgesForPersonAtCenterForCyto=getQuery("./EdgesForPersonAtCenterForCyto.aql")
EdgesForPersonAtCenterForCyto=getQuery("./EdgesForPersonAtCenterForCyto_Direct.aql")
#TotalNodesForPersonAtCenterForCyto=getQuery("./TotalNodesForPersonAtCenterForCyto.aql")     
TotalNodesForPersonAtCenterForCyto=getQuery("./TotalNodesForPersonAtCenterForCyto_Direct.aql")



def run_cloud_query(QueryText, my_bind_vars={}):
    cloud_function_address=env.CLOUDFUNCTIONADDRESS
    #Convert Bind Vars to Text
    my_bind_vars_text=repr(my_bind_vars)
    gcparams = {'AQL':QueryText,'BindVars':my_bind_vars_text}
    r = requests.post(cloud_function_address,params=gcparams)
    #Return List Object 
    mydict=ast.literal_eval(r.text)  
    return(mydict)


def get_text_results_for_name(movie_person_name):

    #Set Default Name
    if movie_person_name==None:
        movie_person_name=person1Name
    name_query_bind_vars={'myname': movie_person_name}
    movies_cloud_query = run_cloud_query(MoviesPersonsQuery,name_query_bind_vars)
    return(movies_cloud_query)


def get_relationships(person1nconst,person2nconst):
    name_query_bind_vars={'nconst1': person1nconst,'nconst2': person2nconst}
    relationship_query = run_cloud_query(PersonRelationshipQuery,name_query_bind_vars)
    return(relationship_query)

#Initial Setup
maxnodespergraph=10
myoffset=0
total_return_nodes=20
pagenumber=1
node_query_bind_vars={'nconst': person1nconst, 'myoffset': myoffset, 'mycount': maxnodespergraph }
query_nodes = run_cloud_query(NodesForPersonAtCenterForCyto,node_query_bind_vars)
nodes=query_nodes+CenterNode
all_layout_types=['random','grid','circle','concentric','breadthfirst','cose']
initial_layout_type='circle'
all_node_shapes=['rectangle', 'roundrectangle', 'round-rectangle', 'cutrectangle', 'cut-rectangle', 'bottomroundrectangle', 'bottom-round-rectangle', 'barrel', 'ellipse', 'triangle', 'round-triangle', 'square', 'pentagon', 'round-pentagon', 'hexagon', 'round-hexagon', 'concavehexagon', 'concave-hexagon', 'heptagon', 'round-heptagon', 'octagon', 'round-octagon', 'tag', 'round-tag', 'star', 'diamond', 'round-diamond', 'vee', 'rhomboid', 'polygon']
initial_title_node_shape='ellipse'
initial_name_node_shape='square'
edge_query_bind_vars={'nconst': person1nconst, 'myoffset': myoffset, 'mycount': maxnodespergraph}
edges = run_cloud_query(EdgesForPersonAtCenterForCyto,edge_query_bind_vars)

#Get Initial Dropdown Elements
baseresults=get_text_results_for_name(person1Name)

#For Cloud Query need to Return as Text for the dataframe to Work
dropdownelements = [{"label": doc["primaryName"]+'-'+doc["nconst"], "value": doc["nconst"]} for doc in baseresults]
initial_dropdownelement = dropdownelements[0]["value"]

#Show Initial Table
#Convert Results to a Dataframe to show in a Dash Table
df = pd.DataFrame(baseresults)
myinitialtable=dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])

#Layout
app = DashProxy(transforms=[MultiplexerTransform()],external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
     html.Table(
        id='selection-table', 
        className='mytable',
        children = 
         [
            html.Tr( [
                html.Td([  
                html.Div('Find Person from full or partial name'),
                dcc.RadioItems([{'label': 'Like Query', 'value': 'likequery'},{'label': 'Levenshtein Distance', 'value': 'levenshtein'}], 'levenshtein', id='namesearchquerytype', inline=True),
                html.Div('Query Description', id='querydescription'),
                dcc.Input(id='persontofind', type='text', value=person1Name),
                html.Button('Find Person', id='Find-Person', n_clicks=0),
                html.Div(id='container-find-person', children='Enter a value and press submit'),
                html.Div('Selected Person', id='selected-person')
                ]),
                html.Td([
                    html.P("Node 1:  "),
                    html.Div(person1Name,id='person1name'),
                    html.Div(person1nconst,id='person1nconst'),
                    html.P("Node 2:  "),
                    html.Div(person2Name,id='person2name'),
                    html.Div(person2nconst,id='person2nconst'),
                    html.Button('Show Relationship', id='show-relationship', n_clicks=0)
                ])
              ] 
             ),
            html.Tr( [
                html.Td([    
                html.Div(myinitialtable,id='dashtable')
                ], style={'width': '50vw'}),
                html.Td([  
                    html.Div('The relationship between these two people is:', id='person-relationship')
                ])                
              ] 
             ),
            html.Tr( [
                html.Td([
                    dcc.Dropdown(dropdownelements, initial_dropdownelement, id='person-dropdown-1')
                ])                ,
                html.Td([  
                    html.Div('List as Table',id='relationship_dashtable')
                ])   
              ] 
             )
         ]),       
    html.Div(id='cytorow', children=[
        html.P("Selected Node:"),
        html.Div(id='container-add-person'),
        html.Div(children=[
            html.Button('Add as Node 1', id='submit-person1', n_clicks=0), 
            html.Button('Add as Node 2', id='submit-person2', n_clicks=0), 
            html.P("Total Connected Nodes: ", style={'display':'inline-block'}),
            html.Div(id='total-return-nodes',style={'display':'inline-block'}),
            html.P(" Nodes on Page: ", style={'display':'inline-block', 'padding-left': '20px'}),
            dcc.Input(id="nodes-on-page", type="number",debounce=False, placeholder=1, value=maxnodespergraph, min=1, max=25, step=1, style={'display':'inline-block', 'padding-left': '20px'}),
            html.P(" Current Page Number: ", style={'display':'inline-block', 'padding-left': '20px'}),
            dcc.Input(id="page-number", type="number",debounce=False, placeholder=1, value=1, min=1, max=4, step=1, style=default_inline )
        ]),
        html.Div(id='SelectLayoutTypes', children=[
	        html.Span("Graph display type: "),
	        dcc.Dropdown(all_layout_types, initial_layout_type, id='layout_type',style=default_inline_dropdown),
            html.Span("Title Node Shape:", style=default_inline),
	        dcc.Dropdown(all_node_shapes, initial_title_node_shape, id='title_node_shape',style=default_inline_dropdown ),
            html.Span("Name Node Shape:", style=default_inline),
	        dcc.Dropdown(all_node_shapes, initial_name_node_shape, id='name_node_shape',style=default_inline_dropdown ),
            html.Br(),
	        daq.ColorPicker(id='title-node-color-picker',label='Select Title Node Color',value=dict(hex='#119DFF'),style=default_inline),
    	    daq.ColorPicker(id='name-node-color-picker',label='Select Name Node Color',value=dict(hex='#119DFF'),style=default_inline),
            daq.ColorPicker(id='edge-color-picker',label='Select Edge Color',value=dict(hex='#119DFF'),style=default_inline)
            ]),
        html.Div('Initial IMDB',id='output-serverside-imdb'),
        html.Div('Initial Wiki',id='output-serverside-title'),
        cyto.Cytoscape(
            id='cytoscape1',
            elements=edges+nodes,
            layout=cyto_layout,
            style=cyto_style,
            stylesheet=cyto_stylesheet
            )
        ]
    )
])



# The call back and related update_output need to be in sequence 

#Get Name Search Query Type
@app.callback(
    Output('querydescription', 'children'),   
    Input('namesearchquerytype', 'value')
)
def update_output(value):
    if value=='levenshtein':
        MoviesPersonsQuery=getQuery("./MoviesPersonsQuery_lev.aql")
        ReturnValue='Levenshtein Queries are quicker but sometimes will not bring back all the desired results'
    else:    
        MoviesPersonsQuery=getQuery("./MoviesPersonsQuery_like.aql")
        ReturnValue='The like Query will add % to each side of your text for short strings this could take a long time'
    return ReturnValue

#Fill in Left Drop Down from Search
@app.callback(
    Output('container-find-person', 'children'),
    Output('dashtable', 'children'),
    Output('person-dropdown-1', 'options'),
    Output('person-dropdown-1', 'value'),   
    Input('Find-Person', 'n_clicks'),
    State('persontofind', 'value')
)
def update_output(n_clicks, value):
    #Get Results from Arango Query

    person1_results=get_text_results_for_name(value)
    #Convert Results to a Dataframe to show in a Dash Table

    if len(person1_results)==0:
        FirstReturn='There were no results for "{}" and the button has been clicked {} times'.format(value,n_clicks)
        MyDashTable=myinitialtable
        my_new_dropdown=dropdownelements
        new_first_element=initial_dropdownelement
    else:
        FirstReturn='The input value was "{}" and the button has been clicked {} times'.format(value,n_clicks)
        df = pd.DataFrame(person1_results)
        MyDashTable=dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns])
        #Get list To UPdate DropDown
        my_new_dropdown = [{"label": doc["primaryName"]+'-'+doc["nconst"], "value": doc["nconst"]} for doc in person1_results]
        new_first_element = my_new_dropdown[0]["value"]

    return FirstReturn, MyDashTable ,my_new_dropdown,new_first_element

#Change Cytoscape Output Type
@app.callback( 
    Output('cytoscape1', 'layout'),
    Output('cytoscape1', 'stylesheet'),
    Input('layout_type', 'value'),
    Input('title-node-color-picker', 'value'),
    Input('name-node-color-picker', 'value'),
    Input('edge-color-picker', 'value'),
    Input('title_node_shape', 'value'),
    Input('name_node_shape', 'value')
)
def update_output(layouttype, titlenodecolor, namenodecolor, edgecolor,titlenodeshape,namenodeshape):
    new_layout_type={'name': layouttype}
    new_cyto_stylesheet=cyto_stylesheet
    new_cyto_stylesheet[2]['style']['background-color']=titlenodecolor['hex']
    new_cyto_stylesheet[2]['style']['shape']=titlenodeshape
    new_cyto_stylesheet[3]['style']['background-color']=namenodecolor['hex']
    new_cyto_stylesheet[3]['style']['shape']=namenodeshape
    new_cyto_stylesheet[1]['style']['line-color']=edgecolor['hex']
    return new_layout_type,new_cyto_stylesheet

#When we do the dropdowns to select the center for the cyto graph
@app.callback(
    Output('cytoscape1', 'elements'),
    Output('total-return-nodes', 'children'),
    Output('page-number', 'max'),
    Input('person-dropdown-1', 'value'),
    Input('person-dropdown-1', 'options')
)
def update_output_dropdown1(value,options):
    if not value:
        raise PreventUpdate()
    else:
        #Update Cyto graph from Dropdown
        label='initial label'
        #Tell The query where to start
        pagenumber=1
        myoffset=(pagenumber-1)*maxnodespergraph
        node_query_bind_vars={'nconst': value, 'myoffset': myoffset, 'mycount': maxnodespergraph }
        total_node_query_bind_vars={'nconst': value }
        edge_query_bind_vars={'nconst': value, 'myoffset': myoffset, 'mycount': maxnodespergraph}
        for element in options:
            if element['value'] == value:
                label=element['label'] 
                break
            else:
                label= "NONE"
        #Since This is Coming From Drop Down it is always going to be name_basics in new system
        new_CenterNode=[ {'data': {'id': 'name_basics/'+value, 'label': label}} ]
        #Run Query - For Nodes we can use the query for both Person and Title Centered
        new_nodes = run_cloud_query(NodesForPersonAtCenterForCyto,node_query_bind_vars)
        #Get the total nodes return to update the page list
        total_return_nodes_json = run_cloud_query(TotalNodesForPersonAtCenterForCyto,total_node_query_bind_vars)
        total_return_nodes=total_return_nodes_json[0]['nodecount']
        maxpages=math.ceil(total_return_nodes/maxnodespergraph)
        new_nodes=new_nodes+new_CenterNode 
        new_edges = run_cloud_query(EdgesForPersonAtCenterForCyto,edge_query_bind_vars)

    return new_edges+new_nodes,total_return_nodes,maxpages

#Left On Cytoscape Click

@app.callback(
    Output('cytoscape1', 'elements'),
    Output('container-add-person', 'children'),
    Output('total-return-nodes', 'children'),
    Output('page-number', 'max'),  
    Output('page-number', 'value'),  
    Input('cytoscape1', 'tapNodeData'),
    Input('page-number', 'value'),
    Input('container-add-person', 'children'),
    Input('nodes-on-page', 'value')
)
def update_output_click1(tapNodeData,mypagenumber,LastNode,nodesonpage):
    #Update Cyto graph
    if (not tapNodeData) and (not mypagenumber) and (not nodesonpage):
        raise PreventUpdate() 
    else:
        #If node is selected Get Search info from Node
        if tapNodeData==None:
            #Means nothing was selected so go to last selection and update page number
            label=person1Name
            ClickedNodeID=person1nconst
            #myID="movie_nodes/"+ClickedNodeID
            #Since This is a Click need to Figure out if a Name or Film
            if ClickedNodeID[0:2]=='nm':
                myID="name_basics/"+ClickedNodeID
            else:
                myID="title_basics/"+ClickedNodeID
            ClickedNodeJson={ "id": myID, "label": label }
            ClickedNode=json.dumps(ClickedNodeJson)
        else:
            ClickedNode=json.dumps(tapNodeData, indent=2)
            ClickedNodeID=tapNodeData['id'].split("/")[1]
            label=tapNodeData['label']

        #Set Page number if Clicked Node Not Equal to Current Node
 
        if LastNode==ClickedNode:
            pagenumber=mypagenumber
        else:
            pagenumber=1

        maxnodespergraph=nodesonpage
        myoffset=(pagenumber-1)*maxnodespergraph
        node_query_bind_vars={'nconst': ClickedNodeID, 'myoffset': myoffset, 'mycount': maxnodespergraph }
        edge_query_bind_vars={'nconst': ClickedNodeID, 'myoffset': myoffset, 'mycount': maxnodespergraph }

        #Since This is a Click need to Figure out if a Name or Film
        if ClickedNodeID[0:2]=='nm':
            myID="name_basics/"+ClickedNodeID
        else:
            myID="title_basics/"+ClickedNodeID
        new_CenterNode=[ {'data': {'id': myID, 'label': label}} ]

        #Run Query - For Nodes we can use the query for both Person and Title Centered
        new_nodes = run_cloud_query(NodesForPersonAtCenterForCyto,node_query_bind_vars)
        #Get the total nodes return to update the page list
        total_node_query_bind_vars={'nconst': ClickedNodeID }
        total_return_nodes_json = run_cloud_query(TotalNodesForPersonAtCenterForCyto,total_node_query_bind_vars)
        total_return_nodes=total_return_nodes_json[0]['nodecount']
        maxpages=math.ceil(total_return_nodes/maxnodespergraph)

        new_nodes=new_nodes+new_CenterNode 
        new_edges = run_cloud_query(EdgesForPersonAtCenterForCyto,edge_query_bind_vars)
    return new_edges+new_nodes,ClickedNode,total_return_nodes,maxpages,pagenumber


#Add Person to Relation Test
@app.callback(
    Output('person1nconst', 'children'),
    Output('person1name', 'children'),
    Output('person2nconst', 'children'),
    Output('person2name', 'children'),
    Input('submit-person1', 'n_clicks'),
    Input('submit-person2', 'n_clicks'),
    State('container-add-person', 'children')
)

def update_output(n_clicks,n_clicks2,value):

    if value==None:
        ClickedNodeName=person1Name
        ClickedNodeNconst=person1nconst
    else:
        myjson=json.loads(value)
        myid=repr(myjson['id'])
        ClickedNodeNconst=myid.split("/")[1] 
        ClickedNodeName=repr(myjson['label'])
        ClickedNodeName = re.sub("[']", '', ClickedNodeName)
        ClickedNodeNconst = re.sub("[']", '', ClickedNodeNconst)

    #Set Default Left Button
    myreturns=[ClickedNodeNconst,ClickedNodeName, dash.no_update,dash.no_update]

    if "submit-person1" == ctx.triggered_id:
        myreturns=[ClickedNodeNconst,ClickedNodeName, dash.no_update,dash.no_update]
    if "submit-person2" == ctx.triggered_id:
        myreturns=[dash.no_update,dash.no_update,ClickedNodeNconst,ClickedNodeName]
    return myreturns

#Callback to get context menu on Cytoscape
# For Javscript Just update the Div with the data

@app.callback(
    Output('output-serverside-imdb', 'children'),
    Output('output-serverside-title', 'children'), 
    Input('cytoscape1', 'mouseoverNodeData')
)
def toggle_modal(mouseoverData):
    if mouseoverData!=None:
        #get nconst from id
        mouseoverid=mouseoverData['id'].split("/")[1]
        RightClickheader=mouseoverData['label']
    else:
        mouseoverid='nm0000102'
        RightClickheader='MyHeader'
    return mouseoverid,RightClickheader

#For The Relationship between 2 People
@app.callback(
    Output('person-relationship', 'children'),
    Output('relationship_dashtable', 'children'),
    Input('show-relationship', 'n_clicks'),
    State('person1nconst', 'children'),
    State('person2nconst', 'children')
)
def update_output(n_clicks,value1,value2):
    relationship_results=get_relationships(value1,value2)
    #Add Everything to one line and then use BR tag to show different lines
    relationship_results_text = ''
    for doc in relationship_results:
        results_text=repr(doc) 
        relationship_results_text = relationship_results_text  + results_text
 
    #get rid of: , ' [  ]    
    for char in """[],'""":
        relationship_results_text = relationship_results_text.replace(char,'')  
    return 'The button has been clicked {} times. And the Relationship between {} and {} is: '.format(n_clicks,value1,value2), return_ducument(relationship_results_text)

if __name__ == '__main__':
    app.run_server(host=env.LOCALHOST, port=env.LOCALPORT, debug=True)