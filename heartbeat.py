import os
from datetime import datetime, timezone, timedelta
from telegram_sender import send_heartbeat

IST              = timezone(timedelta(hours=5, minutes=30))
DAILY_PING_HOUR  = 21  # 9 PM IST

def smart_ping(nse_count: int, bse_count: int, alerts_sent: int,
               errors: list, state: dict) -> dict:
    now_ist = datetime.now(IST)
    today   = now_ist.strftime('%Y-%m-%d')
    last    = state.get('last_daily_ping', '')

    # Error ping — immediate
    if errors:
        msg = (f'⚠️ *Poller Error — {now_ist.strftime("%d-%b %H:%M IST")}*\n'
               + '\n'.join(f'  • {e[:80]}' for e in errors[:5]))
        send_heartbeat(msg)

    # Daily ping — once after 9 PM IST
    if now_ist.hour >= DAILY_PING_HOUR and last != today:
        msg = (f'✅ *Daily Status — {now_ist.strftime("%d-%b-%Y")}*\n'
               f'NSE feed: {nse_count} filings  |  BSE feed: {bse_count} filings\n'
               f'Alerts sent today: {alerts_sent}\n'
               f'System: Running normally')
        send_heartbeat(msg)
        state['last_daily_ping'] = today

    return state
