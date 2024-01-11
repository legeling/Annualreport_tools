#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：PycharmProjects
@File    ：巨潮资讯年报2.0.py
@IDE     ：PyCharm
@Author  ：lingxiaotian
@Date    ：2023/5/20 12:38
'''

import requests
import re
import openpyxl
import time


GZH = "【公众号：凌小添】"
def get_report(page_num,date):
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Content-Length": "195",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.cninfo.com.cn",
        "Origin": "http://www.cninfo.com.cn",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&checkedCategory=category_ndbg_szsh",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42",
        "X-Requested-With": "XMLHttpRequest"
    }
    '''
    参数列表
     plate: sz;sh, 表示沪深两市
     seDate：查询时间
    '''
    data = {
        "pageNum": page_num,
        "pageSize": 30,
        "column": "szse",
        "tabName": "fulltext",
        "plate": "sz;sh",
        "searchkey": "",
        "secid": "",
        "category": "category_ndbg_szsh",
        "trade": "",
        "seDate": date,
        "sortName": "code",
        "sortType": "asc",
        "isHLtitle": "false"
    }
    response = requests.post(url, data=data, headers=headers)
    return response

# 发送HTTP请求并获取响应
def downlaod_report(date):
    global counter
    all_results = []
    page_num = 1
    response_test = get_report(page_num,date)
    data_test = response_test.json()
    total_pages = data_test["totalpages"]
    max_retries = 3 #最大重试次数
    retry_count = 0 #当前重试次数
    while page_num <= total_pages:
        response = None

        # 重试机制
        while retry_count <= max_retries:
            # 发送请求
            try:
                # response = requests.post(url, data=data,headers=headers)
                response = get_report(page_num,date)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"出现错误！: {e}")
                print(f"5秒后重试...")
                time.sleep(5)
                retry_count += 1

        if retry_count > max_retries:
            print(f"{max_retries} 次重试后均失败. 跳过第 {page_num}页.")
            page_num += 1
            retry_count = 0
            continue
        else:
            # 解析数据
            try:
                data = response.json()

                per = (counter/sum)
                if  per <1:
                    print(f"\r当前年份下载进度 {per*100:.2f} %",end='')
                else:
                    print(f"\r下载完成，正在保存……", end='')
                # 尝试解析公告数据，如果解析失败则重试
                retry_count = 0
                while True:
                    try:
                        if data["announcements"] is None:
                            raise Exception("公告数据为空")
                        else:
                            all_results.extend(data["announcements"])
                        break
                    except (TypeError, KeyError) as e:
                        print(f"解析公告数据失败: {e}")
                        print(f"5秒后重试...")
                        time.sleep(5)
                        retry_count += 1
                        if retry_count > max_retries:
                            raise Exception("达到最大重试次数，跳过此页")
                        continue
                page_num += 1
                counter +=1
            except (ValueError, KeyError) as e:
                print(f"解析响应数据失败: {e}")
                print(f"5秒后重试...")
                time.sleep(5)
                retry_count += 1
                if retry_count > max_retries:
                    raise Exception("达到最大重试次数，跳过此页")
                continue
    return all_results


def main(year):
    # 计数器
    global sum
    date_count = f"{year}-01-01~{year}-04-30"
    response = get_report(1,date_count)

    data = response.json()
    sum = data["totalpages"]

    year = year+1
    all_results = []
    time_segments = [
        f"{year}-01-01~{year}-04-01",
        f"{year}-04-02~{year}-04-15",
        f"{year}-04-16~{year}-04-22",
        f"{year}-04-23~{year}-04-26",
        f"{year}-04-27~{year}-04-28",
        f"{year}-04-29~{year}-04-30",
        f"{year}-05-01~{year}-07-31",
        f"{year}-08-01~{year}-10-31",
        f"{year}-11-01~{year}-11-30",
        f"{year}-12-01~{year}-12-31"
    ]
    for i in time_segments:
        results = downlaod_report(i)
        all_results.extend(results)


    # 创建Excel文件并添加表头
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "公众号 凌小添"
    worksheet.append(["公司代码", "公司简称", "标题", "年份", "年报链接"])

    # 解析搜索结果并添加到Excel表格中
    for item in all_results:
        company_code = item["secCode"]
        company_name = item["secName"]
        title = item["announcementTitle"].strip()
        # 剔除不需要的样式和特殊符号，并重新组合标题
        title = re.sub(r"<.*?>", "", title)
        title = title.replace("：", "")
        title = f"《{title}》"

        adjunct_url = item["adjunctUrl"]
        year = re.search(r"\d{4}", title)
        if year:
            year = year.group()
        else:
            year = setYear
        time = f"{year}"
        announcement_url = f"http://static.cninfo.com.cn/{adjunct_url}"

        # 检查标题是否包含排除关键词
        exclude_flag = False
        for keyword in exclude_keywords:
            if keyword in title:
                exclude_flag = True
                break

        # 如果标题不包含排除关键词，则将搜索结果添加到Excel表格中
        if not exclude_flag:
            worksheet.append([company_code, company_name, title, time, announcement_url])
    #注意：年报默认保存在代码同级目录下，如需调整请修改此处的路径，请自行创建文件夹并填入路径
    workbook.save(f"年报链接_{setYear}{GZH}.xlsx")


if __name__ == '__main__':
    # 全局变量
    # 排除列表可以加入'更正后','修订版'来规避数据重复或公司发布之前年份的年报修订版等问题，
    exclude_keywords = ['英文', '摘要','已取消','公告']
    global counter
    global sum
    counter = 1  # 计数器
    setYear = 2011 #设置下载年份
    Flag = 0  #是否开启批量下载模式
    if Flag:
        for setYear in range(2004,2022):
            counter = 1  # 计数器
            main(setYear)
            print(f"----{setYear}年下载完成")
    else:
        main(setYear)
        print(f"----{setYear}年下载完成")

