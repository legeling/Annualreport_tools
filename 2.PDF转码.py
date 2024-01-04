'''
@Project ：PycharmProjects
@File    ：年报批量下载.py
@IDE     ：PyCharm
@Author  ：lingxiaotian
@Date    ：2023/5/30 11:39
'''

import pandas as pd
import requests
import os
import multiprocessing
import pdfplumber
import logging
import re

#日志配置文件
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#下载模块
def download_pdf(pdf_url, pdf_file_path):
    try:
        with requests.get(pdf_url, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(pdf_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except requests.exceptions.RequestException as e:
        logging.error(f"下载PDF文件失败：{e}")
        return False
    else:
        return True

#文件转换
def convert(code, name, year, pdf_url, pdf_dir, txt_dir, flag_pdf):
    pdf_file_path = os.path.join(pdf_dir, re.sub(r'[\\/:*?"<>|]', '',f"{code:06}_{name}_{year}.pdf"))
    txt_file_path = os.path.join(txt_dir, re.sub(r'[\\/:*?"<>|]', '', f"{code:06}_{name}_{year}.txt"))

    try:
        # 下载PDF文件
        if not os.path.exists(pdf_file_path):
            retry_count = 3
            while retry_count > 0:
                if download_pdf(pdf_url, pdf_file_path):
                    break
                else:
                    retry_count -= 1
            if retry_count == 0:
                logging.error(f"下载失败：{pdf_url}")
                return

        # 转换PDF文件为TXT文件
        with pdfplumber.open(pdf_file_path) as pdf:
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                for page in pdf.pages:
                    text = page.extract_text()
                    f.write(text)

        logging.info(f"{txt_file_path} 已保存.")

    except Exception as e:
        logging.error(f"处理 {code:06}_{name}_{year}时出错： {e}")
    else:
        # 删除已转换的PDF文件，以节省空间
        if flag_pdf:
            os.remove(pdf_file_path)
            logging.info(f"{pdf_file_path} 已被删除.")



def main(file_name,pdf_dir,txt_dir,flag_pdf):
    print("程序开始运行，请耐心等待……")
    # 读取Excel文件
    try:
        df = pd.read_excel(file_name)
    except Exception as e:
        logging.error(f"读取失败，请检查路径是否设置正确，建议输入绝对路径 {e}")
        return
    try:
        os.makedirs(pdf_dir, exist_ok=True)
        os.makedirs(txt_dir, exist_ok=True)
    except Exception as e:
        logging.error(f"创建文件夹失败！请检查文件夹是否为只读！ {e}")
        return

    # 读取文件内容并存储为字典
    content_dict = ((row['公司代码'], row['公司简称'], row['年份'], row['年报链接']) for _, row in df.iterrows())

    # 多进程下载PDF并转为TXT文件
    with multiprocessing.Pool() as pool:
        for code, name, year, pdf_url in content_dict:
            txt_file_name = f"{code:06}_{name}_{year}.txt"
            txt_file_path = os.path.join(txt_dir, txt_file_name)
            if os.path.exists(txt_file_path):
                logging.info(f"{txt_file_name} 已存在，跳过.")
            else:
                pool.apply_async(convert, args=(code, name, year, pdf_url, pdf_dir, txt_dir, flag_pdf))

        pool.close()
        pool.join()


if __name__ == '__main__':
    # 是否删除pdf文件，True为是，False为否
    flag_pdf = True
    # 是否批量处理多个年份，True为是，False为否
    Flag = False
    if Flag:
        #批量下载并转换年份区间
        for year in range(2004,2022):
            # ===========Excel表格路径，建议使用绝对路径，务必请自行修改！！！！！！！===========
            file_name = f"/Users/文档/MyProgram/PycharmProjects/财报数据/年报/年报链接_{year}【公众号：凌小添】.xlsx"
            # 创建存储文件的文件夹路径，如有需要请修改
            pdf_dir = f'年报文件/{year}/pdf年报'
            txt_dir = f'年报文件/{year}/txt年报'
            main(file_name,pdf_dir,txt_dir,flag_pdf)
            print(f"{year}年年报处理完毕，若报错，请检查后重新运行")
    else:
        #处理单独年份：
        #特定年份的excel表格，请务必修改。
        year = 2019
        file_name = f"/Users/wangjialong/PycharmProjects/Annualreport_tools/年报链接_{year}【公众号：凌小添】.xlsx"
        pdf_dir = f'年报文件/{year}/pdf年报'
        txt_dir = f'年报文件/{year}/txt年报'
        main(file_name, pdf_dir, txt_dir, flag_pdf)
        print(f"{year}年年报处理完毕，若报错，请检查后重新运行")
