from app.categorizer.category_rules import CATEGORY_RULES

class TransactionCategorizer:

    @staticmethod
    def categorize(description: str):
        description = "".join(description.upper().split())

        for category, keywords in CATEGORY_RULES.items():
            for keyword in keywords:
                if keyword in description:
                    return category
                
        return "Others"