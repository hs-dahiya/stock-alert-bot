GEMINI_WORTHY = [
    'financial results', 'quarterly results', 'annual results', 'earnings',
    'order win', 'order receipt', 'major contract', 'loi received', 'work order',
    'dividend', 'interim dividend',
    'buyback', 'qip', 'rights issue', 'preferential allotment',
]

def needs_gemini(filing: dict) -> bool:
    if not filing.get('pdf_url'):
        return False
    text = (filing.get('category', '') + ' ' + filing.get('description', '')).lower()
    return any(kw in text for kw in GEMINI_WORTHY)
