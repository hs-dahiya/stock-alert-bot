import requests, os

BOT_TOKEN  = os.environ['TELEGRAM_BOT_TOKEN']
GROUP_ID   = os.environ['TELEGRAM_GROUP_ID']

THREAD_ALERTS    = int(os.environ.get('TELEGRAM_ALERTS_THREAD_ID', 0))
THREAD_DIGEST    = int(os.environ['TELEGRAM_DIGEST_THREAD_ID'])
THREAD_HEARTBEAT = int(os.environ['TELEGRAM_HEARTBEAT_THREAD_ID'])

CATEGORY_EMOJI = {
    'financial results': '📊', 'quarterly results': '📊', 'annual results': '📊',
    'board meeting':     '🏛', 'dividend':          '💰', 'buyback':        '🔁',
    'order':             '📦', 'promoter':          '🔍', 'credit rating':  '📈',
    'shareholding':      '👥', 'insider':           '🔍', 'rights issue':   '📋',
}

def _emoji(category: str) -> str:
    c = category.lower()
    for k, e in CATEGORY_EMOJI.items():
        if k in c: return e
    return '🔔'

def _send(text: str, thread_id: int):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id':    GROUP_ID,
        'text':       text,
        'parse_mode': 'Markdown',
    }
    # Only add thread_id if it's a real topic (non-zero)
    if thread_id:
        payload['message_thread_id'] = thread_id
    r = requests.post(url, json=payload, timeout=10)
    if not r.ok:
        print(f'[Telegram] Send failed: {r.text}')

def send_alert(filing: dict, analysis: str = ''):
    emoji = _emoji(filing.get('category', ''))
    score = filing.get('priority_score', '')
    lines = [
        f"{emoji} *{filing.get('category','').upper()}*  |  {filing.get('exchange','')}  |  Priority: {score}/10",
        f"🏢 {filing.get('company','')}  (`{filing.get('symbol','')}`)",
        f"📋 {filing.get('description','')[:200]}",
    ]
    if analysis:
        lines.append('')
        lines.append(analysis)
    if filing.get('pdf_url'):
        lines.append('')
        lines.append(f"[📄 View Filing]({filing['pdf_url']})")
    _send('\n'.join(lines), THREAD_ALERTS)

def send_raw(text: str, thread: str = 'alerts'):
    thread_id = THREAD_ALERTS if thread == 'alerts' else THREAD_HEARTBEAT
    _send(text, thread_id)

def send_digest(text: str):
    _send(text, THREAD_DIGEST)

def send_heartbeat(text: str):
    _send(text, THREAD_HEARTBEAT)
