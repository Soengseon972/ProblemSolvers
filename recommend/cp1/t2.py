from django.db import connection
from django.shortcuts import render
from . import trytry
def tt2(request):
	dep = "北京"
	arr = "长沙"
	raw = trytry.getInfo(dep, arr)
	print(raw)
	return render(request, 'cp1/index.html')
# #返回所有
