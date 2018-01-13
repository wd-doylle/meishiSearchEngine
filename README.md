# 美食搜索
完整报告：https://zybuluo.com/wdUnicorn/note/1017849

![](https://raw.githubusercontent.com/wd-doylle/storage/master/homePage.png)

---

## 功能特征



### 1. 文字搜索

支持的关键词：
> * 菜名 
> * 做法   
> * 口味 
> * 食材

### 2. 食材小知识

根据搜索内容的推荐

![](https://raw.githubusercontent.com/wd-doylle/storage/master/search.png)

### 3. 图片搜索
支持的搜索方式：
> * 本地上传图片
> * 图片URL

![](https://raw.githubusercontent.com/wd-doylle/storage/master/imgSearch.png)

### 4. 高级搜索 
命令语法：
```
<keyword>|f$<flavor>|!f$<not-flavor>|in$<ingredient>|!in$<not-ingredient>|t$<technique>|!t$<not-technique>
```
用户可以直接输入搜索命令，也可通过`s/bl/`指定高级搜索

![](https://raw.githubusercontent.com/wd-doylle/storage/master/booleanSearch.png)

---

## 小组分工
网页爬虫：韩宇杰

索引创建与搜索：陈鸿滨

图像搜索：柴峥豪

WEB：王多

---

## 网页爬虫


### 1. 目标选择
根据搜索引擎需求，对相关美食、菜谱网站进行人工分辨筛选，确定内容质量较高，种类齐全，数量丰富的网站作为爬取目标。确定采用的网站为以下三个：
> * 美食天下 [http://www.meishichina.com/](http://www.meishichina.com/)
> * 美食杰 [http://www.meishij.net/](http://www.meishij.net/)
> * 中华美食网 [http://www.zhms.cn/](http://www.zhms.cn/)

### 2. 内容获取
对于美食菜谱，最终获得的数据按菜名分条，每条记录中除包含正文、图片、网址外，还应有分类标签。目标网站中已有类似结构，因此大部分内容可直接从条目所在网页中提取。为完善获取数据，提高效率，采取了分级爬取的方案：
> #### 1. 爬取网站索引页面，获得具体条目地址及所属的分类信息。
> #### 2. 根据步骤1所得地址爬取具体条目页面，获得主要内容。此处对于体积较大的图片 只记录其url，不下载
> #### 3. 下载步骤2所得图片url指向的图片，供图片搜索模块使用

分级爬取利用了专门性网站内部条理清晰、逻辑性强的特点，爬取过程不再是全网爬虫的随机行为，减少了无用、重复信息量；各步骤之间分工模块化，易于分布式处理，在本次小组规模的实践过程中使仅4台计算机的资源得到了充分利用。

### 3. 其他问题
 * 关于数据更新：
各网站内条目均有发布时间，以此为依据可以判断是否有新数据，在爬取索引页面时更新条目表。各网站数据相互独立，便于添加新网站内容。
 * 关于网站反爬虫机制：
根据礼貌性原则不做过多破解尝试，爬虫程序中加入了异常检测，检测到爬取网页异常时暂停爬取一段时间，或保存当前状态并中止，再次运行时可从中止时状态继续运行。有需要时也可将状态记录转移至其他机体继续运行。

---

## 索引创建与搜索

### 环境配置与工具说明

环境：

> python-2.7      Pylucene- 4.9.0 

分词工具：

> jieba分词（使用了两个版本的jieba）：
>
> 一个是自带的（课程提供，重命名为my_jieba）
>
> 二是使用pip install jieba 安装的官方的最新版本

### 索引的创建

标签对应：

> 菜名：name
>
> 原料：ingredient
>
> 口味：taste
>
> 工艺：tech
>
> 其他标签：others
>
> 正文：content
>
> 图片地址：img
>
> 网页地址：url

#### 关于分词

###### Analyzer

使用SimpleAanlyzer

###### 分词对象

菜名，原料，其他标签以及正文（描述）

###### 分词工具使用

使用可对中文进行分词的jieba分词，其中，my_jieba 主要用于去除菜名中的无关的标点符号；jieba用于分词，主要使用jieba.cut()和jieba.cut_for_search()两种模式进行分词，菜名和正文用于搜索的索引使用cut_for_search 模式分词

###### 用户自定义词典

考虑到构建的是美食搜索引擎，为增加对菜名、食材名称的分词准确率，特使用jieba的用户自定义词典功能（jieba.load_userdict(dic_name)）

词典来源为搜狗拼音官网上一个名为“饮食大全”的词库（词量大小为1w+），下载下scel文件后，用python代码将其转换为符合jieba词典格式的txt文件

#### 索引创建

所有内容都存储，除了网页url和图片地址外的内容都加入索引

值得注意的有以下两点：

> 1. 正文参与索引时，将其field的权值使用setBoost调成0.1，即参与评分时处次要地位
> 2. 为在搜索结果中添加关键词高亮，建立索引时，另外添加菜名和正文的使用jieba.cut()模式分词的索引
> 3. 另外添加一个菜名不分词的索引

### 关于搜索

#### 模糊搜索（低级搜索）

根据用户的一个或多个关键词（句）直接搜索，对搜索命令使用jieba全模式分词，使用SimpleAnalyzer，对所有的field进行搜索，结果取并集，值得注意的有：

> 1. 将标签为口味和工艺的query的权值调为0.1
> 2. 考虑用户的搜索意图，若用户输入的是一个完整的常见的菜名（如宫保鸡丁），则放回不分词的搜索结果
> 3. 使用highlighter添加关键词高亮
> 4. 设置阈值，丢弃score太低的搜索结果

#### 高级搜索

通过一定语法指定某些标签下的关键词一定出现或一定不出现的条件下搜索菜名，使用布尔搜索

> 1. 将一定出现某关键词的query的权值设为0.1，此举是为了增加菜名的重要性，使搜索结果能更按照菜名的相关性排序
> 2. 使用highlighter添加关键词高亮
> 3. 设置阈值，丢弃score太低的搜索结果

#### 搜索结果的排序

各个网址的点击量将被记录下来，两种搜索模式的搜索结果的前20条，在相关性接近（如score相差不超过0.1）时，将点击量的网址排在前面

#### 根据搜索命令和结果推出食材小知识

若用户的搜索命令里包含某食材名（知识库已有的）或前十条搜索结果中某食材名（知识库已有的）出现次数超过5次，则推出该食材的相关小知识，如别名、相克相宜、适宜人群、禁忌人群等

食材小知识来源于美食杰网站的食材相关网页

---

## 图像检索


### 1. 基于SIFT描述子的词袋模型

搜索引擎主要使用基于SIFT描述子的词袋(Bag of Words)模型对图像进行检索。考虑到SIFT描述子的匹配计算量庞大，而通过词袋模型得以将对N*128维的SIFT描述子的匹配转为k维词频向量的匹配。
将N*128维的SIFT描述子转为词频向量的流程如下：
![img1](http://ww4.sinaimg.cn/large/0060lm7Tly1fnf54iacfmj30v50n9gnf.jpg)

1. 假设图像集有n幅图像，对图像集进行预处理。包括图像增强，分割，图像统一格式，统一规格等等。
2. 提取SIFT特征。对每一幅图像提取SIFT特征（每一幅图像提取多少个SIFT特征不定）。每一个SIFT特征用一个128维的描述子矢量表示。
3. 用K-means对2中提取的SIFT描述子进行聚类，K-mean算法将大于K个对象分为K个簇以使簇内具有较高的相似度，而簇间相似度较低。聚类中心有K个（在词袋模型中聚类中心被定义为视觉词），则词频矢量的长度也为K。
4. 计算词频。计算每一幅图像的每一个SIFT描述子到这K个视觉词的距离，并将其映射到距离最近的视觉词中（即将该视觉词的对应词频+1）。完成这一步后，每一幅图像就变成了一个与视觉词序列相对应的K位词频矢量。
5. 由于每张图像的SIFT描述子数量不定，因此需要对得到的词频数量进行归一化，从而得到最终结果。

![img2](http://ww2.sinaimg.cn/large/0060lm7Tly1fnf54huauxj30t00apjs7.jpg)

得到了图像集的词频矢量集以及K聚类后，即可对目标图像进行检索，流程如下：
![img3](http://ww4.sinaimg.cn/large/0060lm7Tly1fnf54i2imkj30sh0e7dgt.jpg)
	1. 得到了图像集的词频矢量集以及K个聚类中心。
	2. 输入目标图片，进行SIFT计算。
	3. 依照由数据集得到的K个聚类对目标图片的SIFT描述子计算词频矢量并进行归一化。
	4. 分别计算该词频矢量与数据集中词频矢量的欧式距离，将其按欧氏距离有小到大排序，返回检索结果。
	
使用基于SIFT描述子的词袋模型，能够检索经过旋转、裁剪、色差变换的图片，准确度较高，同时速度较快，检索35000条数据集平均用时为0.1秒。

通过检索经过旋转、裁剪、色差变换的蛋糕图片：

![img4](http://ww1.sinaimg.cn/large/0060lm7Tly1fnf5g4yix6j3063063wff.jpg)

测试结果如下：
![img5](http://ww4.sinaimg.cn/large/0060lm7Tly1fnf54jqcl9j31fj0tc12s.jpg)


### 2. 基于VGG16的预训练模型

考虑到基于SIFT描述子的词袋模型，对相似图像的检索有所欠缺，于是同时使用了VGG16的预训练模型对图像集进行特征提取，取得了较好的效果。
对鱼香肉丝图片：

![img6](http://ww1.sinaimg.cn/large/0060lm7Tly1fnf54htvrtj307i07iwf3.jpg)

依据VGG16模型提取得到特征进行检索，得到结果如下：
![img7](http://ww4.sinaimg.cn/large/0060lm7Tly1fnf54jog8jj30iw0fjgr2.jpg)

![img8](http://ww4.sinaimg.cn/large/0060lm7Tly1fnf54jv3x5j30fn0fxq9i.jpg)

### 3. 个性化选择

通过基于SIFT描述子的词袋模型，能够检索经过旋转、裁剪、色差变换的图片，速度较快；通过VGG16模型提取得到特征进行检索，对相似图像检索取得了较好的效果，而速度较慢，进行一次检索平均用时1.5秒，用户可以根据自己的需要进行自主的选择。

---

## WEB

### 1. 环境配置
本项目使用了django框架
```
$ pip install django
```
### 2.运行应用
```
$ cd meishiSearchEngine
$ python manage.py runserver <port>
```
### 3.应用布局
根目录 **meishiSearchEngine**
```
meishiSearchEngine/
    meishi/
    Search/
    imgSearch/
    src/
    templates/
    manage.py
```
### 4.网站布局

```
http://<host>:<port>/
                admin/      #管理
                /           #主页
                s/          #文字搜索
                s/bl/       #高级搜索
                im/         #图片搜索
                    im/s/   
                wp_rd/      #壁纸轮换
                cc/         #记录点击
                static/     #静态文件
                    img/
                    js/
                    css/
                    wp/
```
### 5. 特征
> * 记录点击 
> * 自动补全

#### **记录点击**
生成页面时，将索引得到的原url作为参数传给cc/：
> `http://www.meishij.net/baobaocaipu/baobaonanguahu.html`
->
`/cc/?outlink=http://www.meishij.net/baobaocaipu/baobaonanguahu.html`

在`cc/`内记录点击，写入统计文件：`CLICK_CNT.txt`
在`s/`内读取`CLICK_CNT.txt`，作为排序特征：
```
result, recommand = search(command,click_cnt)
```
#### **自动补全**
**Autocomplete like Google by XDSoftnet**

**github:**

https://github.com/xdan/autocomplete/

**候选词：**

`foodname.txt` `taste_sort.txt` `tech_sort.txt` `food_dic.txt` `ingre_sort.txt` `name_sort.txt`



