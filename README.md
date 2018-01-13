# 美食搜索
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


## WEB

### 1. 环境配置
本项目使用了django框架
```
$ pip install django
```
### 2.运行应用
```
$ cd meishiSearch
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
                admin/      #
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



