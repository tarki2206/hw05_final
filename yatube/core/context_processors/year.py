import datetime


def year(request):
    if request:
        year = datetime.datetime.today().year
    return {'year': year}
