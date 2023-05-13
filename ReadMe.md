
####  要求


运行工具: miniconda

在当前文件夹下:

从 YAML 文件 创建运行环境:

```shell
conda env create -f environment.yml [-n envname]

```

#### 运行

当前文件夹下:

```sh
conda activate envname
python main.py
```



#### 使用说明

1. 新建文件

   click 开始 -> New -> xml

2. 新建Shape

   click 建模选单

3. 查看DataShape

   doubleclick  document 框的树形节点








#### github 地址

https://github.com/nochat1205/RedPanda


#### 戒律

1. myExecute 务必对参数进行检查, 防止会执行生成 0零向量curve等可能不被兼容的元素, 

AIS_Shape似乎无法解析零向量curve,从而导致程序甚至, 电脑宕机.


