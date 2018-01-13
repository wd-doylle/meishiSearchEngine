#!/usr/bin/env python
#-*- coding:utf8 -*-
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time
from datetime import datetime

# import re
# from zhon.hanzi import punctuation
# import string

from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import  WhitespaceAnalyzer
from org.apache.lucene.analysis.core import  SimpleAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from urlparse import urlparse
import jieba
import my_jieba

"""
index1: setboost 1
index2: setboost 0.1
index3: setboost 0.1, equiped with punctuation
index4: setboost 0.1, equiped with punctuation, jieba with new dict
index5: 
index6: all cut
"""

reload(sys)
sys.setdefaultencoding('utf8')
jieba.load_userdict("foodname.txt")
jieba.load_userdict("food_dic.txt")
# c_punc = punctuation
# e_punc = string.punctuation.decode('utf-8')

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.5)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, root, writer):
        global countAll

        print 'indexDocs working'

        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)
        
        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(True)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                try:
                    path = os.path.join(root, filename)
                    file = open(path)
                    string = file.read()
                    file.close()
                    if string == '':
                        continue

                    name, img, ingredient, taste, tech, others, content = string.split("|",6)
                    if len(img) < 55 and len(img) != 40:
                        continue
                    
                    countAll+=1
                    print "adding", filename

                    tmplist = content.split('|')
                    url = tmplist[-1]
                    content = "".join(tmplist[:-1])

                    # content = content.decode('utf-8')
                    # seg_list = re.split('(['+c_punc+e_punc+'])',content)
                    content_show = ' '.join(jieba.cut(content))
                    content_search = ' '.join(jieba.cut_for_search(content))
                    # for seg in seg_list:
                    #     if len(seg) == 1:
                    #         content_show += ' ' + seg.encode('utf-8')
                    #         content_search += ' ' + seg.encode('utf-8')
                    #     if len(seg) > 1:
                    #         content_show += ' ' + ' '.join(jieba.cut(seg.encode('utf-8'))) 
                    #         content_search += ' ' + ' '.join(jieba.cut_for_search(seg.encode('utf-8'))) 

                    name_not_cut = "".join(my_jieba.cut(name))
                    name_show = " ".join(jieba.cut(name))
                    name_search = " ".join(jieba.cut_for_search(name))
                    tmp = ingredient.split(',')
                    ingredient = ''
                    for t in tmp:
                        ingredient += ','.join(jieba.cut(t)) + ' '
                    tmp = others.split(',')
                    others = ''
                    for t in tmp:
                        others += ','.join(jieba.cut(t)) + ' '


                    doc = Document()
                    doc.add(Field("name", name_show, t2))
                    doc.add(Field("name_not_cut", name_not_cut, t2))
                    doc.add(Field("nameforsearch", name_search, t2))
                    doc.add(Field("img", img, Field.Store.YES, Field.Index.NOT_ANALYZED))
                    doc.add(Field("url", url, Field.Store.YES, Field.Index.NOT_ANALYZED))
                    doc.add(Field("ingredient", ingredient, t1))
                    doc.add(Field("taste", taste, t1))
                    doc.add(Field("tech", tech, t1))
                    doc.add(Field("others", others, t1))
                    f_show = Field("content", content_show, t2)
                    f_search = Field("contentforsearch", content_search, t2)
                    f_search.setBoost(0.1)
                    doc.add(f_show)
                    doc.add(f_search)
                    writer.addDocument(doc)

                except Exception, e:
                    print "Failed in indexDocs:", e
        print countAll


countAll=0
if __name__ == '__main__':
    """
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    """
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    try:
        """
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
                   """
        analyzer =  SimpleAnalyzer(Version.LUCENE_CURRENT)
        IndexFiles(os.getcwd()+'/'+'data2', "index2.3", analyzer)
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
        raise e
