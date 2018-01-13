#!/usr/bin/env python
#coding = utf-8
import sys, os, lucene

from java.io import File
from org.apache.lucene.analysis.core import  WhitespaceAnalyzer
from org.apache.lucene.analysis.core import  SimpleAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause

from org.apache.lucene.search.highlight import Highlighter
from org.apache.lucene.search.highlight import QueryScorer
from org.apache.lucene.search.highlight import SimpleHTMLFormatter
from org.apache.lucene.search.highlight import SimpleFragmenter
import jieba
import my_jieba
import time
import swxc

reload(sys)
sys.setdefaultencoding('utf-8')
jieba.load_userdict("foodname.txt")
jieba.load_userdict("food_dic.txt")


def parseCommand(command):
    allowed_opt = {'in':(0,'ingredient'),'f':(0,'taste'),'te':(0,'tech'), 
    '!in':(1,'ingredient'),'!f':(1,'taste'),'!te':(1,'tech')}
    command_dict = [{},{}]
    seg = command.split('|')
    for i in range(1, len(seg)):
        try:
            sign, comm = (seg[i]).split('$')
            if comm and allowed_opt[sign]:
                command_dict[allowed_opt[sign][0]][allowed_opt[sign][1]] = comm
        except:
            pass
    return seg[0], command_dict

def firstsearch(searcher, analyzer,command):
    if len(command.split())>1:
        return []
    querys = BooleanQuery()
    query = QueryParser(Version.LUCENE_CURRENT, "name_not_cut",
                                analyzer).parse(command)
    querys.add(query, BooleanClause.Occur.MUST)
    scoreDocs = searcher.search(querys, 1000).scoreDocs
    return scoreDocs

def run(searcher, analyzer,command, urlclick):

        if command == '':
            return []
        res = firstsearch(searcher, analyzer, command)
        command = ''.join(my_jieba.cut(command))
        command = " ".join(jieba.cut(command, cut_all = True))
        if len(res) > 0:
            scoreDocs = res
        else:
            querys = BooleanQuery()
            for k in tag:
                query = QueryParser(Version.LUCENE_CURRENT, k,
                                    analyzer).parse(command)
                if k =='taste' or k == 'tech':
                    query.setBoost(0.5)
                querys.add(query, BooleanClause.Occur.SHOULD)
            scoreDocs = searcher.search(querys, 10000).scoreDocs

        swxc_res = findres(command, scoreDocs, searcher)
        formatter = SimpleHTMLFormatter("<span style='color:red'>", "</span>")
        formatter_name = SimpleHTMLFormatter("<span,style='color:red'>", "</span>")
        scorer = QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'name',
                                         analyzer).parse(command))
        highlighter1 = Highlighter(formatter_name, scorer)
        highlighter2 = Highlighter(formatter_name, QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'content',
                                         analyzer).parse(command)))
        highlighter3 = Highlighter(formatter, QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'ingredient',
                                         analyzer).parse(command)))
        highlighter4 = Highlighter(formatter, QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'taste',
                                         analyzer).parse(command)))
        highlighter5 = Highlighter(formatter, QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'tech',
                                         analyzer).parse(command)))
        highlighter6 = Highlighter(formatter, QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'others',
                                         analyzer).parse(command)))

        fragmenter = SimpleFragmenter(1000)
        highlighter1.setTextFragmenter(fragmenter)
        highlighter2.setTextFragmenter(fragmenter)
        highlighter3.setTextFragmenter(fragmenter)
        highlighter4.setTextFragmenter(fragmenter)
        highlighter5.setTextFragmenter(fragmenter)
        highlighter6.setTextFragmenter(fragmenter)

        
        results = []
        for scoreDoc in scoreDocs:
            if (len(scoreDocs)>200 and len(scoreDocs) * scoreDoc.score < 2) or scoreDoc.score<0.002:
                continue
            doc = searcher.doc(scoreDoc.doc)

            highlighterContent = highlighter1.getBestFragment(
                analyzer, 'name', doc.get('name'))
            highlighterContent2 = highlighter2.getBestFragment(
                analyzer, 'content', doc.get('content'))   
            highlighterContent3 = highlighter3.getBestFragment(
                analyzer, 'ingredient', doc.get('ingredient'))   
            highlighterContent4 = highlighter4.getBestFragment(
                analyzer, 'taste', doc.get('taste'))   
            highlighterContent5 = highlighter5.getBestFragment(
                analyzer, 'tech', doc.get('tech'))   
            highlighterContent6 = highlighter6.getBestFragment(
                analyzer, 'others', doc.get('others'))   

            if highlighterContent: 
                highlighterContent = highlighterContent.replace(' ','')
                highlighterContent = highlighterContent.replace(',',' ')
            else:
                highlighterContent = doc.get('name').replace(' ','')

            if highlighterContent2:
                highlighterContent2 = highlighterContent2.replace(' ','')
                highlighterContent2 = highlighterContent2.replace(',',' ')
            else:
                highlighterContent2 = doc.get('content').replace(' ','')
            if highlighterContent3:
                highlighterContent3 = highlighterContent3.replace(',','')
            else:
                highlighterContent3 = (doc.get('ingredient')).replace(',','')
            if highlighterContent4:
                pass
            else:
                highlighterContent4 = doc.get('taste')
            if highlighterContent5:
                pass
            else:
                highlighterContent5 = doc.get('tech')
            if highlighterContent6:
                highlighterContent6 = highlighterContent6.replace(',','')
            else:
                highlighterContent6 = (doc.get('others')).replace(',','')

            results.append((highlighterContent, doc.get('img'), highlighterContent2, highlighterContent3, highlighterContent4, highlighterContent5, highlighterContent6, doc.get('url'), scoreDoc.score))

            for i in range(0, min(20,len(results)) - 1):
                flag = True
                for j in range(0, min(20, len(results)) - i -1):
                    if abs(results[j][8] - results[j+1][8]) < 0.1 and urlclick[results[j][7]] < urlclick[results[j+1][7]]:
                        flag = False
                        results[j], results[j+1] = results[j+1], results[j]
                if flag:
                    break

        return results, swxc_res

def vagueSearch(command, urlclick):
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    directory = SimpleFSDirectory(File('index2.3'))
    print "run vague search..."
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)
    results, swxc_res = run(searcher, analyzer,command, urlclick)
    del searcher
    return results, swxc_res


def superSearch(command, command_dict, urlclick):
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    directory = SimpleFSDirectory(File('index2.3'))
    print "run super search..."
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = SimpleAnalyzer(Version.LUCENE_CURRENT)
    command = ' '.join(jieba.cut_for_search(command))
    querys = BooleanQuery()
    if command:
        query = QueryParser(Version.LUCENE_CURRENT, 'nameforsearch', analyzer).parse(command)
        querys.add(query, BooleanClause.Occur.SHOULD)
    for k, v in (command_dict[0]).items():
        query = QueryParser(Version.LUCENE_CURRENT, k, analyzer).parse(v)
        query.setBoost(0.1)
        querys.add(query, BooleanClause.Occur.MUST)
    for k, v in (command_dict[1]).items():
        query = QueryParser(Version.LUCENE_CURRENT, k, analyzer).parse(v)
        querys.add(query, BooleanClause.Occur.MUST_NOT)
    scoreDocs = searcher.search(querys, 10000).scoreDocs
    swxc_res = findres(command + ' ' + command_dict[0].get("ingredient",''), scoreDocs, searcher)
    formatter = SimpleHTMLFormatter("<span style='color:red'>", "</span>")
    formatter_name = SimpleHTMLFormatter("<span,style='color:red'>", "</span>")
    if command:  
        scorer = QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'name',
                                             analyzer).parse(command))
        highlighters = [Highlighter(formatter_name, scorer)]
    else:
        highlighters = ['']
    if command_dict[0].get('ingredient'):
        highlighters.append(Highlighter(formatter, QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'ingredient',
                                             analyzer).parse(command_dict[0]['ingredient']))))
    else:
        highlighters.append('')
    if command_dict[0].get('taste'):
        highlighters.append(Highlighter(formatter, QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'taste',
                                             analyzer).parse(command_dict[0]['taste']))))
    else:
        highlighters.append('')
    if command_dict[0].get('tech'):
        highlighters.append(Highlighter(formatter, QueryScorer(QueryParser(Version.LUCENE_CURRENT, 'tech',
                                             analyzer).parse(command_dict[0]['tech']))))
    else:
        highlighters.append('')
    fragmenter = SimpleFragmenter(1000)
    for h in highlighters:
        if h:
            h.setTextFragmenter(fragmenter)

    results = []
    for scoreDoc in scoreDocs:
        if (scoreDoc.score * len(scoreDocs)<200 and len(scoreDocs)>200) or scoreDoc.score<0.1:
            continue
        doc = searcher.doc(scoreDoc.doc)
        if command:
            highlighterContent = highlighters[0].getBestFragment(
                analyzer, 'name', doc.get('name'))
        else:
            highlighterContent = ''
        if highlighters[1]:
            highlighterContent2 = highlighters[1].getBestFragment(
                analyzer, 'ingredient', doc.get('ingredient'))
        else:
            highlighterContent2 = ''
        if highlighters[2]:
            highlighterContent3 = highlighters[2].getBestFragment(
                analyzer, 'taste', doc.get('taste'))
        else:
            highlighterContent3 = ''
        if highlighters[3]:
            highlighterContent4 = highlighters[3].getBestFragment(
                analyzer, 'tech', doc.get('tech'))
        else:
            highlighterContent4 = ''

        if highlighterContent: 
            highlighterContent = highlighterContent.replace(' ','')
            highlighterContent = highlighterContent.replace(',',' ')
        else:
            highlighterContent = doc.get('name').replace(' ','')
        if highlighterContent2:
            highlighterContent2 = highlighterContent2.replace(',','')
        else:
            highlighterContent2 = (doc.get('ingredient')).replace(',','')
        if highlighterContent3:
            pass
        else:
            highlighterContent3 = doc.get('taste')
        if highlighterContent4:
            pass
        else:
            highlighterContent4 = doc.get('tech')
        results.append((highlighterContent, doc.get('img'), doc.get('content').replace(' ',''), 
            highlighterContent2, highlighterContent3, highlighterContent4, doc.get('others').replace(',',''), doc.get('url'), scoreDoc.score))

        for i in range(0, min(20,len(results)) - 1):
            flag = True
            for j in range(0, min(20, len(results)) - i -1):
                if abs(results[j][8] - results[j+1][8]) < 0.1 and urlclick[results[j][7]] < urlclick[results[j+1][7]]:
                    flag = False
                    results[j], results[j+1] = results[j+1], results[j]
            if flag:
                break

    return results, swxc_res

def findres(command, scoreDocs, searcher):
    res = ''
    for i in command.split():
        if i in swxc_name:
            res = swxc_dic[i.encode('utf8')]
            if i in msjsc_name:
                return (i, msjsc_dic[i.encode('utf8')] + '@' + res)
            return (i, res)
    for i in command.split():
        if i in msjsc_name:
            return (i, msjsc_dic[i.encode('utf8')])
    data = []
    n = 0
    for scoreDoc in scoreDocs:
        n += 1
        if n > 11:
            break
        doc = searcher.doc(scoreDoc.doc)
        for s in (doc.get('nameforsearch')).split():
            if len(s) <= 4:
                data.append(s)
        for s in ((doc.get('ingredient')).replace(',','')).split():
            if len(s) <= 4:
                data.append(s)
    num = 0
    maxname = ''
    for name in swxc_name:
        tmp = 0
        for j in data:
            if j == name:
                tmp += 1
        if tmp>num:
            num = tmp
            maxname = name
    if num > 5:
        if maxname in msjsc_name:
            return (maxname, msjsc_dic[maxname] + '@' + swxc_dic[maxname])
        return (maxname, swxc_dic[maxname])

    num = 0
    maxname = ''
    for name in msjsc_name:
        tmp = 0
        for j in data:
            if j == name:
                tmp += 1
        if tmp>num:
            num = tmp
            maxname = name
    if num > 5:
        return (maxname, msjsc_dic[maxname])


def search(command, urlclick):
    command, command_dict = parseCommand(command)
    if command_dict[0] or command_dict[1]:
        return superSearch(command, command_dict, urlclick)
    else:
        return vagueSearch(command, urlclick)



tag = ['nameforsearch','ingredient', 'taste', 'tech', 'others', 'contentforsearch']
swxc_dic, swxc_name = swxc.readin("swxc.txt")
msjsc_dic, msjsc_name = swxc.readin_msj("msjsc.txt")


vm_env = lucene.initVM()
print 'lucene', lucene.VERSION
