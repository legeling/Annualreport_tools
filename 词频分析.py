'''
@Project ：PycharmProjects
@File    ：词频分析.py
@IDE     ：PyCharm
@Author  ：lingxiaotian
@Date    ：2023/5/30 14:34
'''
import os
import re
import xlwt
import jieba


def extract_keywords(filename, keywords):
    """
    从指定文件中提取关键词，并统计关键词出现次数。
    """
    keyword_counts = [0] * len(keywords)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用jieba库进行分词
        words = jieba.cut(content)
        words = [word for word in words if word.strip()]

        # 统计关键词出现次数
        for i, keyword in enumerate(keywords):
            keyword_counts[i] = words.count(keyword)
    except Exception as e:
        print(f"从文件中获取关键词失败！--- {filename}")
        print(str(e))

    return keyword_counts


def count_total_words(filename):
    """
    统计文本的总字数。
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        total_words = len(content)
    except Exception as e:
        print(f"统计文本总字数失败！--- {filename}")
        print(str(e))
        total_words = 0

    return total_words


def process_files(folder_path, keywords, result_name, flag, enable_word_count):
    """
    处理指定文件夹中的所有txt文件，提取关键词并统计词频，将结果存储到Excel表格中。
    """
    # 创建Excel工作簿
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('公众号凌小添')
    row = 0
    # 添加Excel表头
    worksheet.write(row, 0, '股票代码')
    worksheet.write(row, 1, '公司简称')
    worksheet.write(row, 2, '年份')
    if enable_word_count:
        worksheet.write(row, 3, '文本总字数')
        col_offset = 4
    else:
        col_offset = 3
    for i, keyword in enumerate(keywords):
        worksheet.write(row, i + col_offset, keyword)
    row += 1

    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.txt'):
                # 解析文件名，提取股票代码、公司简称和年份
                match = re.match(r'^(\d{6})_(.*?)_(\d{4})\.txt$', filename)
                if match:
                    stock_code = match.group(1)
                    company_name = match.group(2)
                    year = match.group(3)
                    # 处理年份筛选
                    if flag and year not in flag:
                        continue

                    file_path = os.path.join(root, filename)

                    # 提取关键词并统计词频
                    keyword_counts = extract_keywords(file_path, keywords)

                    # 统计文本总字数
                    total_words = count_total_words(file_path)

                    # 将结果写入Excel表格
                    worksheet.write(row, 0, stock_code)
                    worksheet.write(row, 1, company_name)
                    worksheet.write(row, 2, year)
                    if enable_word_count:
                        worksheet.write(row, 3, total_words)
                        col_offset = 4
                    else:
                        col_offset = 3
                    for i, count in enumerate(keyword_counts):
                        worksheet.write(row, i + col_offset, count)
                    row += 1
                else:
                    # 尝试第二种文件名格式：600519-贵州茅台2016年年度报告.txt
                    match = re.match(r'(\d{6})-(.*?)((19|20)\d{2})', filename)
                    if match:
                        stock_code = match.group(1)
                        company_name = match.group(2)
                        year = match.group(3)
                        # 处理年份筛选
                        if flag and year not in flag:
                            continue

                        file_path = os.path.join(root, filename)

                        # 提取关键词并统计词频
                        keyword_counts = extract_keywords(file_path, keywords)

                        # 统计文本总字数
                        total_words = count_total_words(file_path)

                        # 将结果写入Excel表格
                        worksheet.write(row, 0, stock_code)
                        worksheet.write(row, 1, company_name)
                        worksheet.write(row, 2, year)
                        if enable_word_count:
                            worksheet.write(row, 3, total_words)
                            col_offset = 4
                        else:
                            col_offset = 3
                        for i, count in enumerate(keyword_counts):
                            worksheet.write(row, i + col_offset, count)
                        row += 1
                    else:
                        # 无法解析文件名，跳过当前文件
                        print(f"无法解析文件名：{filename}")
                        continue

    # 保存Excel文件
    try:
        workbook.save(result_name)
    except Exception as e:
        print("保存到Excel失败")
        print(str(e))


if __name__ == '__main__':
    # 设置要提取的关键词列表，此处请自行修改！！！！
    # keywords = ['人工智能', '物联网', '财务共享', '利润', '数字化',  '云计算', '大数据', '互联网']
    keywords= [
        '人工智能', '商业智能', '图像理解',
        '投资决策辅助系统', '智能数据分', '大数据', '数据挖掘', '文本挖掘',
        '智能机器人', '机器学习', '深度学习','数据可视化', '异构数据',
        '语义搜索', '生物识别技术', '混合现实', '虚拟现实',
        '人脸识别', '语音识别', '身份验证', '自动驾驶', '自然语言处理',
        '企业数字化转型','云计算', '流计算',
        '图计算', '内存计算', '多方安全计算', '类脑计算', '綠色计算',
        '认知计算', '融合架构', '亿级并发', '区块链', '数字货币',
        '分布式计算', 'EB级存储', '物联网', '信息',
        '差分隐私技术', '智能金融合约', '物理系统', '移动互联网',
        '工业互联网', '移动互联', '互联网医疗', '电子商务', '移动支付',
        '第三方支付', 'NFC支付', '智能能源', 'B2B', 'B2C',
        'C2B', 'C2C', '020', '网联', '智能穿戴',
        '智慧农业', '智能交通', '智能医疗', '智能客服', '智能家居',
        '智能投顾', '智能文旅', '智能环保', '智能电网', '智能营销',
        '数字营销', '无人零售', '互联网金融', '数学金融', 'Fintech',
        '金融科技', '量化金融', '开放银行'
        ]

    # 要分析的年报所在的文件夹，尽量使用绝对路径，可以是多级目录
    folder_path = "/Users/文档/MyProgram/PycharmProjects/财报数据/年报文件"
    result_name = "词频分析结果【公众号凌小添】.xlsx"
    # 是否筛选特定年份，为列表模式，设置为 None 则不筛选
    # flag = None
    flag = ['2020','2021','2022']

    # 是否开启统计文本总字数
    enable_word_count = True
    # 处理文件夹中的所有txt文件，并将结果存储到Excel表格中
    try:
        process_files(folder_path, keywords, result_name, flag, enable_word_count)
    except Exception as e:
        print("文件处理失败！！")
        print(str(e))
    #！！！注意：如果程序运行无反应，多半是路径和txt文件命名问题！
    # 推荐文件名命名格式：“600519_贵州茅台_2019.txt”
    # 本代码亦支持如下格式：“600519-贵州茅台2019年年度报告.txt”