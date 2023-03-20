from enum import Enum

import beautiful_date as BD

class DateUnit(Enum):
    DAYS = 1
    WEEKS = 2
    BIWEEK = 3
    MONTHS = 4
    YEARS = 5

DATE_TYPE_STR_MAP = {
    'day': DateUnit.DAYS, 
    'week': DateUnit.WEEKS, 
    'biweek': DateUnit.BIWEEK, 
    'month': DateUnit.MONTHS, 
    'year': DateUnit.YEARS, 
}

def get_date_increment(date_unit: DateUnit):
    mapping = {
        DateUnit.DAYS: 1 * BD.days,
        DateUnit.WEEKS: 1 * BD.weeks,
        DateUnit.BIWEEK: 2 * BD.weeks,
        DateUnit.MONTHS: 1 * BD.months,
        DateUnit.YEARS: 1 * BD.years,
    }
    return mapping[date_unit]