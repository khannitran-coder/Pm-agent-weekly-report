import re

def mask_pii(text: str) -> str:
    # Mask SSN
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[PII_REDACTED_SSN]', text)
    # Mask Credit Cards
    text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[PII_REDACTED_CC]', text)
    return text

if __name__ == "__main__":
    sample = "Employee SSN: 123-45-6789 submitted report."
    print(mask_pii(sample))
