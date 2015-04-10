use tianchi;

CREATE TABLE IF NOT EXISTS 31day_train_user(
user_id INT NOT NULL ,
item_id INT NOT NULL ,
behavior_type INT  ,
user_geohash VARCHAR(255),
item_catagory INT  ,
daydiff INT NOT NULL
);

CREATE TABLE IF NOT EXISTS 31day_user_look(
user_id INT NOT NULL,
item_id INT NOT NULL,
look VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS 31day_user_store(
user_id INT NOT NULL,
item_id INT NOT NULL,
store VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS 31day_user_cart(
user_id INT NOT NULL,
item_id INT NOT NULL,
cart VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS 31day_user_buy(
user_id INT NOT NULL,
item_id INT NOT NULL,
buy VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS 31day_user_features(
user_id INT NOT NULL,
item_id INT NOT NULL,
look VARCHAR(255) ,
store VARCHAR(255) ,
cart VARCHAR(255) ,
buy VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS 31day_pure_data(
user_id INT NOT NULL,
item_id INT NOT NULL,
look VARCHAR(255) ,
store VARCHAR(255) ,
cart VARCHAR(255) ,
buy VARCHAR(255)
);