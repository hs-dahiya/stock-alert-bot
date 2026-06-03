SCORE_MAP = [
    (10, ['buyback', 'open offer', 'delisting', 'credit rating downgrade', 'rating withdrawn']),
    (9,  ['dividend', 'interim dividend', 'promoter pledge', 'pledge', 'encumbrance',
          'insider trading', 'bulk deal', 'block deal']),
    (8,  ['financial results', 'quarterly results', 'annual results', 'earnings',
          'order win', 'order receipt', 'major contract', 'loi received', 'work order']),
    (7,  ['board meeting outcome', 'outcome of board', 'board meeting result']),
    (6,  ['rights issue', 'qip', 'preferential allotment', 'ofs', 'fundraise']),
    (5,  ['investor presentation', 'analyst meet', 'concall', 'earnings call']),
    (3,  ['change in director', 'appointment', 'resignation', 'kmp']),
    (2,  ['regulation 30', 'compliance', 'intimation', 'newspaper']),
    (1,  ['exchange notice', 'general update', 'corrigendum']),
]

def score_filing(filing: dict) -> int:
    text = (filing.get('category', '') + ' ' + filing.get('description', '')).lower()
    for score, keywords in SCORE_MAP:
        for kw in keywords:
            if kw in text:
                return score
    return 2

def should_alert(filing: dict, min_score: int = 6) -> bool:
    filing['priority_score'] = score_filing(filing)
    return filing['priority_score'] >= min_score
