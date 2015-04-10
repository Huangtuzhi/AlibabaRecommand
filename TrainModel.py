#!/usr/bin/python env
#-*- coding: utf-8 -*-
import MySQLdb
import MySQLdb.cursors
import numpy as np
__author__ = 'huangyi'

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

#四个表合并太慢，先建立索引。这里应该用outer join，但mysql没有。后面再补充。
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

unique_user_sql = '''INSERT INTO unique_user
(user_id, item_id) SELECT user_id, item_id
FROM train_user_before GROUP BY user_id, item_id '''


DELETE_INDEX = 0

class TrainModel(object):
    def __init__(self):
        self.db = MySQLdb.connect("localhost", "root", "199194", "tianchi",
                                  cursorclass = MySQLdb.cursors.DictCursor)
        self.cursor = self.db.cursor()

    def DivideByTime(self, breaktime):
        sql1 = divide_before_sql % breaktime
        sql2 = divide_after_sql % breaktime
        try:
            self.cursor.execute(sql1)
            self.db.commit()
            self.cursor.execute(sql2)
            self.db.commit()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            self.db.rollback()
        self.db.close

    def MergeData(self):
        try:
            '''
            self.cursor.execute(merge_look_sql)
            self.db.commit()
            self.cursor.execute(merge_store_sql)
            self.db.commit()
            self.cursor.execute(merge_cart_sql)
            self.db.commit()
            self.cursor.execute(merge_buy_sql)
            self.db.commit()
            self.cursor.execute(merge_all_behavoir)
            self.db.commit()
            self.cursor.execute(unique_user_sql)
            self.db.commit()
            '''
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            self.db.rollback()
        self.db.close

    #当用原始数据统计的四种行为（在表user_look,user_store中）符合某个标准，则输出到文本并插入到表pure_data中
    def SimplifyTrainUser(self):
        #一次处理100万左右数据，多了内存占用过高
        self.cursor.execute('SELECT user_id, item_id, look, store, cart, buy FROM user_features')
        fop = open('feature.txt', 'a')
        while True:
            str_all=self.cursor.fetchone()
            if str_all:
                look_times = len(str_all['look'].split(',')) if str_all['look'] else 0
                store_times = len(str_all['store'].split(',')) if str_all['store'] else 0
                cart_times = len(str_all['cart'].split(',')) if str_all['cart'] else 0
                buy_times = len(str_all['buy'].split(',')) if str_all['buy'] else 0
                lru = max(str_all['look'].split(',') + str_all['store'].split(',') + str_all['cart'].split(',') + str_all['buy'].split(','))
                user_id = str_all['user_id']
                item_id = str_all['item_id']

                #如果不是 浏览次数小于4 && 收藏次数小于1 && 最近15天没有记录
                if not (look_times + store_times + cart_times <= 7 and buy_times==0 and int(lru) <= 21 ):
                    fop.write('%d,%d,\"%s\",\"%s\",\"%s\",\"%s\"' % (user_id,item_id,str_all['look'],str_all['store'],str_all['cart'],str_all['buy']) )
                    fop.write('\n')
                    global DELETE_INDEX
                    DELETE_INDEX += 1

            else:
                fop.close()
                return 0

    #特性：一个内四种行为次数 + 总和
    def ExtractMonthlyBehavior(self, user_id, item_id):
        self.cursor.execute('SELECT look, store, cart, buy FROM pure_data WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        str = self.cursor.fetchall()
        if not str:
            return 0
        look_times = len(str[0]['look'].split(',')) if str[0]['look'] else 0
        store_times = len(str[0]['store'].split(',')) if str[0]['store'] else 0
        cart_times = len(str[0]['cart'].split(',')) if str[0]['cart'] else 0
        buy_times = len(str[0]['buy'].split(',')) if str[0]['buy'] else 0
        all_times = look_times + store_times + cart_times + buy_times

        feature = (look_times, store_times, cart_times, buy_times, all_times )
        return feature

    #特性：最后四天四种行为次数 + 总和
    def ExtractLastdaysBehavior(self, user_id, item_id):
        self.cursor.execute('SELECT look, store, cart, buy FROM pure_data WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        str = self.cursor.fetchall()
        if not str:
            return 0

        look_times = store_times = cart_times = buy_times = 0
        look_date = str[0]['look'].split(',') if str[0]['look'] else 0
        store_date = str[0]['store'].split(',') if str[0]['store'] else 0
        cart_date = str[0]['cart'].split(',') if str[0]['cart'] else 0
        buy_date = str[0]['buy'].split(',') if str[0]['buy'] else 0

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

    #特征：最后一次行为离分割点的间隔
    def ExtractLRUsed(self, user_id, item_id):
        self.cursor.execute(' SELECT max(daydiff) FROM train_user_before WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        LRU = self.cursor.fetchall()
        LRUnumber = LRU[0]['max(daydiff)'] if LRU else 0
        feature = int(LRUnumber)
        return feature

    def MergeFeatures(self):
        fop = open('data_features.txt', 'a')
        self.cursor.execute('SELECT user_id, item_id FROM pure_data')
        record = self.cursor.fetchall()
        for rec in record:
            userid =  rec['user_id']
            itemid =  rec['item_id']

            #融合所有特征
            feature1 = self.ExtractMonthlyBehavior(userid, itemid)
            feature2 = self.ExtractLastdaysBehavior(userid, itemid)
            feature3 = self.ExtractLRUsed(userid, itemid)
            features = feature1, feature2, feature3
            line = features[0] + features[1] + (features[2],)

            fop.write('%d %d %d %d %d %d %d %d %d %d %d' % (line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],line[9],line[10]))
            fop.write('\n')
        fop.close()

    def GenLabels(self):
        fop = open('data_labels.txt', 'a')
        self.cursor.execute('SELECT user_id, item_id FROM pure_data')
        record = self.cursor.fetchall()
        for rec in record:
            userid =  rec['user_id']
            itemid =  rec['item_id']
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
    #model.DivideByTime("2014-12-18 00:00:00")
    #model.MergeData()
    #model.SimplifyTrainUser()
    #print DELETE_INDEX
    #print model.ExtractMonthlyBehavior(19095, 14148321)
    #print model.ExtractLastdaysBehavior(19095, 15088134)
    #print model.ExtractLRUsed(19095, 15088134)
    #model.MergeFeatures()
    model.GenLabels()