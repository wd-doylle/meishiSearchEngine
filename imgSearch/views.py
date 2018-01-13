from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
# from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
# from django.core.files.storage import FileSystemStorage
# from django.db import models
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
from datetime import datetime
# from PIL import Image
import os
import BoWSearch
import requests
# Create your views here.



class SearchCommand(forms.Form):
    
    q = forms.CharField(max_length=100)


class ImageUploadForm(forms.Form):
    
    img = forms.ImageField()


def validate_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


def imgHomePage(request):

    # return render(request,'imgHomePage.html')
    return render(request,'imgHomePage_b.html')




def imgResults(request):

    path = os.path.join(os.path.abspath('.'),'tmp/img/')
    if not os.path.exists(path):
        os.makedirs(path)
    url = ''
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = request.FILES['img']
            filename = img.name
            with open(os.path.join(path,filename),'wb+') as destination:  
                for chunk in img.chunks():  
                    destination.write(chunk)
        else:
            return HttpResponseRedirect('/im')
    elif request.method == 'GET':
        form = SearchCommand(request.GET)
        if form.is_valid():
            url = form.cleaned_data['q']
            img = requests.get(url).content
            filename = validate_filename(url)
            with open(os.path.join(path,filename),'wb+') as destination:
                destination.write(img)
        else:
            return HttpResponseRedirect('/im')
    else:
        form = ImageUploadForm()
        return HttpResponseRedirect('/im')


    res = BoWSearch.search_img(os.path.join(path,filename), 20)
    result = [r.split('|') for r in res]
    result_cnt = len(res)
    for d in result:
        if d[7].startswith('http://www.zhms.cn/'):
            d[1] = '/static/img/img/'+validate_filename(d[1])+'.jpg'
        d.append('/cc/?outlink='+d[7])
    end = result_cnt == 0
    content = {'command':url,'result':result,'result_cnt':result_cnt,'end':end}
    return render(request,'imgResults_b.html',content)



        