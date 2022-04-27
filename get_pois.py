# -*- coding: utf-8 -*-
"""
Created on Saturday April 9 10:13:00 2021
E-mail = 1452204356@qq.com
@author: Allen
"""

'''
实现的功能：
① 按区域（cityname）按类别（classfiled）提取poi点
② 将提取的poi点转为表格
'''

## 安装所需的第三方库（利用pip）
from urllib.parse import quote
from urllib import request
import json
import pandas as pd

## ------------------分页抓取高德地图上感兴趣的场所点的相关信息------------
def get_rois_from_page(url, web_key, cityname, classfiled, page_num):
    ALLpage_rois = {} ## 记录每一页的poi信息
    for i in range(int(page_num)):  # 爬取的页面信息，i=2时即爬取前2页的数据。若要提取所有页面，将range函数里的数设置为很大的一个数据即可比如1e10
        req_url = url + "?key=" + web_key + '&extensions=all&keywords=' + quote(classfiled) + '&city=' + quote(cityname) + '&citylimit=true' +\
                  '&offset=25' + '&page=' + str(i) + '&output=json'
        data = ''
        f=request.urlopen(req_url)
        data = f.read()
        data = data.decode('utf-8')
        result=json.loads(data)
        if i%10==0:
            print('正在获取%s第%d页的%s信息'%(cityname, i,classfiled))
        if result['count'] == '0': ## 当result['count']=0页面已经无信息，爬取所有数据时可以用此终止循环
            break
        ALLpage_rois[i] = result
    return ALLpage_rois ## 返回所有页面的roi信息

## 将爬取到的分页poi数据字典转为完整的poi字典
def get_pois_fromDict(ALLpage_rois):
    pois = []
    for i in range(len(ALLpage_rois)):
        page_dict = ALLpage_rois[i]['pois']
        for j in range(len(page_dict)):
            pois.append(page_dict[j])
        print('正在读取第%d页的poi数据点'%i)
    return pois ## 返回完整的兴趣点字典（每个地点都是一个字典）

## 将完整的poi字典（每个地点都是一个字典）转化为一个字典
def poisInfo_to_a_dict(pois):
    pois_one_dict = {}
    for item in pois:
        for k,v in item.items():
            pois_one_dict.setdefault(k, []).append(v)
    return pois_one_dict ## 返回由一个字典表达的所有poi的相关信息

## 获取需要的的poi信息
def get_useful_poisInfo(pois_one_dict):
    geo_location = pois_one_dict['location']
    x,y = [],[]  ## 存放地点的地理经度和纬度
    for i in range(len(geo_location)): ## 得到地点的经纬度信息
        x.append(geo_location[i].split(',')[0])
        y.append(geo_location[i].split(',')[1])
    useful_poisInfo = {
            'name':pois_one_dict['name'],
            'tpye':pois_one_dict['type'],
            'x': x,
            'y': y,
            'province': pois_one_dict['pname'],
            'city': pois_one_dict['cityname'],
            'adname': pois_one_dict['adname'],
            'address': pois_one_dict['address'],
            'business_area': pois_one_dict['business_area'],
            'timestamp': pois_one_dict['timestamp'],
            'tel': pois_one_dict['tel'],
            'photos_link':pois_one_dict['photos']
            }
    return  useful_poisInfo ## 返回需要的兴趣点相关信息

## 将字典存为csv方便观察和加载到arcgis中显示
def dic_to_csv(dic_data,csvsave_path):
    pd.DataFrame(dic_data).to_csv(csvsave_path,encoding='utf_8_sig')

## --------------基本参数---------------------------
url = "http://restapi.amap.com/v3/place/text"   ## 查找地点数据的基路径
## 可能变化的的参数
web_key = '376af2a53019f8d8d4604ea094c536b2'    ## 高德开放平台中web应用的key密钥
cityname = "天河区"      ## 限定的城市范围
classfiled = "幼儿园"   ## 感兴趣的目标场所类别（比如医院、幼儿园等）
page_num = 10 ##需要获取兴趣点的页面数。如需获取全部兴趣点，可设置为1e10
## -----------------------------------------------

## --------------------------------------------------------------
ALLpage_rois = get_rois_from_page(url, web_key, cityname, classfiled, page_num) ## 返回所有页面的roi信息
pois = get_pois_fromDict(ALLpage_rois) ## 返回完整的兴趣点字典（每个地点都是一个字典），相当于变成一页展示兴趣点
pois_one_dict = poisInfo_to_a_dict(pois) ## 返回由一个字典表达的所有poi的相关信息，方便转换成表格
useful_poisInfo = get_useful_poisInfo(pois_one_dict) ## 返回需要的兴趣点相关信息
csv_save_path = './POIS/%s_%s.csv'%(cityname, classfiled) ## 兴趣点转为表格时保存.csv文件的路径
dic_to_csv(useful_poisInfo,csv_save_path) ## 将字典转为csv表格数据

