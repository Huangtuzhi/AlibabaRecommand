## AlibabaRecommand 

## [介绍](http://tianchi.aliyun.com/competition/introduction.htm?spm=5176.100066.333.2.YI657c&raceId=1)

通过对用户在移动终端上一个月的行为数据进行分析，为后一天的用户购买行为作出预测，进行推荐。


##  目录结构

```
├── LICENSE               #许可证
└── README.md             #使用说明
#建表
├── create_table.sql      #创建基本表
├── add_table.sql         #后续增加的表
├── add_index.sql         #为表建立索引
├── add_table_31day.sql   #建立存储31天数据的表，结构同上
└── add_index_31day.sql   #为表建立索引
#数据导入
├── datatoDB.sql          #csv格式原始数据导入基本表
└── FeaturetoDB.sql       #feature.txt导入对应表
#main
├── __init__.py
├── Utility.py            #工具类
├── TrainModel.py         #特征提取
├── ObtainPredict.py      #生成模型
└── GetFeature31day.py    #进行预测
#数据 
├── feature.txt           #符合某个筛选标准的样本
├── data_features.txt     #feature.txt中记录的n维特征
├── data_features.npy     #转为矩阵格式(numpy库)，下同
├── data_labels.txt       #feature.txt中记录的label(1/0表示购买/未购买)
├── data_labels.npy    
├── feature_pos.txt       #feature.txt中所有正例
├── feature_p.npy      
├── feature_neg.txt       #feature.txt中所有负例
├── feature_p.npy
├── TrainSet.npy          #训练集
├── TestSet.npy           #测试集
└── 31day_data_features.txt #31天所有数据的n维特征
#结果
├── predict_all_pairs.txt #得到所有预测的userid itemid对
└── filter_pairs.txt      #用train_item过滤的userid itemid对

```

## 使用

TrainModel类用来生成每个样本的特征和对应的label
```
    model = TrainModel()
    model.DivideByTime("2014-12-18 00:00:00") #按时间点分割
    model.MergeData()           #将特征组合起来
    model.SimplifyTrainUser()   #按规则滤除一部分特征
    model.MergeFeatures()       #合并特征
    model.GenLabels()           #产生样本对应label
```
PredictEmption类用来生成模型和选取最优阈值
```
    PE = PredictEmption()
    PE.DivideSet()          #把正负样本分开
    PE.GenTrainTestSet()    #生成训练集和测试集
    PE.TestPredict()        #打印模型预测的准确率和召回率
```
GetFeature31day.py用来提取31天的特征样本和进行预测
```
    model = TrainModel()
    model.MergeData()
    model.MergeFeatures()    #合并特征
    model.Transform2Matrix() #把文本转化为便于处理的矩阵
    model.PerformPredict()   #进行预测
    model.FilterByItems()    #用物品进行过滤
    model.RemoveDuplicate()  #去除重复
```

## 原理

题目给了31天的数据，我们选择第30天作为分割点。用前30天的数据提取n维特征(每个[user_id,item_id]对可以提取一行特征)，用第31天的真实数据去标记每行特征。

举个例子：某个[user_id，item_id]对[9909811,266982489]在前30天出现，如果在第31天它也出现了且behavior_type为购买，则标记这一行的label为1，否则为0。

这样形成了很多行的特征数据，我们把数据进行[Logistic Regression训练](http://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)，得到一个二分类的模型，这样模型就训练好了。

接下来就是预测，预测的东西就是上面的label，也即模型的输出。label为1表示我们认为用户会购买。那么模型的输入是什么呢？模型的输入就是31天所有数据的特征。

```
1th~30th————> 31th的label
1th~31th————> 32th的label
```
因为31th的label数据是已知的，所以可以利用它对训练出来的模型进行评估。而32th的label就是输出结果了。

## 建模
模型建立主要采取对特征数据进行Logistic Regression。

现有一组用户在一个月内的移动端数据，我们需要预测他们在后一天购买某件商品的可能性。通过二值分类，我们仅仅能够预测用户是否购买，不同于此的是，现在我们还关心购买的可能性，即：

    f(x) = P(+1|x)

取值范围是区间[0,1]。

在二值分类中，我们通过w*x得到一个score后，通过符号运算sign来预测y是+1或-1。而对于当前问题，如果能够将这个score映射到[0,1]区间，问题似乎就迎刃而解了。而问题的关键就是选择映射函数，逻辑斯蒂回归选择的映射函数是S型的sigmoid函数。

    f(s) = 1 / (1 + exp(-s))

s取值范围是整个实数域,f(x)单调递增。而逻辑斯蒂回归用

	h(x) = 1 / (1 + exp(-wx))

来逼近上面的目标函数。其中,x为要预测的样本,w为训练出的模型向量(w和x的维度相同),h是算得的样本概率。


# 说明
本repo是一个流程和预测的框架，特征工程很多地方还需要改善。
