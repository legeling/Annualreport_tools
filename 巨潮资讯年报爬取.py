#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Spider 
@File    ：巨潮资讯年报爬取.py
@IDE     ：PyCharm 
@Author  ：lingxiaotian
@Date    ：2023/3/23 19:16 
'''

import requests
import re
import openpyxl
import time


# 设置搜索参数
search_key = "年报"
url_template = "http://www.cninfo.com.cn/new/fulltextSearch/full?searchkey={}&sdate=2022-01-01&edate=2022-07-01&isfulltext=false&sortName=pubdate&sortType=desc&pageNum={}&type=shj"
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
# 定义需要剔除的标题关键词
exclude_keywords = ["摘要", "英文版", "披露", "风险提示", "督导","反馈","回复","业绩","说明会","意见","审核","独立董事","半年","已取消","补充","提示性","制度","规程","审计","回函","公告","声明","说明","受托","问询函","核查","回复","函","交流","可持续","跟踪"]

# 发送HTTP请求并获取响应
all_results = []
page_num =1
total_pages = 1256
max_retries = 2
retry_count = 0

while page_num <= total_pages:
    url = url_template.format(search_key, page_num)
    response = None

    # 重试机制
    while retry_count <= max_retries:
        # 发送请求
        try:
            response = requests.get(url,headers=headers)
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

    # 解析数据
    try:
        data = response.json()
        total_pages = 1256
        print(f"正在下载第 {page_num}/{total_pages} 页")
        # 尝试解析公告数据，如果解析失败则重试
        retry_count = 0
        while True:
            try:
                if data["announcements"] is None:
                    raise Exception("公告数据为空")
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
    except (ValueError, KeyError) as e:
        print(f"解析响应数据失败: {e}")
        print(f"5秒后重试...")
        time.sleep(5)
        retry_count += 1
        if retry_count > max_retries:
            raise Exception("达到最大重试次数，跳过此页")
        continue

# 创建Excel文件并添加表头
workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.title = "Search Results"
worksheet.append(["公司代码", "公司简称", "标题", "发布日期", "年报链接"])


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
    year = re.search(r"\d{4}", adjunct_url).group()
    publish_time = f"{year}"
    announcement_url = f"http://static.cninfo.com.cn/{adjunct_url}"

    # 检查标题是否包含排除关键词
    exclude_flag = False
    for keyword in exclude_keywords:
        if keyword in title:
            exclude_flag = True
            break

    # 如果标题不包含排除关键词，则将搜索结果添加到Excel表格中
    if not exclude_flag:
        worksheet.append([company_code, company_name, title, publish_time, announcement_url])

# 保存Excel文件
workbook.save(f"年报_2021.xlsx")