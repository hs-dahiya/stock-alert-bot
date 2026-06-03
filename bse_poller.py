import requests

BSE_API = (
    'https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w'
    '?pageno=1&strCat=-1&strPrevDate=&strScrip=&strSearch=P'
    '&strToDate=&strType=C&subcategory=-1'
)
BSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer':    'https://www.bseindia.com/',
}

def poll_bse(watchlist_bse_codes: set) -> list:
    try:
        resp = requests.get(BSE_API, headers=BSE_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json().get('Table', [])
    except Exception as e:
        print(f'[BSE] Poll failed: {e}')
        return []

    filings = []
    for item in data:
        code = str(item.get('SCRIP_CD', '')).strip()
        if code not in watchlist_bse_codes:
            continue
        attach = item.get('ATTACHMENTNAME', '')
        pdf_url = f'https://www.bseindia.com/xml-data/corpfiling/AttachLive/{attach}' if attach else None
        filings.append({
            'id':          f"BSE_{item.get('NEWSID', '')}",
            'symbol':      item.get('SLONGNAME', code),
            'company':     item.get('SLONGNAME', ''),
            'category':    item.get('CATEGORYNAME', 'Announcement'),
            'description': item.get('HEADLINE', ''),
            'pdf_url':     pdf_url,
            'exchange':    'BSE',
            'isin':        item.get('ISIN_CODE', ''),
            'date':        item.get('NEWS_DT', ''),
            'bse_code':    code,
        })
    return filings
