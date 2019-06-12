# -*- coding: utf-8 -*-
'''
获取12306城市名和城市代码的数据
文件名： parse_station.py
'''
#from django.db import connection
from django.shortcuts import render
from cp1.models import flightInfo

import requests
import re
import json
import time
#关闭https证书验证警告
requests.packages.urllib3.disable_warnings()
all_price = {}
#cursor = connection.cursor()
def getStation():
        # 12306的城市名和城市代码js文件url
        url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9018'
        r = requests.get(url,verify=False)
        pattern = u'([\u4e00-\u9fa5]+)\|([A-Z]+)'
        result = re.findall(pattern,r.text)
        station = dict(result)#{'北京北': 'VAP', '北京东': 'BOP', '北京': 'BJP',
        #print(station)
        return station
 
'''
查询两站之间的火车票信息
输入参数： <date> <from> <to>
12306 api:
'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2017-07-18&leftTicketDTO.from_station=NJH&leftTicketDTO.to_station=SZH&purpose_codes=ADULT'
'''
 
 
 
 
 
#生成查询的url
def get_query_url(text, from_station_name, to_station_name, date):
    # 城市名代码查询字典
    # key：城市名 value：城市代码
 
    try:
        #date = '2019-07-01'
        #from_station_name = '长沙南'
        #to_station_name = '北京'
        from_station = text[from_station_name]
        to_station = text[to_station_name]
    except:
        date, from_station, to_station = '--', '--', '--'
        # 将城市名转换为城市代码
 
    # api url 构造
    url = (
        'https://kyfw.12306.cn/otn/leftTicket/query?'
        'leftTicketDTO.train_date={}&'
        'leftTicketDTO.from_station={}&'
        'leftTicketDTO.to_station={}&'
        'purpose_codes=ADULT'
    ).format(date, from_station, to_station)
    #print(url)
 
    return url
 
 
def get_price_info(train_no, from_station_no, to_station_no, seat_types, chufa_date):
 
    link = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no={}&from_station_no={}&to_station_no={}&seat_types={}&train_date={}'.format(train_no, from_station_no, to_station_no, seat_types, chufa_date)
    
    try:
        link_text = requests.get(link, verify=False)
        link_json = link_text.json()['data']
        # 解析是什么座位，并加上颜色
        
        return link_json
    except:
        print('error')
    
 
#获取信息
def query_train_info(url,text):
    '''
    查询火车票信息：
    返回 信息查询列表
    '''
 
    info_list = []
    try:
        r = requests.get(url, verify=False)
        
        # 获取返回的json数据里的data字段的result结果
        raw_trains = r.json()['data']['result']
 
        for raw_train in raw_trains:
            # 循环遍历每辆列车的信息
            data_list = raw_train.split('|')
            if (data_list[11] != "Y" and data_list[11] != "N"):
                continue
            #查询价格
            # 车次很长的查询号码
            train_longno = data_list[2]
            #  出发到达 01 03
            from_station_no = data_list[16]
            to_station_no = data_list[17]
            seat_types = data_list[35]
            chufa_date = data_list[13]
            chufa_riqi = chufa_date[0:4]+"-"+chufa_date[4:6]+"-"+chufa_date[6:8]
            print(train_longno+"\t"+from_station_no+"\t"+to_station_no+"\t"+seat_types+"\t"+chufa_riqi)
            p = 0
            if (from_station_no not in all_price.keys()):
                price = get_price_info(train_longno, from_station_no, to_station_no, seat_types, chufa_riqi)
                
                if 'O' in price:
                    p = price['O']
                elif 'A3' in price:
                    p = price['A3'] 
                all_price[from_station_no] = dict(to_station_no = p)#直接创建
                all_price[to_station_no] = dict(from_station_no = p)

            elif (to_station_no not in all_price[from_station_no].keys()):
                price = get_price_info(train_longno, from_station_no, to_station_no, seat_types, chufa_riqi)
                
                if 'O' in price:
                    p = price['O']
                elif 'A3' in price:
                    p = price['A3'] 
                all_price[from_station_no][to_station_no] = p
                if (to_station_no not in all_price.keys()):
                    all_price[to_station_no] = dict(from_station_no = p)
                else:
                    all_price[to_station_no][from_station_no] = p
            else:
                p = all_price[from_station_no][to_station_no]
            print(p)

            # 车次号码
            train_no = data_list[3]
            # 出发站
            from_station_code = data_list[6]
            #from_station_name = text['上海']
            # 终点站
            to_station_code = data_list[7]
            #to_station_name = text['北京']
            # 出发时间
            start_time = data_list[8]
            # 到达时间
            arrive_time = data_list[9]
            # 总耗时
            time_sum_up = data_list[10]
            # 一等座
            # first_class_seat = data_list[31] or '--'
            #first_class_price = price['M'] if 'M' in price else '--'
            # 二等座
            second_class_seat = data_list[30]or '--'
            #second_class_price = price['O'] if 'O' in price else '--'
            # 软卧
            # soft_sleep = data_list[23]or '--'
           # soft_sleep_price = price['A4'] if 'A4' in price else '--'
            # 硬卧
            hard_sleep = data_list[28]or '--'
            #hard_sleep_price = price['A3'] if 'A3' in price else '--'
            # 硬座
            #hard_seat = data_list[29]or '--'
            #hard_seat_price = price['A1'] if 'A1' in price else '--'
            # 无座
            #no_seat = data_list[26]or '--'
            #no_seat_price = price['WZ'] if 'WZ' in price else '--'
            # 打印查询结果
            #info = ('车次:{}\n出发站:{}\n目的地:{}\n出发时间:{}\n到达时间:{}\n消耗时间:{}\n座位情况：\n 一等座：「{}」 票价：{}\n二等座：「{}」 票价：{}\n软卧：「{}」 票价：{}\n硬卧：「{}」 票价：{}\n硬座：「{}」 票价：{}\n无座：「{}」 票价：{}\n\n'.format(
            #    train_no, list (text.keys()) [list (text.values()).index (from_station_code)], list (text.keys()) [list (text.values()).index (to_station_code)], start_time, arrive_time, time_sum_up, first_class_seat, first_class_price,
            #    second_class_seat, second_class_price, soft_sleep, soft_sleep_price, hard_sleep, hard_sleep_price, hard_seat, hard_seat_price, no_seat, no_seat_price))
            #cursor.execute("INSERT INTO cp1_flightInfo (flight_no, dep_time, dep_loc, arr_time, arr_loc, flight_schedule, norm_price, dur_time) values (%s,%s,%s,%s,%s,%s,%s,%s)",  [train_no,start_time,list (text.keys()) [list (text.values()).index (from_station_code)],arrive_time,list (text.keys()) [list (text.values()).index (to_station_code)], "一 二 三 四 五 六 日", p, time_sum_up]) 
            #print()
            test1 = flightInfo.objects.create(id=1,flight_no=train_no, dep_time=start_time,
                    dep_loc=list (text.keys()) [list (text.values()).index (from_station_code)], arr_time=arrive_time, arr_loc=list (text.keys()) [list (text.values()).index (to_station_code)],
                    flight_schedule="一 二 三 四 五 六 日",norm_price=p, dur_time = time_sum_up)
            test1.save()
            #print(info)
            #info_list.append(info)
 
        #return info_list
    except:
        return ' 输出信息有误，请重新输入'
 
def traindb(request):
    text=getStation();
    count = 1
    date = '2019-06-15'
    wuzong1 = ["哈尔滨","扶余","长春","四平南","沈阳","营口","大连","烟台","青岛","日照","连云港","盐城","南通","上海"]
    for st_from_name in wuzong1:
        for st_to_name in wuzong1:
            if (st_to_name == st_from_name):
                continue
            #print("here")
            url=get_query_url(text, st_from_name, st_to_name, date)  
            query_train_info(url,text)
            time.sleep(2)
    return render(request, 'cp1/index.html')