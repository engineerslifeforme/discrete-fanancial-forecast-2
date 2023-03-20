from decimal import Decimal

import beautiful_date as BD

ZERO = Decimal("0.00")
CENTS = Decimal('.01')
NEGATIVE_ONE = Decimal("-1")

def month_round(date: BD.BeautifulDate) -> BD.BeautifulDate:
    return BD.BeautifulDate(date.year, date.month, 1)

def year_round(date: BD.BeautifulDate) -> BD.BeautifulDate:
    return BD.BeautifulDate(date.year, 1, 1)

def month_int(date: BD.BeautifulDate) -> int:
    return date.year * 12 + date.month

def parse_date(date_str: str) -> BD.BeautifulDate:
    date_parts = [int(value) for value in date_str.split('-')]
    return BD.BeautifulDate(*date_parts)