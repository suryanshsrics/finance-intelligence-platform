import unittest

from app.parsers.banks.sbi_parser import SBIParser


class SBIParserTests(unittest.TestCase):
    def test_imps_deposit_is_classified_as_credit(self):
        parser = SBIParser()
        block = [
            "DEP TFR",
            "02/05/2026 02/05/2026 IMPS/612214573820/ICN-XX602- - - 64.00 59,038.86",
            "FLIPKART/FT2605021",
            "0098328162092 AT 03205",
            "GOLGHAR (GORAKHPUR)",
        ]

        parsed = parser.parse_transaction(block)

        self.assertEqual(parsed["transaction_type"], "CREDIT")

    def test_atm_wdl_transaction_is_parsed_as_separate_debit(self):
        parser = SBIParser()
        text = (
            "WDL TFR\n"
            "06/05/2026 06/05/2026 UPI/DR/923646461266/SURAJIT - 33.00 - 3,540.16\n"
            "/SBIN/surajit.se/UPI\n"
            "0097692162094 AT 03205\n"
            "GOLGHAR (GORAKHPUR)\n"
            "ATM WDL ATM CASH\n"
            "06/05/2026 06/05/2026 612615023310 +TCS GITANJALI - 300.00 - 3,240.16\n"
            "TECH PARN 24"
        )

        blocks = parser.split_transaction_blocks(text)
        self.assertEqual(len(blocks), 2)
        self.assertTrue(any("ATM WDL" in " ".join(block) for block in blocks))

        atm_block = next(block for block in blocks if "ATM WDL" in " ".join(block))
        parsed = parser.parse_transaction(atm_block)

        self.assertEqual(parsed["transaction_type"], "DEBIT")
        self.assertEqual(parsed["amount"], "300.00")
        self.assertEqual(parsed["balance"], "3240.16")

    def test_pos_atm_transaction_is_parsed_and_separated(self):
        parser = SBIParser()
        text = (
            "WDL TFR\n"
            "27/04/2026 27/04/2026 UPI/DR/984151661176/MONOTOS - 16.00 - 299.72\n"
            "H/YESB/paytmqr6r2/UPI\n"
            "0097690162095 AT 03205\n"
            "GOLGHAR (GORAKHPUR)\n"
            "POS ATM PURCH OTHPG\n"
            "28/04/2026 28/04/2026 611815219209WBMETRO - 28.50 - 127.22\n"
            "Mumbai"
        )

        blocks = parser.split_transaction_blocks(text)
        self.assertEqual(len(blocks), 2)

        pos_block = next(block for block in blocks if any("POS ATM" in l for l in block))
        parsed = parser.parse_transaction(pos_block)

        self.assertEqual(parsed["transaction_type"], "DEBIT")
        self.assertEqual(parsed["amount"], "28.50")
        self.assertEqual(parsed["balance"], "127.22")

    def test_interest_credit_transaction_is_parsed_separately(self):
        parser = SBIParser()
        text = (
            "ATM WDL ATM CASH\n"
            "25/06/2026 25/06/2026 617609006417 GORAKHPUR - 1,000.00 - 307.61\n"
            "GORA\n"
            "25/06/2026 25/06/2026 INTEREST CREDIT - - 35.00 342.61"
        )

        blocks = parser.split_transaction_blocks(text)
        self.assertEqual(len(blocks), 2)

        interest_block = next(block for block in blocks if any("INTEREST CREDIT" in l for l in block))
        parsed = parser.parse_transaction(interest_block)

        self.assertEqual(parsed["transaction_type"], "CREDIT")
        self.assertEqual(parsed["amount"], "35.00")
        self.assertEqual(parsed["balance"], "342.61")


if __name__ == "__main__":
    unittest.main()
