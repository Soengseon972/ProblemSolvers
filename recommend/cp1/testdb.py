# -*- coding: utf-8 -*-
from django.shortcuts import render
from cp1.models import flightInfo
 
import requests
from bs4 import BeautifulSoup
import random
import datetime
import re
# 得到所有地方航班及链接
def getAllFlights():
    flights = {}   # {'安庆航班': 'https://flights.ctrip.com/schedule/aqg..html', ...}
    url = 'https://flights.ctrip.com/schedule'
    headers = {
        'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'zh-CN,zh;q=0.9',
        'upgrade-insecure-requests':'1'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    letter_list = soup.find( attrs={'class':'letter_list'} ).find_all('li')
    for li in letter_list:
        for a in li.find_all('a'):
            flights[a.get_text()] = url + a['href'][9:]
    return flights

# 得到一个地方航班的所有线路
def getFlightLines(url):
    flightlines = {}   # {'安庆-北京': 'http://flights.ctrip.com/schedule/aqg.bjs.html', ...｝
    headers = {
        'Referer': 'https://flights.ctrip.com/schedule/',
        'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    try:
    	letter_list = soup.find(attrs={'id': 'ulD_Domestic'}).find_all('li')
    except AttributeError:
    	print("no flight for")
    	return flightlines
    else:
	    for li in letter_list:
	        for a in li.find_all('a'):
	            flightlines[a.get_text()] = a['href']

	    return flightlines

# 得到这条线路的所有航班信息
def getFlightInfo(url):
	flightInfos = []
	headers = {
		'Host': 'flights.ctrip.com',
		'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
	}
	response = requests.get(url, headers=headers)
	soup = BeautifulSoup(response.text, 'lxml')
	try:
		flights_tr = soup.find(attrs={'id':'flt1'}).find_all('tr')
	except AttributeError:
		print("***** no flight for")
		return flightInfos
	else:
	    for tr in flights_tr:        # 遍历每个一航班
	        theflightInfo = {}
	        info_td = tr.find_all('td')
	        # 航班编号
	        flight_no = info_td[0].find('strong').get_text().strip()
	        theflightInfo['flight_no'] = flight_no
	        # 起飞时间
	        flight_stime = info_td[1].find('strong').get_text().strip()
	        theflightInfo['flight_stime'] = flight_stime
	        # 起飞机场
	        flight_sairport = info_td[1].find('div').get_text().strip()
	        theflightInfo['flight_sairport'] = flight_sairport
	        # 降落时间
	        flight_etime = info_td[3].find('strong').get_text().strip()
	        theflightInfo['flight_etime'] = flight_etime
	        # 降落机场
	        flight_eairport = info_td[3].find('div').get_text().strip()
	        theflightInfo['flight_eairport'] = flight_eairport
	        # 班期
	        flight_schedule = []
	        for s in info_td[4].find(attrs={'class':'week'}).find_all(name='span', attrs={'class':'blue'}):
	            flight_schedule.append(s.get_text().strip())
	        flight_schedule = ' '.join( flight_schedule )
	        theflightInfo['flight_schedule'] = flight_schedule
	        # 准点率
	        flight_punrate = info_td[5].get_text().strip()
	        theflightInfo['flight_punrate'] = flight_punrate
	        # 价格
	        flight_price = info_td[6].get_text().strip()
	        theflightInfo['flight_price'] = flight_price

	        flightInfos.append(theflightInfo)
	    return flightInfos

def get_price_from_str(price):
	
	return re.findall(r"\d+", price)

def get_duration(stime, etime):
	
	d1 = datetime.datetime.strptime(stime,"%H:%M")
	d2 = datetime.datetime.strptime(etime,"%H:%M")
	if ((d2-d1).days < 0):#跨天
		d2 = d2+datetime.timedelta(days=1)
	p = re.findall(r"^\d+:\d+", str(d2-d1))
	if len(p[0]) < 5:
		p[0] = "0"+p[0]
	return p[0]
# 数据库操作
def testdb(request):
	atlast = False
	allFlights = getAllFlights();
	for flight in allFlights.keys():
		if flight != "梅县航班":
			if not atlast:
				continue
		else :
			atlast = True
			continue
		flightlines = getFlightLines(allFlights[flight])
		if not flightlines:
			continue
		for line in flightlines.keys():
			flightInfos = getFlightInfo(flightlines[line])
			if not flightInfos:
				continue
			for info in flightInfos:
				price = get_price_from_str(info['flight_price'])
				if (len(price) == 0):
					continue
				pr = price[0]
				dur_t = get_duration(info['flight_stime'], info['flight_etime'])
				test1 = flightInfo(flight_no=info['flight_no'], dep_time=info['flight_stime'],
					dep_loc=info['flight_sairport'], arr_time=info['flight_etime'], arr_loc=info['flight_eairport'],
					flight_schedule=info['flight_schedule'],norm_price=pr, dur_time = dur_t)
				test1.save()

	return render(request, 'cp1/index.html')