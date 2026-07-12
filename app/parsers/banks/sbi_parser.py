from typing import List

class SBIParser:
    def _find_value_after_label(self, lines: List[str], label: str):
        for line in lines:
            if label in line:
                return line.split(label, 1)[1].strip()
        return None
    
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
    
