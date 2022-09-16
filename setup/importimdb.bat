call env.bat

arangoimport --file title.akas.tsv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --collection=title_akas --create-collection=true --type=tsv --translate "tconst=_key" 

arangoimport --file title.basics.tsv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --collection=title_basics --create-collection=true --type=tsv --translate "tconst=_key" 

arangoimport --file title.crew.tsv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --collection=title_crew --create-collection=true --type=tsv --translate "tconst=_key" 

arangoimport --file title.episode.tsv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --collection=title_episodes --create-collection=true --type=tsv  --translate "tconst=_key" 

arangoimport --file name.basics.tsv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --collection=name_basics --create-collection=true --type=tsv  --translate "nconst=_key" 

arangoimport --file title.ratings.tsv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword%  --server.database Movies --collection=title_ratings --create-collection=true --type=tsv  --translate "tconst=_key" 

arangoimport --file professions_basics.csv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --collection=professions_basics --create-collection=true --type=csv --translate "Profession=_key" 

arangoimport --file genres_basics.csv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --collection=genres_basics --create-collection=true --type=csv --translate "Genres=_key"

::In this Both tconst and nconst are repeated so need to import with unique ID
arangoimport --file title.principals.tsv --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --collection=title_principals --create-collection=true --type=tsv