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

def process_files(folder_path, keywords):
    """
    处理指定文件夹中的所有txt文件，提取关键词并统计词频，将结果存储到Excel表格中。
    """
    # 创建Excel工作簿
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('Sheet1')
    row = 0
    # 添加Excel表头
    worksheet.write(row, 0, '股票代码')
    worksheet.write(row, 1, '公司简称')
    worksheet.write(row, 2, '年份')
    for i, keyword in enumerate(keywords):
        worksheet.write(row, i + 3, keyword)
    row += 1

    # 获取文件总数
    total_files = len([filename for filename in os.listdir(folder_path) if filename.endswith('.txt')])
    processed_files = 0

    # 遍历文件夹中的所有txt文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            # 解析文件名，提取股票代码、公司简称和年份
            match = re.match(r'^(\d{6})_(.*?)_(\d{4})\.txt$', filename)
            if match:
                stock_code = match.group(1)
                company_name = match.group(2)
                year = match.group(3)

                # 提取关键词并统计词频
                keyword_counts = extract_keywords(os.path.join(folder_path, filename), keywords)

                # 将结果写入Excel表格
                worksheet.write(row, 0, stock_code)
                worksheet.write(row, 1, company_name)
                worksheet.write(row, 2, year)
                for i, count in enumerate(keyword_counts):
                    worksheet.write(row, i + 3, count)
                row += 1

                # 更新进度
                processed_files += 1
                progress = (processed_files / total_files) * 100
                print(f"\r当前进度: {progress:.2f}%", end='', flush=True)

    # 保存Excel文件
    try:
        workbook.save('result20200.xls')
    except Exception as e:
        print("Failed to save Excel file.")
        print(str(e))

if __name__ == '__main__':
    # 设置要提取的关键词列表
    keywords = ['财务', '共享服务', '财务共享','利润','数字化','培训','云计算','大数据','互联网']

    # 处理文件夹中的所有txt文件，并将结果存储到Excel表格中
    try:
        process_files('txt年报2020', keywords)
    except Exception as e:
        print("文件处理失败！！")
        print(str(e))