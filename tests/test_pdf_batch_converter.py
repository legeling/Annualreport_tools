import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "2.pdf_batch_converter.py"
spec = importlib.util.spec_from_file_location("pdf_batch_converter", MODULE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load module from {MODULE_PATH}")
pdf_batch_converter = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pdf_batch_converter
spec.loader.exec_module(pdf_batch_converter)


class WorkerCountTests(unittest.TestCase):
    def make_processor(self, processes=None):
        config = pdf_batch_converter.ConverterConfig(
            excel_file="reports.xlsx",
            pdf_dir="pdf",
            txt_dir="txt",
            target_year=2024,
            processes=processes,
        )
        return pdf_batch_converter.AnnualReportProcessor(config)

    @mock.patch.object(pdf_batch_converter, "cpu_count", return_value=16)
    def test_default_worker_count_is_capped(self, _mock_cpu_count):
        processor = self.make_processor()

        self.assertEqual(processor._resolve_worker_count(20), 4)

    @mock.patch.object(pdf_batch_converter, "cpu_count", return_value=16)
    def test_default_worker_count_never_exceeds_task_count(self, _mock_cpu_count):
        processor = self.make_processor()

        self.assertEqual(processor._resolve_worker_count(2), 2)

    def test_explicit_worker_count_is_respected(self):
        processor = self.make_processor(processes=8)

        self.assertEqual(processor._resolve_worker_count(20), 8)

    def test_explicit_worker_count_never_exceeds_task_count(self):
        processor = self.make_processor(processes=8)

        self.assertEqual(processor._resolve_worker_count(3), 3)

    def test_invalid_worker_count_raises_error(self):
        processor = self.make_processor(processes=0)

        with self.assertRaises(ValueError):
            processor._resolve_worker_count(10)


if __name__ == "__main__":
    unittest.main()
