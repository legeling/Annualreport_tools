import pandas as pd
import requests
import os
import multiprocessing
import pdfplumber
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def convert(code, name, year, pdf_url, pdf_dir, txt_dir):
    pdf_file_path = os.path.join(pdf_dir, f"{code}_{name}_{year}.pdf")
    txt_file_path = os.path.join(txt_dir, re.sub(r'[\\/:*?"<>|]', '', f"{code}_{name}_{year}.txt"))

    try:
        # 下载PDF文件
        if not os.path.exists(pdf_file_path):
            with requests.get(pdf_url, stream=True) as r:
                r.raise_for_status()
                with open(pdf_file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        # 转换PDF文件为TXT文件
        with pdfplumber.open(pdf_file_path) as pdf:
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                for page in pdf.pages:
                    text = page.extract_text()
                    f.write(text)

        logging.info(f"{txt_file_path} 已保存.")

    except Exception as e:
        logging.error(f"Error occurred while processing {code}_{name}_{year}. {e}")

    else:
        # 删除已转换的PDF文件，以节省空间
        os.remove(pdf_file_path)
        logging.info(f"{pdf_file_path} has been deleted.")


def main():
    # 读取Excel文件
    try:
        df = pd.read_excel('年报_2015.xlsx')
    except Exception as e:
        logging.error(f"读取失败！！ {e}")
        return

    # 创建存储文件的文件夹
    pdf_dir = 'pdf年报'
    txt_dir = 'txt年报'
    try:
        os.makedirs(pdf_dir, exist_ok=True)
        os.makedirs(txt_dir, exist_ok=True)
    except Exception as e:
        logging.error(f"创建文件夹失败！请检查权限！ {e}")
        return

    # 读取文件内容并存储为字典
    content_dict = ((row['公司代码'], row['公司简称'], row['年份'], row['年报链接']) for _, row in df.iterrows())

    # 多进程下载PDF并转为TXT文件
    with multiprocessing.Pool() as pool:
        for code, name, year, pdf_url in content_dict:
            txt_file_name = f"{code}_{name}_{year}.txt"
            txt_file_path = os.path.join(txt_dir, txt_file_name)
            if os.path.exists(txt_file_path):
                logging.info(f"{txt_file_name} 已存在，跳过.")
            else:
                pool.apply_async(convert, args=(code, name, year, pdf_url, pdf_dir, txt_dir))

        pool.close()
        pool.join()


if __name__ == '__main__':
    main()