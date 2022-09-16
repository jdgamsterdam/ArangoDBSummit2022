
:: As every environment is so vastly different I have not included this. 
::./dockersetup.bat

:: Create Movies Database
:: Done through python script
python createMovieDatabase.py

::Download newest IMDB files
./getallimdbfromweb.sh

::Use ArangoImport to import 
./importimdb.bat

:: Create additional collections for Database
python createMovieCollections.py