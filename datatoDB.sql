use tianchi;
LOAD DATA INFILE '/home/huangyi/Desktop/tianchi/tianchi_mobile_recommend_train_item.csv'
INTO TABLE tianchi.train_item
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


LOAD DATA INFILE '/home/huangyi/Desktop/tianchi/tianchi_mobile_recommend_train_user.csv'
INTO TABLE tianchi.train_user
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

