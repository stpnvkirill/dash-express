import datetime
# Функции фильтрации данных

def select_filters(serias, value):
    return serias == value


def multiselect_filters(serias, value):
    return serias.isin(value)

def range_filters(serias, value):
    return (serias >= value[0]) & (serias <= value[1])

def dateselect_filters(serias, value):
    value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
    return serias.dt.floor('d') == value

def daterange_filters(serias, value):
    # value = [datetime.datetime.strptime(v, '%Y-%m-%d').date() for v in value]
    return  (serias >= value[0]) & (serias <= value[1])