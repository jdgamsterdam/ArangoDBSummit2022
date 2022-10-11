require('@arangodb');

//These need to be cleaned before putting on GitHub
const databaseName='Movies'
const moviesUserName='USER';
const moviesUserNamePassword='PASSWORD';
const users=require("@arangodb/users");
const allusers=users.all();
//The following show string list of databases but will only work if logged into system 
const alldatabases=db._databases();

//Create Database if it does not exist
var database_exists = alldatabases.includes(databaseName);

if (database_exists){
    //Do Nothing
    console.log(database_exists);
    }
else{
    console.log('No Database');
    //Create New Database
    db._createDatabase(databaseName);
    }

var userexists = allusers.find(myuser => myuser.user === moviesUserName);

if (userexists == null){
    console.log('No User');
    //Create New User
    users.save(moviesUserName,moviesUserNamePassword);
    users.grantDatabase(moviesUserName, databaseName, 'rw');
    }
else{
  console.log(userexists)
    }