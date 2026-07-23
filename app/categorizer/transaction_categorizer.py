from app.categorizer.category_rules import CATEGORY_RULES
import re

class TransactionCategorizer:
    @staticmethod
    def categorize(description: str) -> str:
        description = description.upper()

        for category, patterns in CATEGORY_RULES.items():
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    return category
        # Fallback: Unknown UPI transactions -> Transfer
        if re.search(r"\b(UPI|IMPS|NEFT|RTGS)\b", description):
            return "Transfer"
        return "Others"