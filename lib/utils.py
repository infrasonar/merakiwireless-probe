import time
from typing import Optional


def datetime_to_timestamp(val: Optional[str]) -> Optional[int]:
    if not isinstance(val, str):
        return
    d_fmt = '%Y/%m/%d %H:%M:%S'
    n_chars = 19
    try:
        return int(time.mktime(time.strptime(val[:n_chars], d_fmt)))
    except Exception:
        return None


def datefmt_to_timestamp(val: Optional[str], fmt: str) -> Optional[int]:
    if not isinstance(val, str):
        return
    try:
        return int(time.mktime(time.strptime(val.strip(), fmt)))
    except Exception:
        return None


def uptime_seconds(val: Optional[str]) -> Optional[int]:
    if not isinstance(val, str):
        return
    lst = val.split(' days, ')
    days = int(lst[0]) if len(lst) > 1 else 0
    seconds = sum(
        a * b
        for a, b in zip((3600, 60, 1), map(int, lst[-1].split(':'))))
    return 86400 * days + seconds


def to_int(val: Optional[str]) -> Optional[int]:
    try:
        assert val is not None
        return int(val)
    except Exception:
        return None


def to_bool(val: Optional[str]) -> Optional[bool]:
    return True if val == 'True' else False if val == 'False' else None
