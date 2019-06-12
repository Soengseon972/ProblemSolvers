from django.db import connection
from cp1.models import flightInfo
def getInfo(dep, arr):
	#dep = "北京"
	#arr = "长沙"
	#print("ee")
	cursor = connection.cursor()
	#查询
	cursor.execute("select * from cp1_flightInfo where dep_loc like '"+dep+"%' and arr_loc like '"+arr+"%'")
	#print("ee")
	#返回一行
	raw = cursor.fetchall()
	print(raw)
	return raw
# #返回所有
