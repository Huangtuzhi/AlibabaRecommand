use tianchi;

CREATE TABLE IF NOT EXISTS train_user_before(
user_id INT NOT NULL ,
item_id INT NOT NULL ,
behavior_type INT NOT NULL ,
user_geohash VARCHAR(255),
item_catagory INT NOT NULL ,
daydiff INT NOT NULL
);

CREATE TABLE IF NOT EXISTS train_user_after(
user_id INT NOT NULL ,
item_id INT NOT NULL ,
behavior_type INT NOT NULL ,
user_geohash VARCHAR(255),
item_catagory INT NOT NULL ,
daydiff INT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_look(
user_id INT NOT NULL,
item_id INT NOT NULL,
look VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_store(
user_id INT NOT NULL,
item_id INT NOT NULL,
store VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_cart(
user_id INT NOT NULL,
item_id INT NOT NULL,
cart VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_buy(
user_id INT NOT NULL,
item_id INT NOT NULL,
buy VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_features(
user_id INT NOT NULL,
item_id INT NOT NULL,
look VARCHAR(255) NOT NULL,
store VARCHAR(255) NOT NULL,
cart VARCHAR(255) NOT NULL,
buy VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS pure_data(
user_id INT NOT NULL,
item_id INT NOT NULL,
look VARCHAR(255) ,
store VARCHAR(255) ,
cart VARCHAR(255) ,
buy VARCHAR(255)
);