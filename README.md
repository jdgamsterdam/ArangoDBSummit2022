This is the project associated with my presentation for the ArangoDB Summit 2022.

To get this to work for your environment you need to edit two files in  "setup" directory with your system details: 
    "env.bat.bak" and rename it to "env.bat" 
    "env.py.bak" and rename it to "env.py"

You need to have Python on your system with the appropriate modules installed (with PIP install). 
These should be: python-arango, pandas, dash, dash-cytoscape, dash-bootstrap-components, beautifulsoup4, pynput

I built it on Python 3.10.6 but there is nothing too much that should not work on earlier versions of Python (except maybe Dash)

To setup all the data go to the Setup directory and run the setupMoviesArango.bat
This is for Windows but should work fairly the same on Linux by changing into to a Shell script.
I have a script for creating and (making some small fixes) to the ArangoDB docker instance but since this is so different in every environment I have not included it.  But contact me if you need help.

I have created the Database (and Programs and Queries) in two different ways. These can be switched by uncommenting the different queries in the movies_arango_cytoscape_nojs.py:  

    1. The first way creates a special collection of Nodes for Both Shows/Movies and People in One "Vertex" Collection called Movie_Nodes and creates Edges to and from that one collection.
      Advantage: It makes the Python and some queries a bit simpler as you don't have to worry whether the "center" node that you are looking at in a display is a Show or a Person, since they both come from the same movie_nodes collection.
    2. The Second way (with queries and collections ending in/Containing "Direct") uses the "title_basics" (Shows) and "name_basics" (People) as is and creates Edges between the two collection
      Advantage: You don't have to create a new movie_nodes collection and, you have access to other Objects in the title_basics and name_basics collections (e.g. birthYear in Name basics) without having to do the AQL equivalent of a Join to get that information.
    3. A Third way (which I did not do) is, when creating the Database initially, load all the name_basics and title_basics directly into the movie_nodes file. While this would not work in a traditional RDBMS since the objects of these to collections are different, but this should work fine in ArangoDB.

Additionally, the file movies_arango_cytoscape_gc.py uses an intermediate google cloud function to query the database. This is because my ArangoDatabase is on an IPv6 network behind a firewall and certain systems only support IPv4 and the Google Cloud function acts as bridge between the two type of networks.
    1. This version also uses a javascript library (xdialog) to show the custom context dialog. To use this instead, rename the dashmodal.js (to dashmodal.js.bak) and the google-cloud-listener.js.bak to google-cloud-listener.js.  The advantage of this method is that you have a lot more flexibility in the layout. The downside is it is more heavily reliant on JavaScript.
