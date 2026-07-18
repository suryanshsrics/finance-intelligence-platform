from typing import List
import re


class SBIParser:
    DATE_PATTERN = r"\d{2}/\d{2}/\d{4}"
    TRANSACTION_START_RE = re.compile(rf"^{DATE_PATTERN}\s+{DATE_PATTERN}\b")

    def _find_value_after_label(self, lines: List[str], label: str):
        for line in lines:
            if label in line:
                return line.split(label, 1)[1].strip()
        return None

    def _is_transaction_start(self, line: str):
        return bool(self.TRANSACTION_START_RE.match(line.strip()))

    def _is_page_header(self, line: str):
        if line.startswith("Page no.") or line == "Balance":
            return True
        return False

    def parse_transaction(self, transaction_block: list[str]):

        transaction_line = next(
            (
                line
                for line in transaction_block
                if self._is_transaction_start(line.strip())
            ),
            transaction_block[0],
        )

        # -----------------------
        # Transaction Date
        # -----------------------

        m1 = re.match(
            r"^(\d{2}/\d{2}/\d{4})\s+\d{2}/\d{2}/\d{4}",
            transaction_line,
        )

        transaction_date = m1.group(1) if m1 else None

        # -----------------------
        # Amount & Balance
        # -----------------------

        values = re.findall(
            r"\d{1,3}(?:,\d{3})*(?:\.\d{2})",
            transaction_line,
        )

        amount = None
        balance = None

        if len(values) >= 2:
            amount = values[-2].replace(",", "")
            balance = values[-1].replace(",", "")

        # -----------------------
        # Transaction Type
        # -----------------------

        block_text = " ".join(transaction_block).upper()

        transaction_type = None
        transaction_line_upper = transaction_line.upper()

        if "/CR/" in transaction_line_upper:
            transaction_type = "CREDIT"

        elif "/DR/" in transaction_line_upper:
            transaction_type = "DEBIT"

        elif "DIRECT DR" in block_text or "WDL TFR" in block_text:
            transaction_type = "DEBIT"

        # If still unknown, infer from which trailing column contains the amount.
        # Pattern examples:
        #  - Credit:  "... - - 1,252.00 15,202.17"  (dash, dash, credit, balance)
        #  - Debit:   "... - 300.00 - 3,240.16"    (dash, debit, dash, balance)
        if transaction_type is None:
            credit_col_match = re.search(
                r"\s-\s-\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2}))$",
                transaction_line,
            )

            debit_col_match = re.search(
                r"\s-\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))\s+-\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))$",
                transaction_line,
            )

            if credit_col_match:
                transaction_type = "CREDIT"

            elif debit_col_match:
                transaction_type = "DEBIT"

        # -----------------------
        # Description
        # -----------------------

        description_lines = []

        for line in transaction_block:

            if line == transaction_line:

                # Remove both dates
                description = re.sub(
                    rf"^{self.DATE_PATTERN}\s+{self.DATE_PATTERN}\s+",
                    "",
                    line,
                )

                # Remove trailing amount columns
                description = re.sub(
                    r"\s+-?\s*-?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})\s+-?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})$",
                    "",
                    description,
                )

                description = description.strip()

                if description:
                    description_lines.append(description)

            else:
                description_lines.append(line)

        description = " ".join(description_lines)
        description = " ".join(description.split())

        return {
            "transaction_date": transaction_date,
            "balance": balance,
            "transaction_type": transaction_type,
            "amount": amount,
            "description": description,
        }

    def extract_metadata(self, raw_text: str):
        lines = raw_text.splitlines()

        metadata = {}

        metadata["bank_name"] = "State Bank of India"
        metadata["branch_name"] = self._find_value_after_label(
            lines,
            "Branch Name :",
        )
        metadata["account_number"] = self._find_value_after_label(
            lines,
            "Account Number :",
        )
        metadata["currency"] = self._find_value_after_label(
            lines,
            "Currency :",
        )

        statement_period = self._find_value_after_label(
            lines,
            "Statement From :",
        )

        if statement_period:
            parts = statement_period.split(" to ")

            if len(parts) == 2:
                metadata["statement_start_date"] = parts[0].strip()
                metadata["statement_end_date"] = parts[1].strip()
            else:
                metadata["statement_start_date"] = None
                metadata["statement_end_date"] = None
        else:
            metadata["statement_start_date"] = None
            metadata["statement_end_date"] = None

        return metadata

    def split_transaction_blocks(self, raw_text: str):
        lines = raw_text.splitlines()

        transactions = []
        current_transaction = []

        transaction_markers = (
            "DEP TFR",
            "WDL TFR",
            "ATM WDL",
            "POS ATM PURCH OTHPG",
            "POS ATM",
            "DIRECT DR",
            "DIRECT CR",
        )

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if self._is_page_header(line):
                continue

            if line.startswith("Statement Summary"):
                break

            if line.startswith(transaction_markers):

                if current_transaction:
                    transactions.append(current_transaction)

                current_transaction = [line]

                continue

            if self._is_transaction_start(line):

                if (
                    current_transaction
                    and current_transaction[0].startswith(transaction_markers)
                    and len(current_transaction) == 1
                ):
                    # Marker header has been seen; append the first transaction line.
                    current_transaction.append(line)
                else:
                    if current_transaction:
                        transactions.append(current_transaction)

                    current_transaction = [line]

            else:

                if current_transaction:
                    current_transaction.append(line)

        if current_transaction:
            transactions.append(current_transaction)

        return transactions
    
    def parse_statement(self, raw_text: str):
        metadata = self.extract_metadata(raw_text)
        transaction_blocks = self.split_transaction_blocks(raw_text)

        transactions = []
        for block in transaction_blocks:
            parsed = self.parse_transaction(block)
            transactions.append(parsed)

        return {
            "metadata": metadata,
            "transactions": transactions
        }


'''Wrote this code for faster testing.
 Commented it out now. '''

# if __name__ == "__main__":
#     from pathlib import Path
#     from pprint import pprint

#     # Read extracted text
#     text = Path("parsed_statement.txt").read_text(encoding="utf-8")

#     parser = SBIParser()

#     # Parse complete statement
#     parsed_statement = parser.parse_statement(text)

#     print("=" * 70)
#     print("METADATA")
#     print("=" * 70)
#     pprint(parsed_statement["metadata"])

#     print()

#     print("=" * 70)
#     print(f"TOTAL TRANSACTIONS: {len(parsed_statement['transactions'])}")
#     print("=" * 70)

#     for i, transaction in enumerate(parsed_statement["transactions"], start=1):
#         print(f"\nTransaction {i}")
#         print("-" * 40)
#         pprint(transaction)