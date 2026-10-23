import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PyPDF2 import PdfWriter
from PyPDF2.generic import DictionaryObject, NameObject, DecodedStreamObject


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


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = pdf_batch_converter.ConverterConfig(
            excel_file='reports.xlsx', pdf_dir=str(self.root), txt_dir=str(self.root),
            target_year=2025, delete_pdf=True,
        )
        self.converter = pdf_batch_converter.PDFConverter(self.config)
        self.addCleanup(self.converter.downloader.session.close)
        self.pdf = self.root / '000001_Test_2025.pdf'
        self.txt = self.pdf.with_suffix('.txt')

    def make_pdf(self, texts):
        """生成离线文本或空白页面，验证实际解析器而非只验证 mock 返回值。"""
        writer = PdfWriter()
        for text in texts:
            writer.add_blank_page(width=300, height=300)
            page = writer.pages[-1]
            font = DictionaryObject({
                NameObject('/Type'): NameObject('/Font'),
                NameObject('/Subtype'): NameObject('/Type1'),
                NameObject('/BaseFont'): NameObject('/Helvetica'),
            })
            page[NameObject('/Resources')] = DictionaryObject({
                NameObject('/Font'): DictionaryObject({NameObject('/F1'): font}),
            })
            stream = DecodedStreamObject()
            stream.set_data(f'BT /F1 12 Tf 20 250 Td ({text}) Tj ET'.encode('ascii'))
            page[NameObject('/Contents')] = writer._add_object(stream)
        with self.pdf.open('wb') as output:
            writer.write(output)

    def test_real_multipage_pdf_preserves_both_pages(self):
        self.make_pdf(['first page', 'second page'])
        with mock.patch.object(self.converter, '_convert_with_pypdf2') as fallback:
            self.assertTrue(self.converter._convert_pdf_to_txt(str(self.pdf), str(self.txt)))
            fallback.assert_not_called()
        text = self.txt.read_text()
        self.assertIn('first page', text)
        self.assertIn('second page', text)
        self.assertEqual(list(self.root.glob('*.part')), [])

    def test_blank_pdf_fails_without_deleting_source_or_publishing_txt(self):
        self.make_pdf([''])
        self.assertFalse(self.converter.process_single_file(1, 'Test', 2025, 'unused'))
        self.assertTrue(self.pdf.exists())
        self.assertFalse(self.txt.exists())
        self.assertEqual(list(self.root.glob('*.part')), [])

    def test_existing_whitespace_txt_is_reconverted(self):
        self.make_pdf(['recovered content'])
        self.txt.write_text(' \n\t')
        self.assertTrue(self.converter.process_single_file(1, 'Test', 2025, 'unused'))
        self.assertIn('recovered content', self.txt.read_text())

    def test_pdfplumber_page_exception_is_failure(self):
        document = mock.MagicMock()
        document.pages = [mock.Mock(), mock.Mock()]
        document.pages[0].extract_text.return_value = 'first page'
        document.pages[1].extract_text.side_effect = ValueError('broken page')
        with mock.patch.object(pdf_batch_converter.pdfplumber, 'open') as opened:
            opened.return_value.__enter__.return_value = document
            self.assertFalse(self.converter._convert_with_pdfplumber('unused', str(self.txt)))

    def test_pypdf2_page_exception_is_failure(self):
        self.pdf.write_bytes(b'%PDF fake')
        document = mock.Mock()
        document.pages = [mock.Mock(), mock.Mock()]
        document.pages[0].extract_text.return_value = 'first page'
        document.pages[1].extract_text.side_effect = ValueError('broken page')
        with mock.patch.object(pdf_batch_converter, 'PdfReader', return_value=document):
            self.assertFalse(self.converter._convert_with_pypdf2(str(self.pdf), str(self.txt)))

    def test_partial_failure_is_not_mixed_with_fallback_result(self):
        def partial(_pdf, txt):
            Path(txt).write_text('partial result')
            return False

        def complete(_pdf, txt):
            Path(txt).write_text('complete result')
            return True

        with mock.patch.object(self.converter, '_convert_with_pdfplumber', side_effect=partial), \
             mock.patch.object(self.converter, '_convert_with_pypdf2', side_effect=complete):
            self.assertTrue(self.converter._convert_pdf_to_txt('unused', str(self.txt)))
        self.assertEqual(self.txt.read_text(), 'complete result')
        self.assertEqual(list(self.root.glob('*.part')), [])

    def test_all_methods_fail_preserves_existing_file(self):
        self.txt.write_text('previous output')
        with mock.patch.object(self.converter, '_convert_with_pdfplumber', return_value=False), \
             mock.patch.object(self.converter, '_convert_with_pypdf2', return_value=False), \
             mock.patch.object(self.converter, '_convert_with_pdfminer', return_value=False):
            self.assertFalse(self.converter._convert_pdf_to_txt('unused', str(self.txt)))
        self.assertEqual(self.txt.read_text(), 'previous output')
        self.assertEqual(list(self.root.glob('*.part')), [])

    def test_invalid_download_preserves_previous_pdf_and_cleans_temp(self):
        self.pdf.write_bytes(b'%PDF previous')
        response = mock.MagicMock(status_code=200, headers={'Content-Type': 'application/pdf'})
        response.iter_content.return_value = [b'<html>not a pdf</html>']
        with mock.patch.object(self.converter.downloader.session, 'get') as get:
            get.return_value.__enter__.return_value = response
            self.assertFalse(self.converter.downloader.download(
                'https://static.cninfo.com.cn/report.pdf', str(self.pdf)))
        self.assertEqual(self.pdf.read_bytes(), b'%PDF previous')
        self.assertEqual(list(self.root.glob('*.part')), [])

    def test_detail_page_url_is_rejected_before_network(self):
        with mock.patch.object(self.converter.downloader.session, 'get') as get:
            self.assertFalse(self.converter.downloader.download(
                'https://data.eastmoney.com/notices/detail/002137/AN2026.html', str(self.pdf)))
            get.assert_not_called()

    def test_numeric_excel_years_and_missing_values(self):
        df = pdf_batch_converter.pd.DataFrame({
            '公司代码': [1, 2, 3, 4], '公司简称': ['a', 'b', 'c', 'd'],
            '年份': [2025.0, None, '2025', 2024], '年报链接': ['url'] * 4,
        })
        processor = pdf_batch_converter.AnnualReportProcessor(self.config)
        self.assertEqual(processor._filter_data_by_year(df)['公司代码'].tolist(), [1, 3])

    def test_worker_closes_http_session_on_exception(self):
        with mock.patch.object(pdf_batch_converter, 'PDFConverter') as cls:
            cls.return_value.process_single_file.side_effect = ValueError('invalid report')
            with self.assertRaises(ValueError):
                pdf_batch_converter._process_task((self.config, 1, 'Test', 2025, 'url'))
            cls.return_value.downloader.session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
