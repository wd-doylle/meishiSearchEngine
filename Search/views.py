# -*-coding:utf-8 -*-
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_text
import sys
sys.path.append('index')
from search_sort import search
# Create your views here.


def validate_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


class SearchCommand(forms.Form):

    q = forms.CharField(max_length=100)
    pg = forms.IntegerField()


class BooleanCommand(forms.Form):
    
    q = forms.CharField(max_length=100)
    f = forms.CharField(max_length=100)
    ing = forms.CharField(max_length=100)
    t = forms.CharField(max_length=100)
    f_n = forms.CharField(max_length=100)
    ing_n =forms.CharField(max_length=100)
    t_n = forms.CharField(max_length=100)


def results(request):

    if request.method == 'GET':
        form = SearchCommand(request.GET)
        if form.is_valid():
            command = form.cleaned_data['q']
            page = form.cleaned_data['pg']
        else:
            print 'invalid'
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')
    
    click_cnt = {}
    with open('CLICK_CNT.txt') as click_file:
        for l in click_file.readlines():
            item = l[:-1].split(',')
            u = item[0]
            if len(item) == 2:
                click_cnt[u] = int(item[1])
            else: 
                click_cnt[u] = 0
    result, recommand = search(command,click_cnt)
    result_cnt = len(result)
    disp = [list(r) for r in result[10*(page-1):10*page]]
    for d in disp:
        if d[7].startswith('http://www.zhms.cn/'):
            d[1] = '/static/img/img/'+validate_filename(d[1])+'.jpg'
        d.append('/cc/?outlink='+d[7])
    if recommand:
        recommand = list(recommand)
        recommand[1] = recommand[1].split('@')
    end = 10*(page-1) >= result_cnt
    content = {'command':command,'page':page,'result':disp,'result_cnt':result_cnt,'iter':range(max(1,page-3),min(max(1,page-3)+6,result_cnt/10+2)),'last':page*10 >= len(result),'end':end,'autocomplete':names+ingredients,"recommand":recommand}
    
    return render(request, 'resultPage_b.html',content)


def booleanSearch(request):
    
    if request.method == 'GET':
        form = BooleanCommand(request.GET)
        form.is_valid()
        if "q" not in form.cleaned_data:
            return render(request,'booleanSearch_b.html')
        command = form.cleaned_data['q']
        for item in ['f','ing','t','f_n','ing_n,t_n']:
            if item in form.cleaned_data and form.cleaned_data[item]:
                it = item if not item.endswith('_n') else '!%s' % item.split('_')[0]
                it = it if it != 'ing' else 'in'
                command += '|%s$%s' % (it,form.cleaned_data[item])
        return HttpResponseRedirect('/s/?pg=1&q='+command)
    else:
        return HttpResponseRedirect('/')

ingred_s = open('Search/ingre_sort.txt')
name_s = open('Search/name_sort.txt')
ingredients = [l.split()[0].decode('utf-8') for l in ingred_s.readlines()]
names = [l.split()[0] for l in name_s.readlines()]
ingred_s.close()
name_s.close()

