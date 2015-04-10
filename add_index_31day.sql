use tianchi;

#CREATE INDEX train_user_userid_itemid ON          31day_train_user(user_id, item_id);
#CREATE INDEX pure_data_userid_itemid ON           31day_pure_data(user_id, item_id);
#CREATE INDEX user_features_userid_itemid ON        31day_user_features(user_id, item_id);

#CREATE INDEX user_look_userid_itemid ON            31day_user_look(user_id, item_id);
#CREATE INDEX user_store_userid_itemid ON           31day_user_store(user_id, item_id);
#CREATE INDEX user_cart_userid_itemid ON            31day_user_cart(user_id, item_id);
#CREATE INDEX user_buy_userid_itemid ON             31day_user_buy(user_id, item_id);
CREATE INDEX train_item_itemid ON                   train_item(item_id);