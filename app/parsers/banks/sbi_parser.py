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
        if line.startswith("Page no.") or line == 'Balance':
            return True
        return False
    
    def parse(self, raw_text: str):
        pass

    def extract_metadata(self, raw_text: str):
        lines = raw_text.splitlines()
        metadata = {}

        metadata['bank_name'] = "State Bank of India"
        metadata['branch_name'] = self._find_value_after_label(lines, "Branch Name :")
        metadata['account_number'] = self._find_value_after_label(lines, "Account Number :")
        metadata['currency'] = self._find_value_after_label(lines, "Currency :")
        statement_period = self._find_value_after_label(lines, "Statement From :")
        if statement_period:
            parts = statement_period.split(' to ')

            if len(parts) == 2:
                metadata['statement_start_date'] = parts[0].strip()
                metadata['statement_end_date'] = parts[1].strip()
            else:
                metadata['statement_start_date'] = None
                metadata['statement_end_date'] = None
        else:
            metadata['statement_start_date'] = None
            metadata['statement_end_date'] = None

        return metadata
    
    def split_transaction_blocks(self, raw_text: str):
        lines = raw_text.splitlines()
        transactions = []
        current_transaction = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if self._is_page_header(line):
                continue

            if line.startswith("Statement Summary"):
                break

            if self._is_transaction_start(line):
                if not current_transaction:
                    current_transaction = [line]
                else:
                    transactions.append(current_transaction)
                    current_transaction = [line]
            else:
                if current_transaction:
                    current_transaction.append(line)
            
        if current_transaction:
            transactions.append(current_transaction)

        return transactions
    
