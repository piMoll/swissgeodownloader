from datetime import datetime

def formatCoordinate(number):
    """Format big numbers with thousand separator, swiss-style"""
    if number is None:
        return ''
    # Format big numbers with thousand separator
    elif number >= 1000:
        return f"{number:,.0f}".replace(',', "'")
    else:
        return f"{number:,.6f}"
    

def castToNum(formattedNum):
    """Casts formatted numbers back to floats"""
    if type(formattedNum) in [int, float]:
        return formattedNum
    try:
        num = float(formattedNum.replace("'", ''))
    except (ValueError, AttributeError):
        num = None
    return num

def filesizeFormatter(num, suffix='B'):
    """Formats data sizes to human readable units"""
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def getDateFromIsoString(isoString):
    """Translate ISO date string to swiss date format"""
    if isoString[-1] == 'Z':
        isoString = isoString[:-1]
    dt = datetime.fromisoformat(isoString)
    return dt.strftime('%d.%m.%Y')
