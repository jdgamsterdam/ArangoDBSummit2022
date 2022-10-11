
:: As every environment is so vastly different I have not included this. 
::./dockersetup.bat

:: Create Movies Database
:: Done through Javascript

call env.bat
arangosh --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --javascript.execute createmoviedatabases.js

::Download newest IMDB files
./getallimdbfromweb.bat

::Use ArangoImport to import 
./importimdb.bat

:: Create additional collections for Database
python createMovieCollections.py


:: Now done with ArangoSh

arangosh --server.endpoint tcp://%serverendpoint% --server.password %serverpassword% --server.database Movies --javascript.execute createmovieindexes.js
