from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
import time
import os
import random
# Create your views here.



class outLinkForm(forms.Form):
    
    outlink = forms.CharField(max_length=200)


def homePage(request):

    content = {'autocomplete':names+ingredients}
    return render(request,'homePage_b.html',content)


def wallPaper(request):

    wp_lst = os.listdir('src/wp')
    rd = random.randint(1,len(wp_lst))
    return HttpResponseRedirect('/static/wp/'+wp_lst[rd-1])


def clickCount(request):
    
    if request.method == 'GET':
        form = outLinkForm(request.GET)
        if form.is_valid():
            link = form.cleaned_data['outlink']
            if link in click_cnt:
                click_cnt[link] += 1
            else:
                click_cnt[link] = 1
            with open('CLICK_CNT.txt','w') as click_file:
                for u,c in click_cnt.items():
                    click_file.write('%s,%s\n'%(u,c))
            return HttpResponseRedirect(link)
        else:
            print 'invalid'
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')

ingred_s = open('ingre_sort.txt')
name_s = open('name_sort.txt')
ingredients = [l.split()[0].decode('utf-8') for l in ingred_s.readlines()]
names = [l.split()[0] for l in name_s.readlines()]
random.seed(time.time())
ingred_s.close()
name_s.close()

click_cnt = {}
with open('CLICK_CNT.txt') as click_file:
    for l in click_file.readlines():
        item = l[:-1].split(',')
        u = item[0]
        if len(item) == 2:
            c = int(item[1])
        else:
            c = 0
        click_cnt[u] = c