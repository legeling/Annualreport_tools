'''
@Project ：PycharmProjects
@File    ：年报批量下载.py
@IDE     ：PyCharm
@Author  ：lingxiaotian
@Date    ：2023/5/30 11:39
@LastEditTime: 2025/11/21 14:10
'''

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import pdfplumber
import requests

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@dataclass(frozen=True)
class ConverterConfig:
    """PDF批量下载转换配置类。"""
    excel_file: str  # Excel表格路径
    pdf_dir: str  # PDF存储目录
    txt_dir: str  # TXT存储目录
    target_year: int  # 目标年份
    delete_pdf: bool = False  # 是否删除转换后的PDF
    max_retries: int = 3  # 下载最大重试次数
    timeout: int = 15  # 请求超时时间（秒）
    chunk_size: int = 8192  # 下载块大小
    processes: Optional[int] = None  # 进程数，None表示自动


class PDFDownloader:
    """PDF下载器类。"""
    
    HEADERS = {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    
    def __init__(self, timeout: int = 15, chunk_size: int = 8192) -> None:
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def download(self, pdf_url: str, pdf_file_path: str) -> bool:
        """下载PDF文件并验证完整性。
        
        Args:
            pdf_url: PDF下载链接
            pdf_file_path: 保存路径
            
        Returns:
            下载是否成功
        """
        try:
            # 请求PDF文件
            response = self.session.get(pdf_url, stream=True, timeout=self.timeout)
            
            # 检查HTTP状态码
            if response.status_code == 403:
                logging.error(f"403 Forbidden: 服务器禁止访问 {pdf_url}")
                return False
            elif response.status_code != 200:
                logging.error(f"请求失败: {response.status_code} - {response.text[:500]}")
                return False
            
            # 验证Content-Type
            content_type = response.headers.get("Content-Type", "")
            if "pdf" not in content_type.lower():
                logging.error(f"服务器返回的不是 PDF: {content_type}")
                return False
            
            # 写入PDF文件
            with open(pdf_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件完整性
            if not self._verify_pdf(pdf_file_path):
                return False
            
            logging.info(f"PDF 下载成功: {pdf_file_path}")
            return True
            
        except requests.exceptions.Timeout:
            logging.error(f"下载超时: {pdf_url}")
            return False
        except requests.exceptions.RequestException as e:
            logging.error(f"下载 PDF 文件失败: {e}")
            return False
        except OSError as e:
            logging.error(f"文件写入失败: {e}")
            return False
    
    @staticmethod
    def _verify_pdf(pdf_file_path: str) -> bool:
        """验证PDF文件完整性。"""
        if not os.path.exists(pdf_file_path):
            logging.error(f"文件不存在: {pdf_file_path}")
            return False
        
        if os.path.getsize(pdf_file_path) == 0:
            logging.error(f"下载失败，文件大小为 0 KB: {pdf_file_path}")
            return False
        
        try:
            with open(pdf_file_path, "rb") as f:
                first_bytes = f.read(5)
                if not first_bytes.startswith(b"%PDF"):
                    logging.error(f"下载的文件不是有效的 PDF: {pdf_file_path}")
                    return False
        except OSError as e:
            logging.error(f"文件验证失败: {e}")
            return False
        
        return True

class PDFConverter:
    """PDF转TXT转换器类。"""
    
    # 文件名非法字符正则
    INVALID_CHARS = r'[\\/:*?"<>|]'
    
    def __init__(self, config: ConverterConfig) -> None:
        self.config = config
        self.downloader = PDFDownloader(
            timeout=config.timeout,
            chunk_size=config.chunk_size
        )
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """清理文件名中的非法字符。"""
        return re.sub(PDFConverter.INVALID_CHARS, '', filename)
    
    def _download_with_retry(self, pdf_url: str, pdf_file_path: str) -> bool:
        """带重试机制的下载。"""
        for attempt in range(1, self.config.max_retries + 1):
            if self.downloader.download(pdf_url, pdf_file_path):
                return True
            if attempt < self.config.max_retries:
                logging.warning(f"重试下载 ({attempt}/{self.config.max_retries}): {pdf_url}")
        
        logging.error(f"下载失败（已重试 {self.config.max_retries} 次）: {pdf_url}")
        return False
    
    def _convert_pdf_to_txt(self, pdf_path: str, txt_path: str) -> bool:
        """将PDF转换为TXT。"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                with open(txt_path, 'w', encoding='utf-8') as f:
                    for page_num, page in enumerate(pdf.pages, 1):
                        try:
                            text = page.extract_text()
                            if text:
                                f.write(text)
                        except Exception as e:
                            logging.warning(f"提取第 {page_num} 页失败: {e}")
                            continue
            
            logging.info(f"转换成功: {txt_path}")
            return True
            
        except Exception as e:
            logging.error(f"PDF转换失败 {pdf_path}: {e}")
            return False
    
    def process_single_file(
        self,
        code: int,
        name: str,
        year: int,
        pdf_url: str
    ) -> bool:
        """处理单个文件的下载和转换。
        
        Args:
            code: 公司代码
            name: 公司简称
            year: 年份
            pdf_url: PDF下载链接
            
        Returns:
            处理是否成功
        """
        # 生成文件名
        base_name = self._sanitize_filename(f"{code:06}_{name}_{year}")
        pdf_file_path = os.path.join(self.config.pdf_dir, f"{base_name}.pdf")
        txt_file_path = os.path.join(self.config.txt_dir, f"{base_name}.txt")
        
        try:
            # 检查TXT是否已存在
            if os.path.exists(txt_file_path):
                logging.info(f"文件已存在，跳过: {base_name}.txt")
                return True
            
            # 下载PDF（如果不存在）
            if not os.path.exists(pdf_file_path):
                if not self._download_with_retry(pdf_url, pdf_file_path):
                    return False
            
            # 转换PDF为TXT
            if not self._convert_pdf_to_txt(pdf_file_path, txt_file_path):
                return False
            
            # 删除PDF（如果配置要求）
            if self.config.delete_pdf and os.path.exists(pdf_file_path):
                try:
                    os.remove(pdf_file_path)
                    logging.info(f"已删除PDF: {pdf_file_path}")
                except OSError as e:
                    logging.warning(f"删除PDF失败: {e}")
            
            return True
            
        except Exception as e:
            logging.error(f"处理文件失败 {code:06}_{name}_{year}: {e}")
            return False



def _process_task(args: Tuple) -> bool:
    """多进程任务包装函数。"""
    converter, code, name, year, pdf_url = args
    return converter.process_single_file(code, name, year, pdf_url)


class AnnualReportProcessor:
    """年报批量处理器。"""
    
    def __init__(self, config: ConverterConfig) -> None:
        self.config = config
        self.converter = PDFConverter(config)
    
    def _load_excel_data(self) -> Optional[pd.DataFrame]:
        """加载Excel数据。"""
        try:
            df = pd.read_excel(self.config.excel_file)
            logging.info(f"成功加载Excel文件: {self.config.excel_file}")
            return df
        except FileNotFoundError:
            logging.error(f"Excel文件不存在: {self.config.excel_file}")
            return None
        except Exception as e:
            logging.error(f"读取Excel失败: {e}")
            return None
    
    def _prepare_directories(self) -> bool:
        """创建必要的目录。"""
        try:
            Path(self.config.pdf_dir).mkdir(parents=True, exist_ok=True)
            Path(self.config.txt_dir).mkdir(parents=True, exist_ok=True)
            logging.info(f"目录准备完成: PDF={self.config.pdf_dir}, TXT={self.config.txt_dir}")
            return True
        except OSError as e:
            logging.error(f"创建目录失败: {e}")
            return False
    
    def _filter_data_by_year(self, df: pd.DataFrame) -> pd.DataFrame:
        """按年份过滤数据。"""
        required_columns = ['公司代码', '公司简称', '年份', '年报链接']
        
        # 检查必需列
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logging.error(f"Excel缺少必需列: {missing_cols}")
            return pd.DataFrame()
        
        # 过滤年份
        filtered = df[df['年份'].astype(str) == str(self.config.target_year)]
        logging.info(f"找到 {len(filtered)} 条 {self.config.target_year} 年的记录")
        return filtered
    
    def run(self) -> None:
        """执行批量处理流程。"""
        logging.info("="*60)
        logging.info("年报批量下载转换程序启动")
        logging.info(f"目标年份: {self.config.target_year}")
        logging.info(f"删除PDF: {self.config.delete_pdf}")
        logging.info("="*60)
        
        # 加载数据
        df = self._load_excel_data()
        if df is None:
            return
        
        # 准备目录
        if not self._prepare_directories():
            return
        
        # 过滤数据
        filtered_df = self._filter_data_by_year(df)
        if filtered_df.empty:
            logging.warning(f"未找到 {self.config.target_year} 年的数据")
            return
        
        # 准备任务列表
        tasks = [
            (self.converter, row['公司代码'], row['公司简称'], row['年份'], row['年报链接'])
            for _, row in filtered_df.iterrows()
        ]
        
        # 多进程处理
        worker_count = self.config.processes or min(cpu_count(), len(tasks))
        logging.info(f"使用 {worker_count} 个进程处理 {len(tasks)} 个文件")
        
        success_count = 0
        with Pool(processes=worker_count) as pool:
            results = pool.map(_process_task, tasks)
            success_count = sum(results)
        
        # 输出统计
        logging.info("="*60)
        logging.info(f"处理完成: 成功 {success_count}/{len(tasks)}")
        logging.info("="*60)


if __name__ == '__main__':
    # ==================== 配置区域 ====================
    
    # Excel表格路径（建议使用绝对路径）
    # 2024年02月14日更新后，此处只需要填写总表的路径，请于网盘或github中获取总表
    EXCEL_FILE = "年报链接_2024【公众号：凌小添】.xlsx"
    
    # 是否删除转换后的PDF文件（节省磁盘空间）
    DELETE_PDF = False
    
    # 是否批量处理多个年份
    BATCH_MODE = True
    
    # 批量模式：年份区间（包含起始和结束年份）
    START_YEAR = 2022
    END_YEAR = 2024
    
    # 单独模式：指定年份
    SINGLE_YEAR = 2023
    
    # 下载配置
    MAX_RETRIES = 3  # 最大重试次数
    TIMEOUT = 15  # 请求超时（秒）
    PROCESSES = None  # 进程数（None表示自动）
    
    # ==================== 执行逻辑 ====================
    
    if BATCH_MODE:
        # 批量处理多个年份
        for year in range(START_YEAR, END_YEAR + 1):
            config = ConverterConfig(
                excel_file=EXCEL_FILE,
                pdf_dir=f'年报文件/{year}/pdf年报',
                txt_dir=f'年报文件/{year}/txt年报',
                target_year=year,
                delete_pdf=DELETE_PDF,
                max_retries=MAX_RETRIES,
                timeout=TIMEOUT,
                processes=PROCESSES
            )
            
            processor = AnnualReportProcessor(config)
            processor.run()
            
            print(f"\n{year}年年报处理完毕\n")
    else:
        # 处理单独年份
        config = ConverterConfig(
            excel_file=EXCEL_FILE,
            pdf_dir=f'年报文件/{SINGLE_YEAR}/pdf年报',
            txt_dir=f'年报文件/{SINGLE_YEAR}/txt年报',
            target_year=SINGLE_YEAR,
            delete_pdf=DELETE_PDF,
            max_retries=MAX_RETRIES,
            timeout=TIMEOUT,
            processes=PROCESSES
        )
        
        processor = AnnualReportProcessor(config)
        processor.run()
        
        print(f"\n{SINGLE_YEAR}年年报处理完毕\n")
