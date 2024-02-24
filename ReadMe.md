

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

### 前置知识

1. [topology]( https://dev.opencascade.org/sites/default/files/pdf/Topology.pdf)
2. 





### 初识

当我们首次启动RedPanda时, 软件界面时这样的:

![image-20240220233323486](/MarkDownImages/image-20240220233323486.png)

其中中间的两个黑色窗格, 分别是3d视图(上)和2d视图(下);

同时我们看到有褐色和白色小背景位于黑色窗格左下角, 这是一个待修复bug(TODO:), 会在linux环境下运行时出现, 变动黑色窗格内容(包括大小), 就可以刷新, 恢复正常.

接下来, 我们来创建一个项目.



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

#### 菜单

1. 开始

   1. New

      1. xml 

         创建一个新的Document

   2. open

      1. open rp xml

         打开一个保存的 Document文件.

      2. open pickle shape 

         打开 保存的shape.

      3. save pickle shape

         保存选中的3d图形, 会失去参数信息.

   3. save

      保存当前Document文件为xml.

2. operator

   切换2d视图, 访问.

   1. viewer

      观察者视图.

   2. line [未完成]

      简单画线段操作, 可以根据[2d视图] 的选中功能, 选择点线面上的点, 绘制直线.

      选中 + shift键 画平行于坐标轴的线.

3. 建模

   参考具体源码具体实现.

   ```python
   # 建模box
   self.RegisterShapeDriver('PrimAPI', 'Box', BoxDriver()) 
   self.RegisterShapeDriver('PrimAPI', 'Cone', ConeDriver())
   
   # topology Cut
   self.RegisterShapeDriver('AlgoAPI', 'Cut', CutDriver())
   # topology Fuse
   self.RegisterShapeDriver('AlgoAPI', 'Fuse', FuseDriver())
   
   # bezier曲线
   self.RegisterShapeDriver('GeomAPI', 'bezier', BezierDriver())
   # 建模 圆筒表面
   self.RegisterShapeDriver('GeomAPI', 'Cyl', CylSurDriver())
   # 椭圆2d
   self.RegisterShapeDriver('GeomAPI', 'Ellipse2d', Ellipse2dDriver())
   self.RegisterShapeDriver('Geom2dAPI', 'Ellipse', Elps2dDriver())
   # 绘制2d线段
   self.RegisterShapeDriver('Geom2dAPI', 'Seg2d', Segment2dDriver())
   # 绘制圆弧
   self.RegisterShapeDriver('Geom2dAPI', 'ArcCirc2d', ArcCircleDriver())
   # 2d curve 裁剪
   self.RegisterShapeDriver('Geom2dAPI', 'Trimmed', TrimmedCurveDriver())
   # 参考topology
   self.RegisterShapeDriver('Topo', 'Wire', WireDriver())
   self.RegisterShapeDriver('Topo', 'Mirror', MirrorDriver())
   self.RegisterShapeDriver('Topo', 'Face', FaceDriver())
   # curve/suface 沿着一个方向扫描
   self.RegisterShapeDriver('Topo', 'Prism', PrismDriver())
   # 2d edge to 3d edge
   self.RegisterShapeDriver('Topo', 'Build3d', Build3dDriver())
   # 图形位置偏移
   self.RegisterShapeDriver('Topo', 'Transform', TransShapeDriver())
   # 图形组合
   self.RegisterShapeDriver('Topo', 'Compu', CompoudDriver())
   self.RegisterShapeDriver('Topo', 'NurbConvert', NurbsConvtDriver())
   # 倒圆角
   self.RegisterShapeDriver('Fillet', 'FilletAll', FilletAllDriver())
   #
   self.RegisterShapeDriver('Offset', 'Thick', ThickSoldDriver())
   # 删去一个表面
   self.RegisterShapeDriver('Offset', 'ThruSec', ThruSecDriver())
   # curve/suface 沿着 curve 扫描
   self.RegisterShapeDriver('Offset', 'Pipe', PipeDriver())
   
   ```



#### document 窗格

![image-20240224234949621](/MarkDownImages/image-20240224234949621.png)



**功能:**

1. 显示当前创建的所有图形.
2. 方框选中, 可以在2d图形中显示.
3. 



#### 视图

2d, 3d视图.

![image-20240224235409268](/MarkDownImages/image-20240224235409268.png)



##### 3d视图

基于occt的viewer, 会有一些自带的功能, 没有详细探究. 以下是主要用到的功能.

1. 按键F - 使图形居中.
2. 按键G - 切换topology选中模式.
3.  基本的视图操作, 以选中点为中心, 进行平移, 旋转, 放大缩小.
4. 选中 topology 图形.
5. 右键打开选项菜单.

##### 2d视图

	1. 基本的2d视图操作, 以选中点为中心, 进行平移, 放大缩小.
	2. 按键G - 切换topology选中模式.
	3. 选中平面点.



#### 参数表格

填写建模参数:

![image-20240225000955644](/MarkDownImages/image-20240225000955644.png)

一共两种参数 data 类型:  数值 和 shape 标签:

1. 数值就是简单的建模参数.

2. shape标签, 填写的是 [Document]中, 显示的节点标签.

   当填写正确的节点标签参数, 就会显示此节点表示的参数.



#### 可视化信息

显示2d, 3d视图中显示的 点信息.

![image-20240225001434721](/MarkDownImages/image-20240225001434721.png)





# 开发

待完善.



> 代码的整体架构基于MVC模式，并分为三个主要部分：[Document 数据结构]、[UI 显示]和[控制逻辑]。
>
> 在这一架构中，[Document 数据结构]和[UI 显示]部分吸纳了微服务架构的特点，它们各自提供处理接口和多种信息交换的功能。这些服务模块间的通信采用Qt的信号与槽机制。另一方面，[控制逻辑]部分负责启动服务、建立信号与槽的连接，并处理部分数据转换工作。



> 项目中 RPAF文件夹 为[Document 数据结构]的设计, 和参数建模功能设计. 
>
> pythonocc 的swig封装, 无法很好的处理c++的引用参数, 且occt的application framework 也不完善, 所以, 或许需要自己设计xml的读取显示和保存.
>
> 参考例如 BoxDriver的实现, 可以快速实现一个对occt建模函数的可视化封装.



#### 项目文件说明

![image-20240225003517411](/MarkDownImages/image-20240225003517411.png)

1. config - 全局配置
2. doc - 设计文档说明
3. MarkDownImages - ReadMe.md 中图片的保存文件夹
4. RedPanda - 实际代码文件.
   1. Core  - 对于pythonocc 的封装, occt包含可视化显示, 模型数据结构与操作.
   2. RPAF - [Document]的数据存储形式实现.
   3. utils - 使用函数.
   4. widgets - ui的logic部分, 与ui设计部分.
   5. main.py 启动类.
5. tests - 一些函数测试.
6. main.py 启动函数.





#### 缺陷

基本上只能是个demo.

1. 模块功能不清晰.
2. 模块功能的稳定性.
3. 功能的不完整: 2d绘图功能, 对接step等常用3d图形数据形式, 装配功能.



#### 可能有用参考资料

1. 2d视图的设计: https://librecad.org/





#### 戒律

1. DisplayShape(selector.activate) 似乎无法解析curve parameter (nan, nan)
2. Geom_Surface.bounds 可能为(infinite, infinite, infinite, infinite), `BRepBuilderAPI_NurbsConvert`可以解决问题





# 参考

文档书写: 参考 https://www.cnblogs.com/wingsummer/p/16709970.html