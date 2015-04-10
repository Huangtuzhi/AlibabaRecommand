#!/usr/bin/python env
#-*- coding: utf-8 -*-
# 由TrainModel更改过来，目的是提取31days的特征。

import MySQLdb
import MySQLdb.cursors
import numpy as np
import string
from ObtainPredict import PredictEmption
__author__ = 'huangyi'

transform_dataformat_sql = '''INSERT INTO 31day_train_user
(user_id,item_id,behavior_type,user_geohash,item_catagory, daydiff)
SELECT user_id,item_id,behavior_type,user_geohash,item_catagory,DATEDIFF(time, '2014-11-18') AS daydiff
FROM train_user'''

merge_look_sql = '''INSERT INTO 31day_user_look
(user_id, item_id, look)
SELECT user_id, item_id, group_concat(daydiff) as look
FROM 31day_train_user WHERE behavior_type=1 GROUP BY user_id, item_id '''

merge_store_sql = '''INSERT INTO 31day_user_store
(user_id, item_id, store)
SELECT user_id, item_id, group_concat(daydiff) as store
FROM 31day_train_user WHERE behavior_type=2 GROUP BY user_id, item_id '''

merge_cart_sql = '''INSERT INTO 31day_user_cart
(user_id, item_id, cart)
SELECT user_id, item_id, group_concat(daydiff) as cart
FROM 31day_train_user WHERE behavior_type=3 GROUP BY user_id, item_id '''

merge_buy_sql = '''INSERT INTO 31day_user_buy
(user_id, item_id, buy)
SELECT user_id, item_id, group_concat(daydiff) as buy
FROM 31day_train_user WHERE behavior_type=4 GROUP BY user_id, item_id '''

#四个表合并太慢，先建立索引。这里应该用outer join，但mysql没有。后面再补充。
merge_all_behavoir = '''INSERT INTO 31day_user_features
(user_id, item_id, look, store, cart, buy)
SELECT 31day_user_look.user_id, 31day_user_look.item_id,
31day_user_look.look, 31day_user_store.store, 31day_user_cart.cart, 31day_user_buy.buy
FROM 31day_user_look
LEFT join  31day_user_store ON 31day_user_look.user_id = 31day_user_store.user_id AND
                               31day_user_look.item_id = 31day_user_store.item_id
LEFT join  31day_user_cart  ON 31day_user_look.user_id = 31day_user_cart.user_id AND
                               31day_user_look.item_id = 31day_user_cart.item_id
LEFT join  31day_user_buy   ON 31day_user_look.user_id = 31day_user_buy.user_id AND
                               31day_user_look.item_id = 31day_user_buy.item_id'''

class TrainModel(object):
    def __init__(self):
        self.db = MySQLdb.connect("localhost", "root", "199194", "tianchi",
                                  cursorclass = MySQLdb.cursors.DictCursor)
        self.cursor = self.db.cursor()

    def MergeData(self):
        try:
            # self.cursor.execute(transform_dataformat_sql)
            # self.db.commit()
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

    #特性：一个内四种行为次数 + 总和
    def ExtractMonthlyBehavior(self, user_id, item_id):
        self.cursor.execute('SELECT look, store, cart, buy FROM 31day_user_features WHERE user_id=%s AND item_id=%s', (user_id, item_id))
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
        self.cursor.execute('SELECT look, store, cart, buy FROM 31day_user_features WHERE user_id=%s AND item_id=%s', (user_id, item_id))
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
        self.cursor.execute(' SELECT max(daydiff) FROM 31day_train_user WHERE user_id=%s AND item_id=%s', (user_id, item_id))
        LRU = self.cursor.fetchall()
        LRUnumber = LRU[0]['max(daydiff)'] if LRU else 0
        feature = int(LRUnumber)
        return feature

    def MergeFeatures(self):
        fop = open('31day_data_features.txt', 'a')
        self.cursor.execute('SELECT user_id, item_id FROM 31day_user_features')
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

    def Transform2Matrix(self):
        #第一次加载重写txt文件到numpy的格式npy中
        #predict_data = np.loadtxt('31day_data_features.txt')
        #np.save('31day_data_features.npy',predict_data)
        pass

    #用31day的31daySet（即所有457万数据的11维特征）得到predict购买的list
    def PerformPredict(self):
        fop = open('predict_all_pairs.txt', 'w+')
        train_set = np.load('TrainSet.npy') #得模型
        predict_data = np.load('31day_data_features.npy') #31天的特征

        train_data = train_set[:,0:-1] #去除label后的特征数据
        train_data_label = train_set[:,-1] #label

        best_th = 0.013 #前面计算出来的
        PE = PredictEmption()
        predict_labels, predict_proba = PE.TrainAndPredict(train_data, train_data_label, predict_data)
        index = np.array(range(0,len(predict_proba)))
        index_predict = index[predict_proba > best_th] #大于阈值对应的索引
        index_predict = list(index_predict) #得到的对应31daySet序号的购买index

        #用一个txt文件lines装带有user_id和item_id。和31daySet顺序对应。
        self.cursor.execute('SELECT user_id, item_id FROM 31day_user_features')
        lines = self.cursor.fetchall()
        for i in index_predict:
             fop.write('%d,%d' % (lines[i]['user_id'],lines[i]['item_id'])) #将预测购买的user_id和item_id写入文件
             fop.write('\n')
        fop.close()

    #用给的商品子集来过滤
    def FilterByItems(self):
        fop = open('filter_pairs.txt', 'w+')
        all_pairs = open('predict_all_pairs.txt', 'r')
        lines = []
        items = [] #保存train_id中出现在 预测中的item_id

        #子集train_item过滤
        while True:
            myString = all_pairs.readline()
            if myString:
                #把predict_all_pairs.txt变为方便解析的list
                myList = map(string.strip, myString.split(','))#去除回车
                lines.append(myList)  #list格式的pairs

            #读取文件完毕后开始处理
            else:
                all = np.array(lines) #矩阵格式的pairs
                self.cursor.execute('SELECT item_id FROM train_item')
                record = self.cursor.fetchall()
                for rec in record:
                    itemid = rec['item_id']
                    #注意两者的类型,all是字符串类型,itemid是long类型
                    if str(itemid) in all[:,1]:
                        items.append(itemid)

                for it in items:
                    for pair in lines:
                        if str(pair[1]) == str(it):
                            fop.write('%d,%d' % (int(pair[0]),int(pair[1])) )
                            fop.write('\n')
                fop.close()
                return 0
    #结果去重复
    def RemoveDuplicate(self):
        fop1 = open('filter_pairs.txt', 'r')
        fop2 = open('remove_pairs.txt', 'w+')

        lines = []
        #filter_pairs去重
        while True:
            myString = fop1.readline()
            if myString:
                myList = map(string.strip, myString.split(','))#去除回车
                lines.append(myList)

            else:
                lines_remove = []
                for it in lines:
                    if it not in lines_remove:
                        lines_remove.append(it)

                for it in lines_remove:
                    fop2.write('%d,%d' % (int(it[0]),int(it[1])))
                    fop2.write('\n')
                fop1.close()
                fop2.close()
                return 0


if __name__ == '__main__':
    model = TrainModel()
    #model.MergeData()
    #model.MergeFeatures()##这个很耗时间
    #model.Transform2Matrix()
    model.PerformPredict()
    model.FilterByItems()
    model.RemoveDuplicate()