"""3.text_analysis 的关键词统计测试，覆盖 spawn 子进程下词频为 0 的问题。"""

import importlib.util
import multiprocessing
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "3.text_analysis.py"

CONTENT = "公司加快数字资产布局，数字资产规模增长，大数据平台上线。" * 3


def _load():
    spec = importlib.util.spec_from_file_location("text_analysis_mod", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclass 需要模块已注册
    spec.loader.exec_module(module)
    return module


def _count_in_child(args):
    """spawn 子进程里重新导入模块，模拟 Windows/macOS 的真实情况。"""
    filename, keywords = args
    module = _load()
    return module.extract_keywords(filename, keywords)


class KeywordCountTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / "000001_测试_2023.txt"
        self.file.write_text(CONTENT, encoding="utf-8")
        self.keywords = ["数字资产", "大数据"]

    def test_extract_keywords_registers_words_itself(self):
        module = _load()
        counts, total = module.extract_keywords(str(self.file), self.keywords)
        self.assertEqual(counts, [6, 3])
        self.assertGreater(total, 0)

    def test_spawn_child_process_counts_keywords(self):
        ctx = multiprocessing.get_context("spawn")
        with ctx.Pool(1) as pool:
            counts, total = pool.apply(_count_in_child, ((str(self.file), self.keywords),))
        self.assertEqual(counts, [6, 3])
        self.assertGreater(total, 0)


if __name__ == "__main__":
    unittest.main()
