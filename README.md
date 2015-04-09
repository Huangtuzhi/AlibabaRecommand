# AlibabaRecommand
 Alibaba 2015 mobile recommending algorithm competition.
 
## [比赛介绍](http://tianchi.aliyun.com/competition/introduction.htm?spm=5176.100066.333.2.YI657c&raceId=1)
通过对用户在移动终端上一个月的行为数据进行分析，为后一天的用户购买行为作出预测，进行推荐。

##目录结构

```
├── LICENSE         	    #许可证
└── README.md       	    #使用说明
#建表
├── create_table.sql     #创建基本表
├── add_table.sql 		     #后续增加的表
├── add_index.sql        #为表建立索引
├── add_table_31day.sql  #建立存储31天数据的表，结构同上
└── add_index_31day.sql  #为表建立索引
#数据导入
├── datatoDB.sql      	  #大赛csv格式原始数据导入基本表
└── FeaturetoDB.sql   	  #feature.txt导入对应表
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
└── TestSet.npy           #测试集

```

##原理

##结果
