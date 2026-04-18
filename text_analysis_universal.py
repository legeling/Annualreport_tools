#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Annualreport_tools
@File    ：文本分析-universal.py
@IDE     ：PyCharm
@Author  ：lingxiaotian
@Date    ：2024/1/3 19:45
'''

from __future__ import annotations

import logging
import os
import re
from collections import Counter
from typing import List, Tuple

import jieba
import xlwt

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def extract_keywords(content: str, keywords: List[str]) -> Tuple[List[int], int]:
    """提取文本中的关键词并统计词频。

    Args:
        content: 文本内容
        keywords: 关键词列表

    Returns:
        关键词计数列表和总词数的元组
    """
    keyword_counts = [0] * len(keywords)
    total_words = 0

    try:
        # 使用jieba库进行分词
        words = [word for word in jieba.cut(content) if word.strip()]
        # 使用正则表达式去除标点符号、数字、英文、空格等非中文字符
        content_non = re.sub(r'[^\u4e00-\u9fa5]', '', content)
        words_non = [word for word in jieba.cut(content_non) if word.strip()]

        # 预聚合词频，避免 repeated O(n) 扫描
        word_counter = Counter(words)
        for i, keyword in enumerate(keywords):
            keyword_counts[i] = word_counter.get(keyword, 0)

        total_words = len(words_non)

    except Exception as e:
        logging.error(f"提取关键词失败: {e}")

    return keyword_counts, total_words
def process_files(folder_path: str, keywords: List[str]) -> None:
    """处理文件夹中的所有txt文件，统计关键词并保存到Excel。

    Args:
        folder_path: 文件夹路径
        keywords: 关键词列表
    """
    try:
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            logging.error(f"文件夹不存在: {folder_path}")
            return

        # 将关键词一次性添加到jieba自定义词典
        for word in keywords:
            jieba.add_word(word)
        logging.info(f"已加载 {len(keywords)} 个关键词到jieba词典")

        # 创建Excel工作簿
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('关键词统计')
        row = 0

        # 添加Excel表头
        worksheet.write(row, 0, '文件名')
        worksheet.write(row, 1, '总词数')
        for i, keyword in enumerate(keywords):
            worksheet.write(row, i + 2, keyword)
        row += 1

        total_files = 0  # 记录处理的文件数

        # 遍历文件夹中的所有文件
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith('.txt'):
                total_files += 1
                file_path = os.path.join(folder_path, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取关键词并统计词频和总词数
                    keyword_counts, total_words = extract_keywords(content, keywords)

                    # 将结果写入Excel表格
                    worksheet.write(row, 0, os.path.splitext(filename)[0])  # 使用文件名去除后缀
                    worksheet.write(row, 1, total_words)  # 总词数
                    for i, count in enumerate(keyword_counts):
                        worksheet.write(row, i + 2, count)
                    row += 1

                    logging.info(f"已处理: {filename}")

                except OSError as e:
                    logging.error(f"读取文件失败: {file_path} - {e}")
                except Exception as e:
                    logging.error(f"处理文件失败: {file_path} - {e}")

        if total_files == 0:
            logging.warning(f"文件夹内没有找到任何txt文件，请检查路径：{folder_path}")
            return

        # 保存Excel文件
        try:
            excel_file = os.path.join(folder_path, '关键词统计结果.xls')
            workbook.save(excel_file)
            logging.info(f"Excel文件保存成功: {excel_file}")
            print(f"\n✅ 处理完成！共处理 {total_files} 个文件")
            print(f"📊 结果已保存到: {excel_file}")
        except Exception as e:
            logging.error(f"保存Excel文件失败: {e}")

    except Exception as e:
        logging.error(f"处理文件夹失败: {folder_path} - {e}")



if __name__ == '__main__':
    # 设置要提取的关键词列表（可根据需要修改）
    keywords = ['人工智能', '数字资产', '数据', '资产', '智能数据分', '大数据', '数据挖掘', '文本挖掘']

    # 输入文件夹路径，可通过环境变量 UNIVERSAL_ANALYSIS_DIR 覆盖
    folder_path = os.getenv("UNIVERSAL_ANALYSIS_DIR", "年报文件/2024/txt年报")

    # 处理文件夹中的所有txt文件，并将结果存储到Excel表格中
    logging.info("开始处理文件...")
    process_files(folder_path, keywords)
    logging.info("处理完成")
