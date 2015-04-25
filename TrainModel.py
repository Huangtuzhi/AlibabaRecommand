#!/usr/bin/python env
# -*- coding: utf-8 -*-
import MySQLdb
import MySQLdb.cursors
import numpy as np
__author__ = 'Huang yi'

divide_before_sql = '''INSERT INTO train_user_before
(user_id,item_id,behavior_type,user_geohash,item_catagory, daydiff)
SELECT user_id,item_id,behavior_type,user_geohash,item_catagory,DATEDIFF(time, '2014-11-18') AS daydiff
FROM train_user WHERE time<= '%s' '''

divide_after_sql = '''INSERT INTO train_user_after
(user_id,item_id,behavior_type,user_geohash,item_catagory, daydiff)
SELECT user_id,item_id,behavior_type,user_geohash,item_catagory,DATEDIFF(time, '2014-11-18') AS daydiff
FROM train_user WHERE time> '%s' '''

merge_look_sql = '''INSERT INTO user_look
(user_id, item_id, look)
SELECT user_id, item_id, group_concat(daydiff) as look
FROM train_user_before WHERE behavior_type=1 GROUP BY user_id, item_id '''

merge_store_sql = '''INSERT INTO user_store
(user_id, item_id, store)
SELECT user_id, item_id, group_concat(daydiff) as store
FROM train_user_before WHERE behavior_type=2 GROUP BY user_id, item_id '''

merge_cart_sql = '''INSERT INTO user_cart
(user_id, item_id, cart)
SELECT user_id, item_id, group_concat(daydiff) as cart
FROM train_user_before WHERE behavior_type=3 GROUP BY user_id, item_id '''

merge_buy_sql = '''INSERT INTO user_buy
(user_id, item_id, buy)
SELECT user_id, item_id, group_concat(daydiff) as buy
FROM train_user_before WHERE behavior_type=4 GROUP BY user_id, item_id '''

# 四个表合并太慢，先建立索引。这里应该用outer join，但mysql没有。后面再补充。
merge_all_behavoir = '''INSERT INTO user_features
(user_id, item_id, look, store, cart, buy)
SELECT user_look.user_id, user_look.item_id,
user_look.look, user_store.store, user_cart.cart, user_buy.buy
FROM user_look
LEFT join  user_store ON user_look.user_id = user_store.user_id AND
                        user_look.item_id = user_store.item_id
LEFT join  user_cart  ON user_look.user_id = user_cart.user_id AND
                        user_look.item_id = user_cart.item_id
LEFT join  user_buy   ON user_look.user_id = user_buy.user_id AND
                        user_look.item_id = user_buy.item_id'''

class TrainModel(object):
    def __init__(self):
        self.db = MySQLdb.connect("localhost", "root", "199194", "tianchi",
                                  cursorclass = MySQLdb.cursors.DictCursor)
        self.cursor = self.db.cursor()
        # 这个数据库连接用来查询train_user_after 31th的数据
        self.db2 = MySQLdb.connect("localhost", "root", "199194", "tianchi",
                                  cursorclass = MySQLdb.cursors.DictCursor)
        self.cursor2 = self.db2.cursor()

    def DivideByTime(self, breaktime):
        sql1 = divide_before_sql % breaktime
        sql2 = divide_after_sql % breaktime
        try:
            self.cursor.execute(sql1)
            self.db.commit()
            self.cursor.execute(sql2)
            self.db.commit()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            self.db.rollback()
        self.db.close

    def MergeData(self):
        try:
            # self.cursor.execute(merge_look_sql)
            # self.db.commit()
            # self.cursor.execute(merge_store_sql)
            # self.db.commit()
            # self.cursor.execute(merge_cart_sql)
            # self.db.commit()
            # self.cursor.execute(merge_buy_sql)
            # self.db.commit()
            self.cursor.execute(merge_all_behavoir)
            self.db.commit()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            self.db.rollback()
        self.db.close

    # 当用原始数据统计的四种行为（在表user_features中）符合某个标准，则输出到文本并插入到表pure_data中
    def SimplifyTrainUser(self):
        # 一次处理150万数据，多了内存占用过高
        # (limit 0, 1500000 -> limit 1500000, 1500000 -> limit 3000000, 2000000)
        self.cursor.execute('SELECT user_id, item_id, look, store, cart, buy FROM user_features limit') # 注意加limit再跑程序
        fop = open('feature.txt', 'a')
        while True:
            str_all=self.cursor.fetchone()
            if str_all:
                look_times = len(str_all['look'].split(',')) if str_all['look'] else 0
                store_times = len(str_all['store'].split(',')) if str_all['store'] else 0
                cart_times = len(str_all['cart'].split(',')) if str_all['cart'] else 0
                buy_times = len(str_all['buy'].split(',')) if str_all['buy'] else 0
                lru = max(str_all['look'].split(',') + str_all['store'].split(',') + str_all['cart'].split(',') + str_all['buy'].split(','))
                # 注意look等项在DB中应该为NOT NULL，不然lru会出错。
                user_id = str_all['user_id']
                item_id = str_all['item_id']

                buy_flag = False
                self.cursor2.execute('SELECT behavior_type FROM train_user_after WHERE user_id=%s AND item_id=%s', (user_id, item_id))
                behaviors = self.cursor2.fetchall()
                if behaviors:
                    for be in behaviors:
                        if be['behavior_type'] == 4:
                            buy_flag = True   # 说明在31th有购买行为，保留作为label

                # 如果浏览次数小于 && 收藏次数小于1 && 最近15天没有记录
                if not (look_times + store_times + cart_times <= 7 and buy_times==0 and int(lru) <= 21 and buy_flag == False ):
                    fop.write('%d,%d,\"%s\",\"%s\",\"%s\",\"%s\"' % (user_id,item_id,str_all['look'],str_all['store'],str_all['cart'],str_all['buy']) )
                    fop.write('\n')

            else:
                fop.close()
                return 0

    # 特征：一个内四种行为次数 + 总和 (基于简单特征的策略)
    def ExtractMonthlyBehavior(self, user_id, item_id):
        self.cursor.execute('SELECT look, store, cart, buy FROM pure_data WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        str_all = self.cursor.fetchall()
        if not str_all:
            raise TypeError('Database NULL!')
        look_times = len(str_all[0]['look'].split(',')) if str_all[0]['look'] else 0
        store_times = len(str_all[0]['store'].split(',')) if str_all[0]['store'] else 0
        cart_times = len(str_all[0]['cart'].split(',')) if str_all[0]['cart'] else 0
        buy_times = len(str_all[0]['buy'].split(',')) if str_all[0]['buy'] else 0
        all_times = look_times + store_times + cart_times + buy_times

        feature = (look_times, store_times, cart_times, buy_times, all_times )
        return feature

    # 特征：最后四天四种行为次数 + 总和 (基于简单特征的策略)
    def ExtractLastdaysBehavior(self, user_id, item_id):
        self.cursor.execute('SELECT look, store, cart, buy FROM pure_data WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        str_all = self.cursor.fetchall()
        if not str_all:
            raise TypeError('Database NULL!')

        look_times = store_times = cart_times = buy_times = 0
        look_date = str_all[0]['look'].split(',') if str_all[0]['look'] else 0
        store_date = str_all[0]['store'].split(',') if str_all[0]['store'] else 0
        cart_date = str_all[0]['cart'].split(',') if str_all[0]['cart'] else 0
        buy_date = str_all[0]['buy'].split(',') if str_all[0]['buy'] else 0

        if look_date:
            for l in look_date:
                if l and int(l) >= 26:
                    look_times += 1
        if store_date:
            for l in store_date:
                if l and int(l) >= 26:
                    store_times += 1
        if cart_date:
            for l in cart_date:
                if l and int(l) >= 26:
                    cart_times += 1
        if buy_date:
            for l in buy_date:
                if l and int(l) >= 26:
                    buy_times += 1

        all_times = look_times + store_times + cart_times + buy_times
        feature = (look_times, store_times, cart_times, buy_times, all_times )
        return feature

    # 特征：最后一次行为离分割点的间隔
    def ExtractLRUsed(self, user_id, item_id):
        self.cursor.execute(' SELECT max(daydiff) FROM train_user_before WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        LRU = self.cursor.fetchall()
        LRUnumber = LRU[0]['max(daydiff)'] if LRU else 0
        feature = int(LRUnumber)
        return feature

    # 特征： 最近一天收藏，加购的次数（基于有购物倾向的策略）
    def ExtractLast1Trend(self, user_id, item_id):
        self.cursor.execute('SELECT store, cart FROM pure_data WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        str_all = self.cursor.fetchall()
        if not str_all:
            raise TypeError('Database NULL!')

        store_times = cart_times = 0
        store_date = str_all[0]['store'].split(',') if str_all[0]['store'] else 0
        cart_date = str_all[0]['cart'].split(',') if str_all[0]['cart'] else 0

        if store_date:
            for l in store_date:
                if l and int(l) == 29:
                    store_times += 1
        if cart_date:
            for l in cart_date:
                if l and int(l) == 29:
                    cart_times += 1
        feature = (store_times, cart_times)
        return feature

    # 特征： 最近三天查看，收藏，加购的次数（基于有购物倾向的策略）
    def ExtractLast3Trend(self, user_id, item_id):
        self.cursor.execute('SELECT look, store, cart FROM pure_data WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        str_all = self.cursor.fetchall()
        if not str_all:
            raise TypeError('Database NULL!')

        look_times=store_times = cart_times = 0
        look_date = str_all[0]['look'].split(',') if str_all[0]['look'] else 0
        store_date = str_all[0]['store'].split(',') if str_all[0]['store'] else 0
        cart_date = str_all[0]['cart'].split(',') if str_all[0]['cart'] else 0

        if look_date:
            for l in look_date:
                if l and int(l) >= 27:
                    look_times += 1
        if store_date:
            for l in store_date:
                if l and int(l) == 27:
                    store_times += 1
        if cart_date:
            for l in cart_date:
                if l and int(l) == 27:
                    cart_times += 1

        feature = (look_times, store_times, cart_times)
        return feature

    # 特征： 最近一天，三天,七天购买的次数（基于买过不会再买的策略）
    def ExtractLast7Buy(self, user_id, item_id):
        self.cursor.execute('SELECT buy FROM pure_data WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        str_all = self.cursor.fetchall()
        if not str_all:
            raise TypeError('Database NULL!')

        buy_times_1day = buy_times_3day = buy_times_7day = 0
        buy_date = str_all[0]['buy'].split(',') if str_all[0]['buy'] else 0

        if buy_date:
            for l in buy_date:
                if l and int(l) == 29:
                    buy_times_1day += 1
                if l and int(l) >= 27:
                    buy_times_3day += 1
                if l and int(l) >= 23:
                    buy_times_7day += 1

        feature = (buy_times_1day, buy_times_3day, buy_times_7day)
        return feature


    def MergeFeatures(self):
        fop = open('data_features.txt', 'a')
        self.cursor.execute('SELECT user_id, item_id FROM pure_data')
        record = self.cursor.fetchall()
        for rec in record:
            userid = rec['user_id']
            itemid = rec['item_id']

            # 融合所有特征 19D
            feature0 = self.ExtractMonthlyBehavior(userid, itemid)    # 5D
            feature1 = self.ExtractLastdaysBehavior(userid, itemid)   # 5D
            feature2 = self.ExtractLRUsed(userid, itemid)             # 1D
            feature3 = self.ExtractLast1Trend(userid, itemid)         # 2D
            feature4 = self.ExtractLast3Trend(userid, itemid)         # 3D
            feature5 = self.ExtractLast7Buy(userid, itemid)           # 3D
            features = feature0, feature1, feature2, feature3, feature4, feature5
            line = features[0] + features[1] + (features[2],) + features[3] + features[4] + features[5]
            fop.write('%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d' % (line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],line[9],
            line[10],line[11],line[12],line[13],line[14],line[15],line[16],line[17],line[18]))
            fop.write('\n')
        fop.close()

    def GenLabels(self):
        fop = open('data_labels.txt', 'a')
        self.cursor.execute('SELECT user_id, item_id FROM pure_data')
        record = self.cursor.fetchall()
        for rec in record:
            userid = rec['user_id']
            itemid = rec['item_id']
            purchase_flag = False
            self.cursor.execute('SELECT behavior_type FROM train_user_after WHERE user_id=%s AND item_id=%s', (userid, itemid))
            lines = self.cursor.fetchall()
            if lines:
                for line in lines:
                    if line['behavior_type'] == 4:
                        purchase_flag = True
            if purchase_flag:
                fop.write('1')
                fop.write('\n')
            else:
                fop.write('0')
                fop.write('\n')
        fop.close()

if __name__ == '__main__':
    model = TrainModel()
    # model.DivideByTime("2014-12-18 00:00:00")
    # model.MergeData()
    # model.SimplifyTrainUser()
    # model.MergeFeatures() # 比较耗时间
    model.GenLabels()