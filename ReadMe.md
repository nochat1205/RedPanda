

# 简述

一个可视化辅助参数建模工具.

#### Result

![image-20230521164113042](/MarkDownImages/image-20230521164113042.png)



演示:

https://drive.google.com/file/d/16SpPVt0-Xr_SG2oYCXywITaS-xPO3c2s/view?usp=drive_link

https://drive.google.com/file/d/1NdWNz9CCszv3WoN-6FU98RUhnI9svzpe/view?usp=drive_link



#  环境搭建

###### 1. 使用miniconda(存在版本冲突) 

运行工具: miniconda

在当前文件夹下:

从 YAML 文件 创建运行环境:

```shell
conda env create -f environment.yml [-n envname]

```



**运行:**

当前文件夹下:

```sh
conda activate envname
python main.py
```



###### 2.pip 安装需要的依赖

安装pythonocc: https://github.com/tpaviot/pythonocc-core

安装pyqt:

报错什么, 安装什么.



**运行:** python mian.py



#### github 地址

https://github.com/nochat1205/RedPanda



# 使用

###### 前置知识





### 初识

当我们首次启动RedPanda时, 软件界面时这样的:

![image-20240220233323486](\MarkDownImages\image-20240220233323486.png)

其中中间的两个黑色窗格, 分别是3d视图(上)和2d视图(下);

同时我们看到有褐色和白色小背景位于黑色窗格左下角, 这是一个待修复bug(TODO:), 会在linux环境下运行时出现, 变动黑色窗格内容(包括大小), 就可以刷新, 恢复正常.

接下来, 我们来创建一个项目.

###### 创建项目.

点击 [**开始**], 选择 [new], [xml], 创建一个基于xml的项目文件:

![创建](/MarkDownImages/创建.png)

项目创建好如下所示, 存在一个UnSaved根节点:

![image-20240220235657183](/MarkDownImages/image-20240220235657183.png)

添加一个3d box:

![建模](/MarkDownImages/建模.png)

双击选择Document 中的 box 节点:

![image-20240221230031120](/MarkDownImages/image-20240221230031120.png)

输入建模参数, 创建相应的 3d box:
![image-20240221232641406](\MarkDownImages/image-20240221232641406.png)

选中3d视图, 按f使得图形居中, 鼠标在3d视图中, 鼠标左键选中, 以选中点为中心, 可以:

1.移动鼠标进行旋转, 

2.鼠标滚轮进行放大缩小.

3.按住中键进行移动.

![operator](/MarkDownImages/operator.gif)

使用[G键], 切换选中模式, 使用左键选中体, 面, 框, 边, 点, 右键唤出选单, 可以引用选中的图形:

![ref_sub](/MarkDownImages/ref_sub.gif)

创建一个椭圆:

![image-20240222211120691](/MarkDownImages/image-20240222211120691.png)

[参数选框]里, 节点如果有相同的子节点, 然后可以进行参数复制粘贴:

![参数](/MarkDownImages/参数-1708607887358.gif)

绘制直线:

![line](/MarkDownImages/line.gif)

保存文件:

![save](/MarkDownImages/save.png)

读取文件, 开始菜单, 选择[open]-[open rp xml] 读取之前保存的xml文件:

![读取](/MarkDownImages/读取.png)

其他操作, 参考:

[ 演示 ](#Result)



### 窗体





#### 戒律

1. DisplayShape(selector.activate) 似乎无法解析curve parameter (nan, nan)
2. Geom_Surface.bounds 可能为(infinite, infinite, infinite, infinite), `BRepBuilderAPI_NurbsConvert`可以解决问题

