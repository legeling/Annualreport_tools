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
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

        session = requests.Session()
        session.headers.update(headers)

        # 请求PDF文件
        response = session.get(pdf_url, stream=True, timeout=15)
        # 检查HTTP状态码
        if response.status_code == 403:
            logging.error(f"❌ 403 Forbidden: 服务器禁止访问 {pdf_url}")
            return False
        elif response.status_code != 200:
            logging.error(f"❌ 请求失败: {response.status_code} - {response.text[:500]}")
            return False
        content_type = response.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower():
            logging.error(f"❌ 服务器返回的不是 PDF: {content_type}")
            return False
        # 写入PDF文件
        with open(pdf_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        # 验证文件是否为PDF
        if os.path.exists(pdf_file_path) and os.path.getsize(pdf_file_path) > 0:
            with open(pdf_file_path, "rb") as f:
                first_bytes = f.read(5)
                if not first_bytes.startswith(b"%PDF"):
                    logging.error(f"❌ 下载的文件不是 PDF！可能是 HTML 错误页面，请检查 {pdf_file_path}")
                    return False
        else:
            logging.error(f"❌ 下载失败，文件大小为 0 KB: {pdf_file_path}")
            return False
        logging.info(f"✅ PDF 下载成功: {pdf_file_path}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ 下载 PDF 文件失败: {e}")
        return False

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



def main(file_name,pdf_dir,txt_dir,flag_pdf,year):
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
    content_dict = ((row['公司代码'], row['公司简称'], row['年份'], row['年报链接']) for _, row in df.iterrows() if str(row['年份']) == str(year))

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
    Flag = True
    if Flag:
        #批量下载并转换年份区间
        for year in range(2013,2023):
            # ===========Excel表格路径，建议使用绝对路径，请自行修改！！！！！！！===========
            # 2024年02月14日更新后，此处只需要填写总表的路径，请于网盘或者github中获取总表
            file_name = f"年报链接截至2023.xlsx"
            # 创建存储文件的文件夹路径，如有需要请修改
            pdf_dir = f'年报文件/{year}/pdf年报'
            txt_dir = f'年报文件/{year}/txt年报'
            main(file_name,pdf_dir,txt_dir,flag_pdf,year)
            print(f"{year}年年报处理完毕，若报错，请检查后重新运行")
    else:
        #处理单独年份：
        #特定年份的excel表格，请务必修改。
        year = 2018
        file_name = f"年报链接2002-2023.xlsx"
        pdf_dir = f'年报文件/{year}/pdf年报'
        txt_dir = f'年报文件/{year}/txt年报'
        main(file_name, pdf_dir, txt_dir, flag_pdf,year)
        print(f"{year}年年报处理完毕，若报错，请检查后重新运行")
