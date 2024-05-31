#!/usr/bin/arangosh --javascript.execute

db._createDatabase("test");
db._useDatabase("test");

db._create('test');

db._query(`
    FOR i IN 1..1000
        INSERT {
            name: CONCAT("test", i),
            test: (i % 3 == 0 ? true : false)
        } IN test
`);
