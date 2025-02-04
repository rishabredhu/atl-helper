DROP TABLE IF EXISTS tourbookings;
DROP TABLE IF EXISTS tourgroups;
DROP TABLE IF EXISTS itineraries;
DROP TABLE IF EXISTS destinations;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS tours;

CREATE TABLE tours (
    tourid INTEGER PRIMARY KEY AUTOINCREMENT,
    tourname TEXT NOT NULL,
    agerestriction INTEGER NOT NULL
);

CREATE TABLE tourgroups (
    tourgroupid INTEGER PRIMARY KEY AUTOINCREMENT,
    tourid INTEGER,
    startdate DATE,
    FOREIGN KEY (tourid) REFERENCES tours (tourid)
);

CREATE TABLE customers (
    customerid INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT,
    familyname TEXT NOT NULL,
    dob DATE,
    email TEXT,
    phone TEXT
);

CREATE TABLE destinations (
    destinationid INTEGER PRIMARY KEY AUTOINCREMENT,
    destinationname TEXT NOT NULL
);

CREATE TABLE itineraries (
    itineraryid INTEGER PRIMARY KEY AUTOINCREMENT,
    tourid INTEGER NOT NULL,
    destinationid INTEGER NOT NULL,
    FOREIGN KEY (tourid) REFERENCES tours (tourid),
    FOREIGN KEY (destinationid) REFERENCES destinations (destinationid)
);

CREATE TABLE tourbookings (
    bookingid INTEGER PRIMARY KEY AUTOINCREMENT,
    tourgroupid INTEGER,
    customerid INTEGER,
    FOREIGN KEY (tourgroupid) REFERENCES tourgroups (tourgroupid),
    FOREIGN KEY (customerid) REFERENCES customers (customerid)
);
