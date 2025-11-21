# @Project ：PycharmProjects
# @File    ：text_analysis.py
# @IDE     ：PyCharm
# @Author  ：lingxiaotian
# @Date    ：2023/5/30 14:34

"""多进程年报文本关键词分析器。"""

from __future__ import annotations
import logging
import os
import re
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from typing import Iterator, List, Optional, Tuple
import jieba
import xlwt

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def extract_keywords(filename: str, keywords: List[str]) -> Tuple[List[int], int]:
    """读取单个文件并统计关键词及总词数。"""
    keyword_counts = [0] * len(keywords)
    total_words = 0

    try:
        with open(filename, "r", encoding="utf-8") as file_handle:
            content = file_handle.read()
    except OSError as exc:  # 捕获所有与文件相关的异常
        logging.error("读取文件失败: %s - %s", filename, exc)
        return keyword_counts, total_words

    words = [word for word in jieba.cut(content) if word.strip()]
    content_non = re.sub(r"[^\u4e00-\u9fa5]", "", content)
    words_non = [word for word in jieba.cut(content_non) if word.strip()]

    for idx, keyword in enumerate(keywords):
        keyword_counts[idx] = words.count(keyword)

    total_words = len(words_non)
    return keyword_counts, total_words


def _analyze_task(task: Tuple[str, str, str, str, List[str]]):
    file_path, stock_code, company_name, file_year, keywords = task
    try:
        keyword_counts, total_words = extract_keywords(file_path, keywords)
        return stock_code, company_name, file_year, total_words, keyword_counts
    except Exception as exc:  # noqa: BLE001
        logging.error("处理文件失败: %s - %s", file_path, exc)
        return None


@dataclass(frozen=True)
class AnalyzerConfig:
    folder_path: str
    keywords: List[str]
    output_path: str
    chunk_size: int = 100
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    processes: Optional[int] = None


class KeywordAnalyzer:
    """面向对象的多进程关键词分析器。"""

    HEADER = ["股票代码", "公司简称", "年份", "总词数"]

    def __init__(self, config: AnalyzerConfig) -> None:
        self.config = config
        self.workbook = xlwt.Workbook(encoding="utf-8")
        self.worksheet = self.workbook.add_sheet("公众号凌小添")
        self.next_row = 1
        self._extend_jieba_dict()
        self._write_header()

    def _extend_jieba_dict(self) -> None:
        """一次性将关键词加入 jieba 自定义词典，避免每个任务重复注入。"""
        for word in self.config.keywords:
            jieba.add_word(word)

    def _write_header(self) -> None:
        for col, title in enumerate(self.HEADER):
            self.worksheet.write(0, col, title)
        for index, keyword in enumerate(self.config.keywords, start=len(self.HEADER)):
            self.worksheet.write(0, index, keyword)

    def _should_skip_year(self, year: Optional[str]) -> bool:
        if year is None:
            return False
        try:
            year_int = int(year)
        except ValueError:
            return False

        if self.config.start_year is not None and year_int < self.config.start_year:
            return True
        if self.config.end_year is not None and year_int > self.config.end_year:
            return True
        return False

    def _count_txt_files(self) -> int:
        total = 0
        for root, dirs, files in os.walk(self.config.folder_path):
            folder_year = self._extract_year_from_path(root)
            if self._should_skip_year(folder_year):
                dirs[:] = []
                continue
            total += sum(1 for filename in files if filename.endswith(".txt"))
        return total

    def _extract_year_from_path(self, path: str) -> Optional[str]:
        match = re.match(r".*([12]\d{3}).*", os.path.basename(path))
        return match.group(1) if match else None

    def _iter_tasks(self) -> Iterator[Tuple[str, str, str, str, List[str]]]:
        for root, dirs, files in os.walk(self.config.folder_path):
            folder_year = self._extract_year_from_path(root)
            if self._should_skip_year(folder_year):
                dirs[:] = []
                continue

            for filename in files:
                if not filename.endswith(".txt"):
                    continue

                metadata = self._parse_filename(filename)
                if metadata is None:
                    stock_code = "000000"
                    company_name = os.path.splitext(filename)[0]
                    file_year = folder_year or "Unknown"
                else:
                    stock_code, company_name, file_year = metadata

                file_path = os.path.join(root, filename)
                yield (file_path, stock_code, company_name, file_year, self.config.keywords)

    @staticmethod
    def _parse_filename(filename: str) -> Optional[Tuple[str, str, str]]:
        match = re.match(r"^(\d{6})_(.*?)_(\d{4})\.txt$", filename)
        if not match:
            return None
        return match.group(1), match.group(2), match.group(3)

    def _write_result_row(self, result) -> None:
        stock_code, company_name, file_year, total_words, keyword_counts = result
        self.worksheet.write(self.next_row, 0, stock_code)
        self.worksheet.write(self.next_row, 1, company_name)
        self.worksheet.write(self.next_row, 2, file_year)
        self.worksheet.write(self.next_row, 3, total_words)
        for idx, count in enumerate(keyword_counts, start=len(self.HEADER)):
            self.worksheet.write(self.next_row, idx, count)
        self.next_row += 1

    def _save_workbook(self) -> None:
        self.workbook.save(self.config.output_path)

    def run(self) -> None:
        if not os.path.exists(self.config.folder_path):
            raise FileNotFoundError(f"文件夹不存在: {self.config.folder_path}")

        total_files = self._count_txt_files()
        if total_files == 0:
            logging.warning("未找到符合条件的 txt 文件，请检查路径：%s", self.config.folder_path)
            return

        logging.info("检测到 %s 个候选文件，准备开始处理", total_files)
        processed = 0
        worker_count = self.config.processes or min(cpu_count(), total_files)
        iterator = self._iter_tasks()

        with Pool(processes=worker_count) as pool:
            for result in pool.imap_unordered(_analyze_task, iterator):
                if result is None:
                    continue

                self._write_result_row(result)
                processed += 1
                progress = (processed / total_files) * 100
                print(f"\r当前进度: {progress:.2f}%", end="", flush=True)

                if self.config.chunk_size > 0 and processed % self.config.chunk_size == 0:
                    self._save_workbook()

        print("\n分析完成，正在保存 Excel……")
        self._save_workbook()
        logging.info("Excel 文件保存成功：%s", self.config.output_path)


def validate_year_range(start_year: Optional[int], end_year: Optional[int]) -> None:
    if start_year is not None and end_year is not None and start_year > end_year:
        raise ValueError("起始年份不能大于结束年份")


if __name__ == "__main__":
    # 自定义关键词列表，可按需扩展/替换
    KEYWORDS = [
        "人工智能",
        "商业智能",
        "图像理解",
        "投资决策辅助系统",
        "智能数据分",
        "大数据",
        "数据挖掘",
        "文本挖掘",
    ]

    # TXT 根目录（建议填写绝对路径，文件夹内按年份划分）
    ROOT_FOLDER = "年报文件"
    # 需要统计的起始年份（包含）
    START_YEAR = 2023
    # 需要统计的结束年份（包含）
    END_YEAR = 2024
    # Excel 输出文件名
    OUTPUT_NAME = "词频分析结果.xls"
    # 每处理多少文件持久化一次，避免数据丢失
    CHUNK_SIZE = 100
    # 自定义进程数（None 表示自动按 CPU 核心数调整）
    PROCESSES = None

    try:
        validate_year_range(START_YEAR, END_YEAR)
        analyzer = KeywordAnalyzer(
            AnalyzerConfig(
                folder_path=ROOT_FOLDER,
                keywords=KEYWORDS,
                output_path=OUTPUT_NAME,
                chunk_size=CHUNK_SIZE,
                start_year=START_YEAR,
                end_year=END_YEAR,
                processes=PROCESSES,
            )
        )
        analyzer.run()
    except Exception as exc:  # noqa: BLE001
        logging.error("文件处理失败: %s", exc)

    print("提示：如果程序没有任何输出，请检查路径及 TXT 文件命名格式（如 600519_贵州茅台_2019.txt）。")
