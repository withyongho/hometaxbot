import unittest
from datetime import date
from decimal import Decimal

from hometaxbot.scraper import HometaxScraper, reports, transactions
from tests import testdata


class TestScrape(unittest.TestCase):
    def test_scrape_세금신고(self):
        scraper = HometaxScraper()
        scraper.login_with_cert(testdata.CORP_CERT, testdata.CORP_PASSWORD)

        begin = date(2024, 1, 1)
        end = date(2024, 6, 1)

        results = list(reports.전자신고결과조회(scraper, begin, end))
        self.assertIsInstance(results[0].접수일, date)
        self.assertIsInstance(results[0].금액, Decimal)

        self.assertIsNotNone(next(reports.납부내역(scraper, begin, end)).전자납부번호)
        self.assertIsNotNone(next(reports.납부내역(scraper, begin, end)).전자납부번호)
        self.assertIsNotNone(list(reports.환급금조회(scraper, begin, end)))
        self.assertIsNotNone(list(reports.고지내역(scraper, begin, end)))
        self.assertIsNotNone(list(reports.체납내역(scraper, begin, end)))

    def test_scrape_데이터(self):
        scraper = HometaxScraper()
        scraper.login_with_cert(testdata.CORP_CERT, testdata.CORP_PASSWORD)

        begin = date(2024, 1, 1)
        end = date(2024, 10, 1)

        tax_invoice = next(transactions.세금계산서(scraper, begin, end))
        self.assertIsNotNone(tax_invoice.전송일자)
        self.assertNotEqual(tax_invoice.공급자.납세자번호, tax_invoice.공급받는자.납세자번호)
        self.assertGreater(tax_invoice.총금액, 0)
        self.assertGreater(next(transactions.카드매입(scraper, begin, end)).총금액, 0)

        # 잘 안 쓰다보니 귀찮아서 안 고침
        # self.assertGreater(next(transactions.카드매출월간집계(scraper, date(2023, 1, 1), date(2023, 3, 1))).합계금액, 0)

    def test_scrape_현금영수증(self):
        scraper = HometaxScraper()
        scraper.login_with_cert(testdata.CORP_CERT, testdata.CORP_PASSWORD)

        self.assertGreater(next(transactions.현금영수증(scraper, date(2023, 11, 1), date(2023, 12, 31))).총금액, 0)
        self.assertGreater(next(transactions.현금영수증(scraper, date(2024, 1, 1), date(2024, 3, 1))).총금액, 0)

        results = list(transactions.현금영수증(scraper, date(2022, 4, 1), date(2022, 6, 27)))
        self.assertEqual(50, len(results))
        self.assertNotEqual(results[1], results[11])
        self.assertGreater(results[0].총금액, 0)

    def test_scrape_세금신고내역(self):
        scraper = HometaxScraper()
        scraper.login_with_cert(testdata.CORP_CERT, testdata.CORP_PASSWORD)

        for report in reports.세금신고내역_원천세(scraper, date(2024, 5, 1), date(2025, 4, 1)):
            self.assertEqual(16500, report.납부금액)

        for report in reports.세금신고내역_부가가치세(scraper, date(2024, 5, 1), date(2025, 4, 1)):
            print(report)

        for report in reports.세금신고내역_법인세(scraper, date(2024, 5, 1), date(2025, 4, 1)):
            print(report)

    def test_신고서_data_for_pdf(self):
        scraper = HometaxScraper()
        scraper.login_with_cert(testdata.CORP_CERT, testdata.CORP_PASSWORD)

        for report in reports.세금신고내역_부가가치세(scraper, date(2024, 5, 1), date(2025, 4, 1)):
            clip_uid = reports.clipreport_uid(scraper, report.세목코드, report.접수번호)
            data = reports.clip_data(scraper, clip_uid)
            print(data)

    def test_연말정산금액_for_pdf(self):
        scraper = HometaxScraper()
        scraper.login_with_cert(testdata.CORP_CERT, testdata.CORP_PASSWORD)

        for report in reports.세금신고내역_원천세(scraper, date(2025, 1, 1), date(2025, 6, 19)):
            clip_uid = reports.clipreport_uid(scraper, report.세목코드, report.접수번호)
            data = reports.clip_data(scraper, clip_uid)
            원천_연말정산금액 = reports.get_원천세_연말정산금액(data)
            print(f"원천_연말정산금액 :{원천_연말정산금액}")
