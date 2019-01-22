# -*- coding: utf-8 -*-
#Author: kyn
#Date: 2018-2-28
#Purpose: 解析excel数据表到lua
import os
import sys
import xlrd
import random
import math
import string
from xlutils.copy import copy

reload(sys)
sys.setdefaultencoding('utf8')

# excel 路径
xls_path = "/Users/koba/Documents/work/FishingData/testData/"
# 距离ID
distanceId=0

# 查找所有 xls
def findAllFile(dirPath,callback,db_route):
	fileList = os.listdir(dirPath)
	for f in fileList:

		filePath = os.path.join(dirPath,f)

		if f[0] == "." or f.find(".svn") > 0 or f.find(".DS_Store") > 0 or f.startswith("~$"):
			continue
	
		if os.path.isdir(filePath):
			findAllFile(filePath,callback,db_route)
		else:
			if f.endswith(".xls") or f.endswith(".xlsx"):
				# print(filePath)
				callback(filePath,f,db_route)

# 检测是否为stage表
def checkIsStage(filePath,fileName,db_route):
	fileNames=[]
	if fileName and fileName.find("_") != -1:
		fileNames = fileName.split("_")
		if fileNames[1]=="Stage" and fileNames[2] and fileNames[2].split(".")[0].isdigit():
			caleTime(filePath,db_route)


# 计算时间
def caleTime(stageFile,db_route):
	global distanceId
	rb = xlrd.open_workbook(stageFile)
	#通过sheet_by_index()获取的sheet没有write()方法
	rs = rb.sheet_by_index(0)
	wb = copy(rb)
	# 利用xlutils.copy函数，将xlrd.Book转为xlwt.Workbook，再用xlwt模块进行存储
	ws = wb.get_sheet(0)

	# 检测字段位置，防止因表内字段顺序改变，导致bug
	MoveTimes_index=0
	RouteId_index=0
	Speed_index=0
	for k in range(rs.ncols):
		if rs.cell(2,k).value=="MoveTimes":
			MoveTimes_index=k
		if rs.cell(2,k).value=="RouteId":
			RouteId_index=k
		if rs.cell(2,k).value=="Speed":
			Speed_index=k

	# 循环字段
	for k in range(rs.nrows):
		if k>2 and rs.cell(k,RouteId_index).ctype>0:
			# 获取Route 表 distance 数据
			routeId=int(rs.cell(k,RouteId_index).value)

			distances=db_route.cell(routeId+2,distanceId).value.split(",")
			# 速度
			speed=rs.cell(k,Speed_index).value

			str1=""
			for dis in (distances):
				str1+=str(round(int(dis)/float(speed),2))+","
			
			ws.write(k,MoveTimes_index,str1[:-1])
	wb.save(stageFile)

def run(sXls_path):
	if sXls_path:
		xls_path=sXls_path

	global distanceId
	db_route = xlrd.open_workbook(os.path.join(xls_path,"2_Route.xls")).sheet_by_index(0)
	for k in range(db_route.ncols):
		if db_route.cell(2,k).value=="Distance":
			distanceId=k

	# 循环stage文件,并设置值
	findAllFile(xls_path,checkIsStage,db_route)

	if sXls_path:
		import gitTool
		print gitTool.commit(xls_path)

if __name__ == '__main__':

	if len(sys.argv)==2:
		xls_path=sys.argv[1]

	db_route = xlrd.open_workbook(os.path.join(xls_path,"2_Route.xls")).sheet_by_index(0)
	for k in range(db_route.ncols):
		if db_route.cell(2,k).value=="Distance":
			distanceId=k

	# 循环stage文件,并设置值
	findAllFile(xls_path,checkIsStage,db_route)

	# print "---解析完毕！---"
	if len(sys.argv)==2:
		import gitTool
		print gitTool.pull(xls_path)






