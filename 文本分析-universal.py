#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Annualreport_tools 
@File    ：文本分析-universal.py
@IDE     ：PyCharm 
@Author  ：lingxiaotian
@Date    ：2024/1/3 19:45 
'''
import os
import re
import xlwt
import jieba


def extract_keywords(content, keywords):
    keyword_counts = [0] * len(keywords)
    total_words = 0

    try:
        # 将关键词添加到自定义词典
        for word in keywords:
            jieba.add_word(word)

        # 使用jieba库进行分词
        words = jieba.cut(content)
        words = [word for word in words if word.strip()]

        # 统计关键词出现次数
        for i, keyword in enumerate(keywords):
            keyword_counts[i] = words.count(keyword)

        total_words = len(words)

    except Exception as e:
        print("从文件中获取关键词失败")
        print(str(e))

    return keyword_counts, total_words
def process_files(folder_path, keywords):
    try:
        # 创建Excel工作簿
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('关键词统计')
        row = 0
        # 添加Excel表头
        worksheet.write(row, 0, '文件名')
        worksheet.write(row, 1, '总字数')
        for i, keyword in enumerate(keywords):
            worksheet.write(row, i + 2, keyword)
        row += 1

        total_files = 0  # 记录处理的文件数

        # 遍历文件夹中的所有文件
        for filename in os.listdir(folder_path):
            if filename.endswith('.txt'):
                total_files += 1
                file_path = os.path.join(folder_path, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取关键词并统计词频和总字数
                    keyword_counts, total_words = extract_keywords(content, keywords)

                    # 将结果写入Excel表格
                    worksheet.write(row, 0, os.path.splitext(filename)[0])  # 使用文件名去除后缀
                    worksheet.write(row, 1, total_words)  # 总字数
                    for i, count in enumerate(keyword_counts):
                        worksheet.write(row, i + 2, count)
                    row += 1

                except Exception as e:
                    print(f"处理文件失败: {file_path}")
                    print(str(e))

        if total_files == 0:
            print(f"文件夹内没有找到任何txt文件，请检查路径：{folder_path}")
            return

        # 保存Excel文件
        try:
            excel_file = os.path.join(folder_path, '关键词统计结果.xlsx')
            workbook.save(excel_file)
            print(f"\nExcel文件保存成功，请到下面路径查看: {excel_file}")
        except Exception as e:
            print("\n保存Excel文件失败。")
            print(str(e))

    except Exception as e:
        print(f"处理文件夹失败: {folder_path}")
        print(str(e))



if __name__ == '__main__':
    # 设置要提取的关键词列表
    keywords = ['人工智能', '数字资产', '数据', '资产', '智能数据分', '大数据', '数据挖掘', '文本挖掘']
    # 输入文件夹路径
    folder_path = "D:/数据集/上市公司爬虫/年报文件"
    # 处理文件夹中的所有txt文件，并将结果存储到Excel表格中
    process_files(folder_path, keywords)
