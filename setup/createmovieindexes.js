require('@arangodb'); 
var analyzers = require("@arangodb/analyzers");
db.movie_edges_direct.ensureIndex({ type: "persistent", fields: [ "job" ], name: "myjob", inBackground: true  });
db.name_basics.ensureIndex({ type: "persistent", fields: [ "primaryName" ], name: "myName", inBackground: true });
db.title_basics.ensureIndex({ type: "persistent", fields: [ "primaryTitle" ], name: "myTitle", inBackground: true });

//Create The Name Basics View
v = db._createView("name_basics_primaryName_view", "arangosearch");
//Modify The Properties
v.properties({links: {name_basics: {includeAllFields: true}}})

//Create The Title Basics View
t = db._createView("title_basics_view", "arangosearch");
//Modify The Properties
t.properties({links: {title_basics: {includeAllFields: true}}})
