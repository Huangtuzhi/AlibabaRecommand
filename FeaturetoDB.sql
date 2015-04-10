use tianchi;
LOAD DATA INFILE '/home/huangyi/Desktop/tianchi/feature.txt'
INTO TABLE tianchi.pure_data
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n';