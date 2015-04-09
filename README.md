# AlibabaRecommand
 Alibaba 2015 mobile recommending algorithm competition.
 
## [比赛介绍](http://tianchi.aliyun.com/competition/introduction.htm?spm=5176.100066.333.2.YI657c&raceId=1)
通过对用户在移动终端上一个月的行为数据进行分析，为后一天的用户购买行为作出预测，进行推荐。

##目录结构

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
├── datatoDB.sql          #大赛csv格式原始数据导入基本表
└── FeaturetoDB.sql       #feature.txt导入对应表
#main
├── __init__.py
├── TrainModel.py
├── ObtainPredict.py
├── GetFeature31day.py
└── x.py
#数据 
├── feature.txt           #符合某个标准的记录(user_id,item_id,look,store,cart，buy）
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

```

##原理
题目给了31天的数据，我们选择第30天作为分割点。用前30天的数据提取n维特征(每个[user_id,item_id]对可以提取一行特征)，用第31天的真实数据去标记每行特征。

举个例子：某个[user_id，item_id]对[9909811,266982489]在前30天出现，如果在第31天它也出现了且behavior_type为购买，则标记这一行的label为1，否则为0。

这样形成了很多行的特征数据，我们把数据进行[Logistic Regression训练](http://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)，得到一个二分类的模型，这样模型就训练好了。

接下来就是预测，预测的东西就是上面的label，也即模型的输出。label为1表示我们认为用户会购买。那么模型的输入是什么呢？模型的输入就是31天所有数据的特征。

```
1th~29th————> 30th的label
1th~30th————> 31th的label
```
因为30th的label数据是已知的，所以可以利用它对训练出来的模型进行评估。而31th的label就是输出结果了。