use tianchi;

DROP TABLE IF EXISTS train_item;
DROP TABLE IF EXISTS train_user;

CREATE TABLE train_item(
item_id  INT NOT NULL,
item_geohash VARCHAR(255),
item_catagory INT
);

CREATE TABLE train_user(
user_id INT NOT NULL,
item_id INT NOT NULL,
behavior_type INT,
user_geohash VARCHAR(255),
item_catagory INT,
time datetime
);


