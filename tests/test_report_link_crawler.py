import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "1.report_link_crawler.py"
spec = importlib.util.spec_from_file_location("report_link_crawler", MODULE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load module from {MODULE_PATH}")
report_link_crawler = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = report_link_crawler
spec.loader.exec_module(report_link_crawler)


class FetchAllPagesTests(unittest.TestCase):
    def make_client(self, pages):
        client = report_link_crawler.CNINFOClient(
            report_link_crawler.CrawlerConfig(
                target_year=2024,
                exclude_keywords=[],
            )
        )
        calls = []

        def fetch_page(page_num, date_range):
            calls.append((page_num, date_range))
            return pages.get(page_num)

        client.fetch_page = fetch_page
        return client, calls

    def test_single_page_result_is_kept_when_totalpages_is_zero(self):
        announcement = {"secCode": "000001", "announcementTitle": "2024年年度报告"}
        client, calls = self.make_client({
            1: {
                "hasMore": False,
                "totalpages": 0,
                "totalRecordNum": 1,
                "announcements": [announcement],
            }
        })

        with contextlib.redirect_stdout(io.StringIO()):
            results = client.fetch_all_pages("2025-04-01~2025-04-01")

        self.assertEqual(results, [announcement])
        self.assertEqual(calls, [(1, "2025-04-01~2025-04-01")])

    def test_fetches_tail_page_when_totalpages_omits_partial_page(self):
        page_1_item = {"secCode": "000001", "announcementTitle": "page 1"}
        page_2_item = {"secCode": "000002", "announcementTitle": "tail page"}
        client, calls = self.make_client({
            1: {
                "hasMore": False,
                "totalpages": 1,
                "totalRecordNum": 31,
                "announcements": [page_1_item],
            },
            2: {
                "hasMore": False,
                "totalpages": 1,
                "totalRecordNum": 31,
                "announcements": [page_2_item],
            },
        })

        with contextlib.redirect_stdout(io.StringIO()):
            results = client.fetch_all_pages("2025-04-02~2025-04-02")

        self.assertEqual(results, [page_1_item, page_2_item])
        self.assertEqual(
            calls,
            [(1, "2025-04-02~2025-04-02"), (2, "2025-04-02~2025-04-02")],
        )

    def test_total_announcement_field_is_supported(self):
        announcement = {"secCode": "000003", "announcementTitle": "field alias"}
        client, calls = self.make_client({
            1: {
                "hasMore": False,
                "totalpages": 0,
                "totalAnnouncement": 1,
                "announcements": [announcement],
            }
        })

        with contextlib.redirect_stdout(io.StringIO()):
            results = client.fetch_all_pages("2025-04-03~2025-04-03")

        self.assertEqual(results, [announcement])
        self.assertEqual(calls, [(1, "2025-04-03~2025-04-03")])

    def test_zero_total_record_num_returns_empty_results(self):
        client, calls = self.make_client({
            1: {
                "hasMore": False,
                "totalpages": 0,
                "totalRecordNum": 0,
                "announcements": None,
            }
        })

        results = client.fetch_all_pages("2025-01-01~2025-01-01")

        self.assertEqual(results, [])
        self.assertEqual(calls, [(1, "2025-01-01~2025-01-01")])


if __name__ == "__main__":
    unittest.main()
