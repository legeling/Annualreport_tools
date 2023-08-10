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
    从指定文件中提取关键词，并统计关键词出现次数和总字数。
    """
    keyword_counts = [0] * len(keywords)
    total_words = 0  # 统计总字数

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用jieba库进行分词
        words = jieba.cut(content)
        words = [word for word in words if word.strip()]

        # 统计关键词出现次数
        for i, keyword in enumerate(keywords):
            keyword_counts[i] = words.count(keyword)

        total_words = len(words)  # 统计总字数
    except FileNotFoundError:
        print(f"文件不存在: {filename}")
    except PermissionError:
        print(f"没有访问权限: {filename}")
    except Exception as e:
        print(f"从文件中获取关键词失败: {filename}")
        print(str(e))

    return keyword_counts, total_words


def count_txt_files(folder_path, start_year=None, end_year=None):
    """
    统计指定文件夹及其子文件夹中符合年份要求的所有txt文件数量。
    """
    total_files = 0
    processed_files = 0

    try:
        # 遍历文件夹中的所有文件和子文件夹
        for root, dirs, files in os.walk(folder_path):
            # 根据文件夹路径获取年份信息
            match = re.match(r'.*([12]\d{3}).*', os.path.basename(root))
            if match:
                year = match.group(1)
                if (start_year is not None and int(year) < int(start_year)) or (end_year is not None and int(year) > int(end_year)):
                    # 如果年份不符合要求，则移除该文件夹，防止遍历其中的文件
                    dirs[:] = []
                    continue

            # 遍历当前文件夹中的所有txt文件
            for filename in files:
                if filename.endswith('.txt'):
                    total_files += 1
    except FileNotFoundError:
        print(f"文件夹不存在: {folder_path}")
    except PermissionError:
        print(f"没有访问权限: {folder_path}")
    except Exception as e:
        print(f"统计文件数量失败: {folder_path}")
        print(str(e))

    return total_files

def process_files(folder_path, keywords, start_year=None, end_year=None):
    """
    处理指定文件夹及其子文件夹中的所有txt文件，提取关键词并统计词频和总字数，将结果存储到Excel表格中。
    """
    try:
        # 创建Excel工作簿
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('公众号凌小添')
        row = 0
        # 添加Excel表头
        worksheet.write(row, 0, '股票代码')
        worksheet.write(row, 1, '公司简称')
        worksheet.write(row, 2, '年份')
        worksheet.write(row, 3, '总字数')  # 添加总字数列
        for i, keyword in enumerate(keywords):
            worksheet.write(row, i + 4, keyword)  # 调整关键词列的索引
        row += 1

        total_files = count_txt_files(folder_path, start_year, end_year)
        processed_files = 0

        try:
            # 遍历文件夹中的所有文件和子文件夹
            for root, dirs, files in os.walk(folder_path):
                # 根据文件夹路径获取年份信息
                match = re.match(r'.*([12]\d{3}).*', os.path.basename(root))
                if match:
                    year = match.group(1)
                    if (start_year is not None and int(year) < int(start_year)) or (end_year is not None and int(year) > int(end_year)):
                        # 如果年份不符合要求，则移除该文件夹，防止遍历其中的文件
                        dirs[:] = []
                        continue

                # 遍历当前文件夹中的所有txt文件
                for filename in files:
                    if filename.endswith('.txt'):
                        # 解析文件名，提取股票代码、公司简称和年份
                        match = re.match(r'^(\d{6})_(.*?)_(\d{4})\.txt$', filename)
                        if match:
                            stock_code = match.group(1)
                            company_name = match.group(2)

                            # 提取关键词并统计词频和总字数
                            keyword_counts, total_words = extract_keywords(os.path.join(root, filename), keywords)

                            # 将结果写入Excel表格
                            worksheet.write(row, 0, stock_code)
                            worksheet.write(row, 1, company_name)
                            worksheet.write(row, 2, year)
                            worksheet.write(row, 3, total_words)  # 写入总字数
                            for i, count in enumerate(keyword_counts):
                                worksheet.write(row, i + 4, count)  # 调整关键词列的索引
                            row += 1

                            # 更新进度
                            processed_files += 1
                            progress = (processed_files / total_files) * 100
                            print(f"\r当前进度: {progress:.2f}%", end='', flush=True)

                            # 每处理指定数目个数据就保存一次Excel文件
                            if processed_files % size == 0:
                                workbook.save(name)
        except FileNotFoundError:
            print(f"文件夹不存在: {folder_path}")
        except PermissionError:
            print(f"没有访问权限: {folder_path}")
        except Exception as e:
            print(f"处理文件失败: {folder_path}")
            print(str(e))

        # 保存Excel文件
        try:
            workbook.save(name)
            print("\nExcel文件保存成功！")
        except FileNotFoundError:
            print(f"保存Excel文件失败: 文件夹不存在")
        except PermissionError:
            print(f"保存Excel文件失败: 没有访问权限")
        except Exception as e:
            print("\n保存Excel文件失败。")
            print(str(e))
    except FileNotFoundError:
        print(f"文件夹不存在: {folder_path}")
    except PermissionError:
        print(f"没有访问权限: {folder_path}")
    except Exception as e:
        print("处理文件失败！")
        print(str(e))


if __name__ == '__main__':
    # 设置要提取的关键词列表
    keywords = [
        '人工智能', '商业智能', '图像理解',
        '投资决策辅助系统', '智能数据分', '大数据', '数据挖掘', '文本挖掘',
        '智能机器人', '机器学习', '深度学习', '数据可视化', '异构数据',
        '语义搜索', '生物识别技术', '混合现实', '虚拟现实',
        '人脸识别', '语音识别', '身份验证', '自动驾驶', '自然语言处理',
        '企业数字化转型', '云计算', '流计算',
        '图计算', '内存计算', '多方安全计算', '类脑计算', '綠色计算',
        '认知计算', '融合架构', '亿级并发', '区块链', '数字货币',
        '分布式计算', 'EB级存储', '物联网', '信息物理系统',
        '差分隐私技术', '智能金融合约', '移动互联网',
        '工业互联网', '移动互联', '互联网医疗', '电子商务', '移动支付',
        '第三方支付', 'NFC支付', '智能能源', 'B2B', 'B2C',
        'C2B', 'C2C', '020', '网联', '智能穿戴',
        '智慧农业', '智能交通', '智能医疗', '智能客服', '智能家居',
        '智能投顾', '智能文旅', '智能环保', '智能电网', '智能营销',
        '数字营销', '无人零售', '互联网金融', '数学金融', 'Fintech',
        '金融科技', '量化金融', '开放银行'
    ]
    # !!!!!注意，请务必将各个年份的年报 文件夹 放到一个大的 文件夹 中，并填入此文件夹的内容，请不要存放其他非年报文件。
    # 输入根文件夹路径，建议输入绝对路径，如“D:/数据集/上市公司爬虫/年报文件夹”
    root_folder = "D:/数据集/上市公司爬虫/年报文件"
    # 输入年份区间
    start_year = "2010"
    end_year = "2022"

    # 输入处理结果的文件名
    name = "词频分析结果.xlsx"
    # 暂存数目大小，默认为100，尽量别改太小，否则IO压力很大。
    size = 100
    # 处理文件夹中的所有txt文件，并将结果存储到Excel表格中
    try:
        if start_year > end_year:
            print("起始年份不能大于中止年份！！！！！")
        else:
            process_files(root_folder, keywords, start_year, end_year)
    except Exception as e:
        print("文件处理失败！！")
        print(str(e))

    #！！！注意：如果程序运行无反应，多半是路径和txt文件命名问题！
    # 推荐文件名命名格式：“600519_贵州茅台_2019.txt”
