PROMOTER_KEYWORDS = [
    'promoter pledge', 'pledge', 'encumbrance',
    'insider trading', 'upsi', 'sast',
    'bulk deal', 'block deal',
    'shareholding pattern', 'promoter stake',
]

def is_promoter_filing(filing: dict) -> bool:
    text = (filing.get('category', '') + ' ' + filing.get('description', '')).lower()
    return any(kw in text for kw in PROMOTER_KEYWORDS)

def format_promoter_alert(filing: dict) -> str:
    lines = [
        f"🔍 *PROMOTER ACTIVITY*  |  {filing['exchange']}  |  Priority: {filing.get('priority_score', 9)}/10",
        f"🏢 {filing['company']}  (`{filing['symbol']}`)",
        f"📋 {filing['description'][:250]}",
    ]
    if filing.get('pdf_url'):
        lines.append(f"\n[📄 View Filing]({filing['pdf_url']})")
    return '\n'.join(lines)
