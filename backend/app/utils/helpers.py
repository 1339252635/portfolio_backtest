from datetime import datetime, date


def parse_date(date_str):
    """解析日期字符串"""
    if isinstance(date_str, date):
        return date_str
    if isinstance(date_str, datetime):
        return date_str.date()
    
    formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%d-%m-%Y']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def format_date(date_obj, fmt='%Y-%m-%d'):
    """格式化日期"""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime(fmt)


def calculate_cagr(begin_value, end_value, years):
    """计算复合年化增长率"""
    if begin_value <= 0 or years <= 0:
        return 0
    return (end_value / begin_value) ** (1 / years) - 1


def format_percentage(value, decimals=2):
    """格式化百分比"""
    return f"{value * 100:.{decimals}f}%"


def format_currency(value, currency='¥', decimals=2):
    """格式化货币"""
    return f"{currency}{value:,.{decimals}f}"
