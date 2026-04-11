from datetime import datetime
from zoneinfo import ZoneInfo
from config import Config

def get_now():
    """
    Retorna o datetime atual no timezone configurado no .env (APP_TIMEZONE).
    Se não houver timezone configurado ou for inválido, cai para UTC.
    """
    try:
        from config import Config
        tz = ZoneInfo(Config.APP_TIMEZONE)
    except Exception:
        # Fallback para UTC se o timezone for inválido ou tzdata estiver ausente
        tz = ZoneInfo("UTC")
    
    return datetime.now(tz).replace(tzinfo=None)

def to_utc(dt: datetime):
    """
    Converte um datetime (naive ou aware) para UTC.
    """
    if dt.tzinfo is None:
        # Assume que o naive dt está no timezone da app
        try:
            tz = ZoneInfo(Config.APP_TIMEZONE)
        except Exception:
            tz = ZoneInfo("America/Sao_Paulo")
        dt = dt.replace(tzinfo=tz)
    
    return dt.astimezone(ZoneInfo("UTC"))
