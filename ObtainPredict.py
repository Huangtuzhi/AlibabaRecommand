#!/usr/bin/python env
# -*- coding: utf-8 -*-
import numpy as np
from sklearn.linear_model import LogisticRegression
__author__ = 'Huang yi'


class PredictEmption(object):
    def __init__(self):
        pass

    def DivideSet(self):
        # 第一次加载重写txt文件到numpy的格式npy中。函数依次运行一次。
        train_data = np.loadtxt('data_features.txt')
        train_data_label = np.loadtxt('data_labels.txt')
        np.save('data_features.npy', train_data)
        np.save('data_labels.npy', train_data_label)
        fop1 = open('feature_pos.txt', 'w+')
        fop2 = open('feature_neg.txt', 'w+')

        train_data = np.load('data_features.npy')
        train_data_label = np.load('data_labels.npy')
        label_size = train_data_label.size
        # 转置
        train_data_label.shape = (1, label_size)
        train_data_label_transpose = np.transpose(train_data_label)
        # 将label加到每行特征的最后
        line = data_with_label = np.hstack((train_data, train_data_label_transpose))

        # 把正例和负例分着放入feature_pos.txt和feature_neg.txt中
        for i in range(0, label_size):
            if(line[i][-1]):
                fop1.write('%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d' %
                (line[i][0],line[i][1],line[i][2],line[i][3],line[i][4],line[i][5],line[i][6],line[i][7],line[i][8],line[i][9],
                 line[i][10],line[i][11],line[i][12],line[i][13],line[i][14],line[i][15],line[i][16],line[i][17],line[i][18],line[i][19]))
                fop1.write('\n')
            else:
                fop2.write('%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d' %
                (line[i][0],line[i][1],line[i][2],line[i][3],line[i][4],line[i][5],line[i][6],line[i][7],line[i][8],line[i][9],
                 line[i][10],line[i][11],line[i][12],line[i][13],line[i][14],line[i][15],line[i][16],line[i][17],line[i][18],line[i][19]))
                fop2.write('\n')
        fop1.close()
        fop2.close()

        feature_pos = np.loadtxt('feature_pos.txt')
        feature_neg = np.loadtxt('feature_neg.txt')
        np.save('feature_p.npy', feature_pos)
        np.save('feature_n.npy', feature_neg)


    def GenTrainTestSet(self):
        feature_pos = np.load('feature_p.npy')
        feature_neg = np.load('feature_n.npy')

        # 打乱生成随机序列
        np.random.shuffle(feature_pos)
        np.random.shuffle(feature_neg)

        TrainSet = np.vstack((feature_pos[0:800], feature_neg[0:500000]))
        TestSet = np.vstack((feature_pos[800:999], feature_neg[500000:750000]))

        np.save('TrainSet.npy', TrainSet)
        np.save('TestSet.npy', TestSet)

    def TrainAndPredict(self, train_data, train_data_label, predict_data):
        # 应用Logistic回归进行预测
        LR = LogisticRegression()
        LR.fit(train_data, train_data_label)
        predict_labels = LR.predict(predict_data)
        # 0为不买的概率，1为买的概率
        predict_proba = LR.predict_proba(predict_data)[:, -1]
        return predict_labels, predict_proba

    def GetF1(self, predict_list, real_list):
        _list = [x for x in predict_list if x in real_list]
        equal_num = len(_list)
        prediction_set_num = len(predict_list)
        reference_set_num = len(real_list)

        precision = float(equal_num) / prediction_set_num
        recall = float(equal_num) / reference_set_num
        f1 = float(2 * precision * recall) / (precision + recall)
        return precision, recall, f1

    # 用30day的TrainSet和TestSet测试，选出最优阈值
    def TestPredict(self):
        train_set = np.load('TrainSet.npy')
        test_set = np.load('TestSet.npy')

        train_data = train_set[:, 0:-1]   # 去除label后的特征数据
        train_data_label = train_set[:, -1]   # label
        test_data = test_set[:, 0:-1]   # 不需要label
        test_data_label = test_set[:, -1]   # label

        predict_labels, predict_proba = self.TrainAndPredict(train_data, train_data_label, test_data)

        # 测试出最优的阈值设置
        # best_th = 0.014
        for i in range(0, 2):
            rough_set = float(i) / 10
            for j in range(0, 100):
                tiny_set = float(j)/1000
                th = rough_set + tiny_set

                # 预测出的购买的list
                index = np.array(range(0, len(predict_proba)))
                # 大于阈值对应的索引
                index_predict = index[predict_proba > th]
                index_predict = list(index_predict)

                # 真实购买的list
                index_real = index[test_data_label > 0]
                precision, recall, f1 = self.GetF1(index_predict, index_real)
                print 'TH %s : %s %s %s | %s %s' % (th, precision, recall, f1, len(index_predict), len(index_real))

        # index = np.array(range(0, len(predict_proba)))
        # # 大于阈值对应的索引
        # index_predict = index[predict_proba > best_th]
        # index_predict = list(index_predict)
        # # 真实购买的list
        # index_real = index[test_data_label > 0]
        # precision, recall, f1 = self.GetF1(index_predict, index_real)
        # print 'TH %s : %s %s %s' % (best_th, precision, recall, f1)

if __name__ == '__main__':
    # predict_data = np.load('predict_data.txt')
    # PE.TrainAndPredict(train_data, train_data_label, predict_data)
    # LR = LogisticRegression()
    # ret = LR.fit(train_data, train_data_label)
    # predict_labels = LR.predict(train_data[3000:3005])
    PE = PredictEmption()
    # PE.DivideSet()
    # PE.GenTrainTestSet()
    PE.TestPredict()