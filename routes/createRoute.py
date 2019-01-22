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
xls_path = "/Users/koba/Documents/work/FishingData/testData/2_Route.xls"
# 生成数量
count = 100
# 贝塞尔曲线点数
bezierPointNum=21
# 屏幕尺寸
screenWidth = [-200,1136+200]
screenHeight = [-200,640+200]
# sheel行数
m_rowNum=0
m_colNum=0
m_isHasData=True
# title对应的次序，即使插入，也不会打乱工具生成顺序
title = {"ID":0,"IsLine":1,"Kind":2,"InPoint":3,"OutPoint":4,"ControllPoint1":5,"ControllPoint2":6,"CPNum":7,"Points":8,"Distance":9,"TotalDistance":9}
rowData = {}

#随机
def randomInt(minNum=1,MaxNum=100):
	return random.randint(minNum,MaxNum)

# 检查表大小(目的，提高效率，减少不必要空字段检查)
def checkTableSize(pTabData):
	# 获取表格默认大小
	nrows = pTabData.nrows
	ncols = pTabData.ncols
	global m_rowNum,m_colNum

	for row in range(nrows):
		cell = pTabData.cell(row,0)
		if cell.ctype>0:
			m_rowNum = row-2
	# 检查列
	for col in range(ncols):
		cell = pTabData.cell(2,col)
		if cell.ctype>0:
			title[cell.value]=col
			m_colNum = col+1

# 创建每一个行数据
def createRowData(rSheel,wSheel,nRow):
	global rowData,m_isHasData
	row = nRow+3
	# 该行无数据，需要创建数据
	if nRow+1>m_rowNum:
		m_isHasData = False
		rowData["ID"]=nRow+1
		rowData["Kind"]=1
		wSheel.write(row,title["ID"],rowData["ID"])
		wSheel.write(row,title["Kind"],rowData["Kind"])
	else:
		cell = rSheel.cell(row,title["ID"])
		if cell.ctype>0:
			rowData["ID"]=cell.value

		cell1 = rSheel.cell(row,title["Kind"])
		if cell1.ctype>0:
			rowData["Kind"]=cell1.value
	# 创建是否直线
	createIsLine(rSheel,wSheel,nRow)

# 创建是否直线 
def createIsLine(rSheel,wSheel,nRow):
	# 30%概率是直线
	if m_isHasData:
		cell = rSheel.cell(nRow+3,title["IsLine"])
		if cell.ctype==0:
			rowData["IsLine"]=randomInt()<=50 and 1 or 0
			wSheel.write(nRow+3,title["IsLine"],rowData["IsLine"])
		else:
			rowData["IsLine"]=cell.value
	else:
		rowData["IsLine"]=randomInt()<=50 and 1 or 0
		wSheel.write(nRow+3,title["IsLine"],rowData["IsLine"])

	# 创建进出点
	createInOutPoint(rSheel,wSheel,nRow)

# 创建进出点
def createInOutPoint(rSheel,wSheel,nRow):
	global rowData,m_isHasData
	if m_isHasData:
		if rowData["Kind"]==1:
			rowData["CPNum"]=rSheel.cell(nRow+3,title["CPNum"]).value
			rowData["InPoint"]= rSheel.cell(nRow+3,title["InPoint"]).value.split(",")
			rowData["OutPoint"]= rSheel.cell(nRow+3,title["OutPoint"]).value.split(",")
	else:
		# 创建进出点
		# 目前先设置每条边100个数据,并且进出点不在同一边
		# 同时设置 直向概率为80%，向两边走的概率为20%
		# 超过400条的，纯随机
		if nRow<count*0.25:
			rowData["InPoint"]= [screenWidth[0],randomInt(screenHeight[0],screenHeight[1])]
			tmp = randomInt()
			if tmp<80:
				rowData["OutPoint"]= [screenWidth[1],randomInt(screenHeight[0],screenHeight[1])]
			elif tmp<90:
				rowData["OutPoint"]= [randomInt(screenWidth[0],screenWidth[1]),screenHeight[1]]
			else:
				rowData["OutPoint"]= [randomInt(screenWidth[0],screenWidth[1]),screenHeight[0]]

		elif nRow<count*0.5:
			rowData["InPoint"]= [randomInt(screenWidth[0],screenWidth[1]),screenHeight[1]]
			tmp = randomInt()
			if tmp<80:
				rowData["OutPoint"]= [randomInt(screenWidth[0],screenWidth[1]),screenHeight[0]]
			elif tmp<count*90:
				rowData["OutPoint"]= [randomInt(screenWidth[0],screenWidth[1]),screenHeight[1]]
			else:
				rowData["OutPoint"]= [screenWidth[0],randomInt(screenHeight[0],screenHeight[1])]
		elif nRow<count*0.75:
			rowData["InPoint"]= [screenWidth[1],randomInt(screenHeight[0],screenHeight[1])]
			tmp = randomInt()
			if tmp<80:
				rowData["OutPoint"]= [screenWidth[0],randomInt(screenHeight[0],screenHeight[1])]
			elif tmp<90:
				rowData["OutPoint"]= [randomInt(screenWidth[0],screenWidth[1]),screenHeight[1]]
			else:
				rowData["OutPoint"]= [screenWidth[1],randomInt(screenHeight[0],screenHeight[1])]
		else:
			rowData["InPoint"]= [randomInt(screenWidth[0],screenWidth[1]),screenHeight[0]]
			tmp = randomInt()
			if tmp<80:
				rowData["OutPoint"]= [randomInt(screenWidth[0],screenWidth[1]),screenHeight[1]]
			elif tmp<90:
				rowData["OutPoint"]= [screenWidth[1],randomInt(screenHeight[0],screenHeight[1])]
			else:
				rowData["OutPoint"]= [screenWidth[0],randomInt(screenHeight[0],screenHeight[1])]

		wSheel.write(nRow+3,title["InPoint"], str(int(rowData["InPoint"][0]))+","+str(int(rowData["InPoint"][1])))
		wSheel.write(nRow+3,title["OutPoint"],str(int(rowData["OutPoint"][0]))+","+str(int(rowData["OutPoint"][1])))

		rowData["CPNum"]=randomInt(1,2)
		wSheel.write(nRow+3,title["CPNum"],rowData["CPNum"])
	createBezierPoint(rSheel,wSheel,nRow)

# 贝塞尔曲线控制点
def createBezierPoint(rSheel,wSheel,nRow):
	# 设置控制点，并限制范围
	global rowData,m_isHasData
	if m_isHasData:
		if rowData["IsLine"]==0:
			rowData["ControllPoint1"]= rSheel.cell(nRow+3,title["ControllPoint1"]).value.split(",")
			rowData["ControllPoint2"]= rSheel.cell(nRow+3,title["ControllPoint2"]).value.split(",")
	else:
		# 先默认 左右两个中心点
		# 分辨率 尺寸
		rowData["ControllPoint1"]= [1136*0.25,640/2]
		rowData["ControllPoint2"]= [1136*0.75,640/2]
		wSheel.write(nRow+3,title["ControllPoint1"],str(int(rowData["ControllPoint1"][0]))+","+str(int(rowData["ControllPoint1"][1])))
		wSheel.write(nRow+3,title["ControllPoint2"],str(int(rowData["ControllPoint2"][0]))+","+str(int(rowData["ControllPoint2"][1])))

	createBezierPoints(rSheel,wSheel,nRow)

# 计算贝塞尔曲线上的 点
def createBezierPoints(rSheel,wSheel,nRow):
	# 设置控制点，并限制范围
	global rowData,m_isHasData,bezierPointNum
	# 是否是自定义节点
	if rowData["Kind"]==2:
		print(str(nRow+3)+":自定义节点不计算贝塞尔曲线上的点！")
	else:
		# 是否直线
		if rowData["IsLine"]==1:
			rowData["Points"]=[]
			rowData["Points"].append(rowData["InPoint"])
			ip=rowData["InPoint"]
			op=rowData["OutPoint"]
			for k in range(bezierPointNum-2):
				rowData["Points"].append([(int(op[0])-int(ip[0]))/(bezierPointNum-1)*(k+1)+int(ip[0]),(int(op[1])-int(ip[1]))/(bezierPointNum-1)*(k+1)+int(ip[1])])
			rowData["Points"].append(rowData["OutPoint"])
		else:
			if rowData["CPNum"]==1:
				rowData["Points"]=getBezierPoints1(rowData["InPoint"],rowData["ControllPoint1"],rowData["OutPoint"],bezierPointNum)
			else:
				rowData["Points"]=getBezierPoints2(rowData["InPoint"],rowData["ControllPoint1"],rowData["ControllPoint2"],rowData["OutPoint"],bezierPointNum)
		str1=""
		for point in (rowData["Points"]):
			str1+="{"+str(int(point[0]))+","+str(int(point[1]))+"},"
		str1=str1[0:-1]
		wSheel.write(nRow+3,title["Points"],str1)

	# 计算距离
	createDistance(rSheel,wSheel,nRow)

# 计算二阶 贝塞尔曲线的点
def getBezierPoints1(sp,cp1,ep,count):
	ret=[]
	for k in range(count):
		t = k/float(count)
		x = math.pow(1-t,2)*int(sp[0])+2*(1-t)*t*int(cp1[0]) + t*t*int(ep[0])
		y = math.pow(1-t,2)*int(sp[1])+2*(1-t)*t*int(cp1[1]) + t*t*int(ep[1])
		ret.append([str(int(x)),str(int(y))])
	return ret

# 计算三阶 贝塞尔曲线的点
def getBezierPoints2(sp,cp1,cp2,ep,count):
	ret =[]
	for k in range(count):
		t = k/float(count)
		x = math.pow(1-t,3)*int(sp[0])+3*math.pow(1-t,2)*t*int(cp1[0]) + 3*t*t*(1-t)*int(cp2[0]) + t*t*t*int(ep[0])
		y = math.pow(1-t,3)*int(sp[1])+3*math.pow(1-t,2)*t*int(cp1[1]) + 3*t*t*(1-t)*int(cp2[1]) + t*t*t*int(ep[1])
		ret.append([str(int(x)),str(int(y))])
	return ret

# 计算距离
def createDistance(rSheel,wSheel,nRow):
	# 设置控制点，并限制范围
	global rowData,m_isHasData
	rowData["Distance"]=[]
	rowData["TotalDistance"]=0
	for k in range(len(rowData["Points"])):
		if k>0:
			lastP=rowData["Points"][k-1]
			curP=rowData["Points"][k]
			af=math.pow(int(curP[0])-int(lastP[0]),2)
			bf=math.pow(int(curP[1])-int(lastP[1]),2)
			c=math.floor(math.sqrt(af+bf))
			rowData["TotalDistance"]+=c
			rowData["Distance"].append(c)
	str2=""
	for k in (rowData["Distance"]):
		str2+=str(int(k))+","
	str2=str2[0:-1]
	wSheel.write(nRow+3,title["Distance"],str2)
	wSheel.write(nRow+3,title["TotalDistance"],rowData["TotalDistance"])

if __name__ == '__main__':

	if len(sys.argv)==2:
		import gitTool
		xls_path=sys.argv[1]
		print gitTool.pull(os.path.dirname(xls_path))

	rb = xlrd.open_workbook(xls_path)
	#通过sheet_by_index()获取的sheet没有write()方法
	rs = rb.sheet_by_index(0)
	wb = copy(rb)
	# 利用xlutils.copy函数，将xlrd.Book转为xlwt.Workbook，再用xlwt模块进行存储
	ws = wb.get_sheet(0)
	# 生成数据
	checkTableSize(rs)
	
	for k in range (count):
		createRowData(rs,ws,k)
	# 保存表格
	wb.save(xls_path)
	print "---解析完毕！---"
	if len(sys.argv)==2:
		print gitTool.commit(os.path.dirname(xls_path))





