CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    login    VARCHAR UNIQUE,
    password TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    cat_id         INTEGER   PRIMARY KEY AUTOINCREMENT,
    codename CHAR (10) PRIMARY KEY,
    name     CHAR (10),
    creator  VARCHAR,
    included TEXT,
    FOREIGN KEY (
        creator
    )
    REFERENCES users (login) ON UPDATE CASCADE
                             ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS costs (
    cost_id         INTEGER   PRIMARY KEY AUTOINCREMENT,
    sum_of_money_co INT,
    descrip_co      TEXT,
    category        CHAR (10),
    who_spend       VARCHAR,
    view_date       CHAR (10),
    created         DATETIME,
    FOREIGN KEY (
        who_spend
    )
    REFERENCES users (login) ON UPDATE CASCADE
                             ON DELETE CASCADE
);
