import requests, time

NSE_BASE = 'https://www.nseindia.com'
NSE_API  = 'https://www.nseindia.com/api/corporate-announcements?index=equities'

SESSION_HEADERS = {
    'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer':         'https://www.nseindia.com/companies-listing/corporate-filings-announcements',
}

def poll_nse(watchlist_symbols: set) -> list:
    try:
        s = requests.Session()
        s.headers.update(SESSION_HEADERS)
        s.get(NSE_BASE, timeout=10)
        time.sleep(2)
        resp = s.get(NSE_API, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f'[NSE] Poll failed: {e}')
        return []

    filings = []
    for item in data:
        symbol = item.get('symbol', '').upper()
        if symbol not in watchlist_symbols:
            continue
        pdf_path = item.get('attchmntFile', '')
        filings.append({
            'id':          f"NSE_{item.get('seq_id', '')}",
            'symbol':      symbol,
            'company':     item.get('comp', symbol),
            'category':    item.get('anct', 'Announcement'),
            'description': item.get('desc', ''),
            'pdf_url':     f'https://nseindia.com{pdf_path}' if pdf_path else None,
            'exchange':    'NSE',
            'isin':        item.get('isin', ''),
            'date':        item.get('exchdisstime', ''),
        })
    return filings
