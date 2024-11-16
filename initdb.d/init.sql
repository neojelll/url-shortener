CREATE TABLE long_url (
    long_id SERIAL PRIMARY KEY,
    long_value VARCHAR(250) UNIQUE NOT NULL
);

CREATE TABLE short_url (
    short_id SERIAL PRIMARY KEY,
    short_value VARCHAR(250) NOT NULL
);

CREATE TABLE url_mapping (
    short_id INT REFERENCES short_url(short_id) ON DELETE CASCADE,
    long_id INT REFERENCES long_url(long_id) ON DELETE CASCADE,
    expiration INT NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (short_id, long_id)
);
