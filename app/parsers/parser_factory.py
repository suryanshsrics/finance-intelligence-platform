from app.parsers.banks.sbi_parser import SBIParser
from app.parsers.statement_parser import UnsupportedBankError

def get_parser(bank_name: str):
    if bank_name == 'State Bank of India':
        return SBIParser()
    
    raise UnsupportedBankError(f"Parser for {bank_name} is not complete.")
    
parser = get_parser("State Bank of India")
print(type(parser))