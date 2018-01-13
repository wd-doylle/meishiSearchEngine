# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import re
import urlparse
import os
import urllib
import sys
from threading import Thread
import threading
from Queue import Queue
import time
import codecs
import sys

crawlc=1
crawled = []
q=Queue()
mem=[]
max_page=0
varlock=threading.Lock()

def readQueue(q,work,seed):
    if work=='working_mstx_material':
        dataname='materiallist.txt'
    elif work=="working_msj":
        dataname='msj.txt'
    else:
        dataname=work+"_sdata.txt"
    try:
        f=codecs.open(dataname,'r','utf-8')
    except Exception, e:
        print str(e)
        print "new"
        #
        if work!='working_mstx_material' and  work!="working_msj":
            for i in range(seed):
                q.put(i)
        return False
    res=f.read()
    res=res.split()
    for i in res:
            q.put(i)
    f.close()
    return True

def saveQueue(mem,work):
        dataname=work+"_sdata.txt"
        s=' '.join(mem)
        f=codecs.open(dataname,'w','utf-8')
        f.write(s)
        f.close()

def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

def get_page(page):
    try:
        content = urllib2.urlopen(page, data=None, timeout=5).read()
    except Exception, e:
        print "error: "+str(e)
        return None
    return content

def is_inDomain(page, dom):
    p=re.compile(dom)
    res=re.search(p,page)
    if(res !=None):
        return True
    else:
        return False

def is_404(page):
    p=re.compile("404")
    res=re.search(p,page)
    if(res!=None):
        return True
    else:
        return False

def get_title(content):
    soup=BeautifulSoup(content,'lxml')
    title=soup.find('title')
    if title!=None:
        return title.string
    return 'none'

def get_all_links(content, page):
    links = []
    soup=BeautifulSoup(content,'lxml')
    p=re.compile('^/')
    for l in soup.findAll('a',{'href' : re.compile('^http|^/')}):
        #print l.get('href')
        t = p.match(l.get('href'))
        if(t!=None):        
            links.append(urlparse.urljoin(page,l.get('href')))
        else:
            links.append(l.get('href'))
    return links
        
def union_dfs(a,b):
    for e in b:
        if e not in a:
            a.append(e)
            
def union_bfs(a,b):
    for e in b:
        if e not in a:
            a.insert(0,e)


def get_content_mstx(content):
    soup=BeautifulSoup(content,'lxml')
    recipe_title=soup.find('input',{'id':"recipe_title"}).get('value')
    img_t=soup.find('a',{'class':'J_photo'})
    img_url=img_t.contents[1].get('src')
    recipe_t=soup.find('div',{'id':'block_txt1'})
    recipe_content=''
    if recipe_t!=None:
        recipe_content=recipe_t.contents[1]
    recipe_ingredient=[]
    ing_t=soup.find('div',{'class':"recipeCategory_sub_R clear"})
    #print ing_t.contents[1]
    for li in ing_t.contents[1].contents:
        try:
            t=li.contents[1].contents[1].contents[0].string
            #print t
            recipe_ingredient.append(t)    
        except:
            pass
    tag_t=soup.find('div',{'class':"recipeCategory_sub_R mt30 clear"})
    flavor=''
    tech=''
    tag_other=[]
    for li in tag_t.contents[1].contents:
        try:
            t= li.contents[3].string
            if t=='口味'.decode('utf-8'):
                    #print li.contents[1].contents[1].contents[0]
                    flavor=li.contents[1].contents[1].contents[0].string
            elif t=='工艺'.decode('utf-8'):
                    #print li.contents[1].contents[1].contents[0]
                    tech=li.contents[1].contents[1].contents[0].string
            else:
                    tag_other.append(li.contents[1].contents[1].contents[0].string)
        except:
            pass
    print '|'.join([recipe_title,img_url,','.join(recipe_ingredient),flavor,tech,','.join(tag_other),recipe_content])
    return '|'.join([recipe_title,img_url,','.join(recipe_ingredient),flavor,tech,','.join(tag_other),recipe_content])


def get_content_zhms(content):
    soup=BeautifulSoup(content,'lxml')
    recipe_title=soup.find('h1').string
    img_t=soup.find('div',{'class':"cai-baike mt10"})
    img_url=img_t.contents[0].get('src')
    recipe_content=''
    h2t=soup.find('h2')
    soupRC=BeautifulSoup(str(h2t),'lxml')
    recipe_content=''.join(soupRC.findAll(text=True))
    recipe_ingredient=[]
    recipe_t=soup.find('div',{'class':"yuan-cailiao mt40"})
    for dd in recipe_t.contents[0].contents:
        try:
            recipe_ingredient.append(dd.contents[0].contents[0].get('alt'))
        except Exception,e:
            pass
    for dd in recipe_t.contents[1].contents:
        try:
            recipe_ingredient.append(dd.contents[0].contents[0].get('alt'))
        except Exception,e:
            pass
    flavor=''
    tech=''
    tag_other=[]
    tag_t=soup.find('ul',{'class':"bk-other clearfix"})
    for tag in tag_t.contents:
        try:
            txt=tag.contents[0].string
            soupt=BeautifulSoup(str(tag),'lxml')
            tlist=[]
            for item in soupt.findAll('span'):
                    tlist.append(item.string)
            ttext=','.join(tlist)
            if txt=='口味'.decode('utf-8'):
                flavor=ttext
            elif  txt=='工艺'.decode('utf-8'):
                tech=ttext
            else:
                tag_other.append(ttext)
        except:
            pass
    print '|'.join([recipe_title,img_url,','.join(recipe_ingredient),flavor,tech,','.join(tag_other),recipe_content])
    return '|'.join([recipe_title,img_url,','.join(recipe_ingredient),flavor,tech,','.join(tag_other),recipe_content])

def get_content_msj(content):
    soup=BeautifulSoup(content,'lxml')
    recipe_title=soup.find('a',{'id':"tongji_title"}).string
    img_t=soup.find('div',{'class':"cp_headerimg_w"})
    img_url=img_t.contents[0].get('src')
    plist=soup.findAll('p')
    soupP=BeautifulSoup(str(plist[1]),'lxml')
    recipe_content=' '.join(soupP.findAll(text=True))
    recipe_ingredient=[]
    soupI=BeautifulSoup(str(soup.find('div',{'class':"materials_box"})),'lxml')
    for h4 in soupI.findAll('h4'):
        recipe_ingredient.append(h4.contents[0].string )
    flavor=''
    tech=''
    tag_other=[]
    for gx in soup.findAll('a',{'id':re.compile("tongji_gx")}):
        tag_other.append(gx.string)
    tech=soup.find('a',{'id':"tongji_gy"}).string
    flavor=soup.find('a',{'id':"tongji_kw"}).string
    print '|'.join([recipe_title,img_url,','.join(recipe_ingredient),flavor,tech,','.join(tag_other),recipe_content])
    return '|'.join([recipe_title,img_url,','.join(recipe_ingredient),flavor,tech,','.join(tag_other),recipe_content])

def get_content_material_mstx(content):
    soup=BeautifulSoup(content,'lxml')
    title=soup.findAll('h1')[1].contents[0].string
    yiji_e=soup.find('h3',{'class':"yi"})
    if yiji_e is None:
        return ''
    yiji_g=soup.findAll('div',{'class':"yiji clear mt20"})[0]
    glist=[]
    g_t=BeautifulSoup(str(yiji_g),'lxml').find('ul')
    gli=BeautifulSoup(str(g_t),'lxml').findAll('li')
    for li in gli:
        mat = li.contents[1].contents[1].string
        reason = li.contents[3].string
        glist.append(mat+':'+reason)

    blist=[]
    try:
        yiji_b=soup.findAll('div',{'class':"yiji clear mt20"})[1]
        b_t=BeautifulSoup(str(yiji_b),'lxml').find('ul')
        bli=BeautifulSoup(str(b_t),'lxml').findAll('li')
        for li in bli:
            mat = li.contents[1].contents[1].string
            reason = li.contents[3].string
            blist.append(mat+':'+reason)
    except:
        pass
    res=title+'|'+','.join(glist)+'|'+','.join(blist)
    return res
        
    
    
def add_page_to_folder(page, content,folder): #将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index.txt'    #index.txt中每行是'网址 对应的文件名'
    #folder = 'html'                 #存放网页的文件夹
    filename = valid_filename(page) #将网址变成合法的文件名
    title=get_title(content)
    if is_404(title):
            return
    else:
            print title
    index = codecs.open(index_filename, 'a','utf-8')
    index.write(page.encode('ascii', 'ignore') + '\t' + filename + '\t' + title + '\n' )
    index.close()
    if not os.path.exists(folder):  #如果文件夹不存在则新建
        os.mkdir(folder)
    f = codecs.open(os.path.join(folder, filename), 'w','utf-8')
	##########
    #contents=''.join(soup.findAll(text=True))
    #print content.encode('utf-8')
    try:
        f.write(get_content_material_mstx(content))#+'|'+page)                #将网页存入文件
    except Exception,e:
       print e
    f.close()

class works():
    def working_mstx_material(this):
    
        while True:
            time.sleep(10)
            page=q.get()+"yiji"
            if varlock.acquire():
                if page not in crawled:
                    varlock.release()
                    content = get_page(page)
                    if(content==None):
                        q.task_done()
                        continue
                    add_page_to_folder(page,content,'html/material')

                else:
                    varlock.release()
            else:
                varlock.release() 
            q.task_done()
            
    def working_mstx(this):
        global crawlc,max_page
    
        while True:
            num=int(q.get())
            page='http://home.meishichina.com/recipe-'+str(num)+'.html'
            if varlock.acquire():
                if page not in crawled:
                    varlock.release()
                    try:
                        content = get_page(page)
                    except:
                        mem.append(str(num+50))
                        q.task_done()
                        break
                    if(content==None):
                        crawlc-=1
                        q.task_done()
                        continue
                    add_page_to_folder(page,content,'html/mstx')
                    if crawlc<max_page:
                        crawlc+=1
                        #print type(num)
                        q.put(num+50)#
                    else:
                            mem.append(str(num+50))
                    if varlock.acquire():
                        #print page
                        crawled.append(page)
                        varlock.release()
                else:
                    varlock.release()
                    crawlc-=1
            else:
                varlock.release() 
            q.task_done()
            time.sleep(20)

    def working_zhms(this):
        global crawlc,max_page
    
        while True:
            time.sleep(5.5)
            num=int(q.get())
            page='http://www.zhms.cn/cp/'+str(num)+'/'
            if varlock.acquire():
                if page not in crawled:
                    varlock.release()
                    content = get_page(page)
                    if(content==None):
                        crawlc-=1
                        q.put(num+1)#
                        q.task_done()
                        continue
                    add_page_to_folder(page,content,'html/zhms')
                    if crawlc<max_page:
                        crawlc+=1
                        q.put(num+1)#
                    else:
                            mem.append(str(num+10))
                    if varlock.acquire():
                        #print page
                        crawled.append(page)
                        varlock.release()
                else:
                    varlock.release()
                    crawlc-=1
            else:
                varlock.release() 
            q.task_done()

    def working_msj(this):
        global crawlc,max_page
        while True:
            page=q.get()
            if varlock.acquire():
                if page not in crawled:
                    varlock.release()
                    content = get_page(page)
                    if(content==None):
                        crawlc-=1
                        q.task_done()
                        continue
                    add_page_to_folder(page,content,'html/msj')
                    if crawlc<max_page:
                        crawlc+=1
                    else:
                        break
                else:
                    varlock.release()
            else:
                varlock.release()
            q.task_done()
            time.sleep(20)
    #def working_mstx(this):
     #       this.working()
def crawl(seed, max_page,work):
    w=works()
    readQueue(q,work,seed)    

    for i in range(seed):
        t=Thread(target=getattr(w,work))
        t.setDaemon(True)
        t.start()
        time.sleep(0.55)

    q.join()
    saveQueue(mem,work)

def  getmaterial():
        content=get_page('http://www.meishichina.com/yuanliao-search/')
        f = codecs.open("materiallist.txt", 'w','utf-8')
        soup=BeautifulSoup(content,'lxml')
        linklist=[]
        for l in soup.findAll('a',{'href' : re.compile('^http://www.meishichina.com/YuanLiao/[A-Z]')}):
            linklist.append(l.get('href'))
        for l in linklist:
            f.write(l+'\n')
        f.close()
        
def msj_pre():
    f = codecs.open("html/msj.txt", 'r','utf-8')
    fr = codecs.open("html/msjLink.txt", 'w','utf-8')
    r=f.read()
    print r
    soup=BeautifulSoup(r,'lxml')
    linklist=[]
    for l in soup.findAll('a',{'href':re.compile('http://www.meishij.net')}):
	    linklist.append(l.get('href'))
    for l in linklist:
        fr.write(l+'\n')
    f.close()
    fr.close()

    p=0
    for l in linklist:
        p+=1
        rlist=[]
        for i in range(1,57):
            try:
                content = urllib2.urlopen(l+'?/&page={0}'.format(i), data=None, timeout=5).read()
                soup=BeautifulSoup(content,'lxml')
                for t in soup.findAll('a',{'class':re.compile('big')}):
                    rlist.append(t.get('href'))
            except:
                print "error: "+str(e)
        f=codecs.open("msj_{0}.txt".format(str(p)), 'w','utf-8')
        for rl in rlist:
            f.write(rl+'\n')
        f.close()

def msj_temp():
    f=codecs.open("html/msj_all.txt", 'w','utf-8')
    for i in range(1,40):
        fr=codecs.open("html/msj_{0}.txt".format(i), 'r','utf-8')
        f.write(fr.read())
        fr.close()
    f.close()

def  msj_sc():
    c=544
    f=codecs.open("html/msjsclink.txt", 'w','utf-8')
    for i in range(35,63):
            content= urllib2.urlopen('http://www.meishij.net/shicai/?page={0}'.format(i),data=None, timeout=5).read()
            soup=BeautifulSoup(content,'lxml')
            soup_t=BeautifulSoup(str(soup.find('div',{'class':"listtyle1_list clearfix"})),'lxml')
            for h in soup_t.findAll('h3'):
                c+=1
                time.sleep(3)
                title=h.contents[0].string
                scUrl=h.contents[0].get('href')
                print title
                #print scUrl.encode('utf-8')
                scContent=urllib2.urlopen(scUrl.encode('utf-8'),data=None,timeout=5).read()
                scSoup=BeautifulSoup(scContent,'lxml')
                #print scContent
                para=scSoup.find('p',{'class':'p2'})
                res=  ''.join(para.findAll(text=True))
                f=codecs.open("html/msjsc/"+str(c)+'.txt','w','utf-8')
                f.write(title+'|'+res)
                f.close()
            time.sleep(60)
        
if __name__ == '__main__':
    '''
    seed = sys.argv[1]
    method = sys.argv[2]
    max_page = sys.argv[3]
    crawl(seed, max_page)
    '''
    print 0 
    seed=10
    max_page=50000
    msj_sc()
    #crawl(seed,max_page,'working_mstx_material')
    
