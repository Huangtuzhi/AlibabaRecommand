use tianchi;

-- CREATE INDEX user_look_userid_itemid ON            user_look(user_id, item_id);
-- CREATE INDEX user_store_userid_itemid ON           user_store(user_id, item_id);
-- CREATE INDEX user_cart_userid_itemid ON            user_cart(user_id, item_id);
-- CREATE INDEX user_buy_userid_itemid ON             user_buy(user_id, item_id);
-- CREATE INDEX user_features_userid_itemid ON        user_features(user_id, item_id);

-- CREATE INDEX train_user_before_userid_itemid ON    train_user_before(user_id, item_id);
-- CREATE INDEX train_user_after_userid_itemid ON     train_user_after(user_id, item_id);

CREATE INDEX pure_data_userid_itemid ON           pure_data(user_id, item_id);

