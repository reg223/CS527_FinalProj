import pytest
from arrow import Arrow, api, constants, factory, locales, parser, formatter
from datetime import timedelta  # Importing timedelta to fix the error

def test_arrow_initialization():
    arrow_instance = Arrow(2023, 10, 5, 12, 30, 45)
    assert arrow_instance.year == 2023
    assert arrow_instance.month == 10
    assert arrow_instance.day == 5
    assert arrow_instance.hour == 12
    assert arrow_instance.minute == 30
    assert arrow_instance.second == 45

def test_arrow_now():
    arrow_now = Arrow.now()
    assert arrow_now.year == Arrow.utcnow().year
    assert arrow_now.month == Arrow.utcnow().month
    assert arrow_now.day == Arrow.utcnow().day

def test_arrow_utcnow():
    arrow_utcnow = Arrow.utcnow()
    assert arrow_utcnow.tzinfo is not None
    assert arrow_utcnow.tzinfo.utcoffset(None) == timedelta(0)

def test_arrow_fromtimestamp():
    timestamp = 1633072800  # Corresponds to 2021-10-01 00:00:00 UTC
    arrow_from_timestamp = Arrow.fromtimestamp(timestamp)
    assert arrow_from_timestamp.year == 2021
    assert arrow_from_timestamp.month == 10
    assert arrow_from_timestamp.day == 1

def test_arrow_strptime():
    date_str = '20-01-2019 15:49:10'
    arrow_instance = Arrow.strptime(date_str, '%d-%m-%Y %H:%M:%S')
    assert arrow_instance.year == 2019
    assert arrow_instance.month == 1
    assert arrow_instance.day == 20
    assert arrow_instance.hour == 15
    assert arrow_instance.minute == 49
    assert arrow_instance.second == 10

def test_api_get_now():
    arrow_instance = api.get()
    assert arrow_instance.year == Arrow.utcnow().year
    assert arrow_instance.month == Arrow.utcnow().month
    assert arrow_instance.day == Arrow.utcnow().day

def test_api_get_with_timestamp():
    timestamp = 1633072800  # Corresponds to 2021-10-01 00:00:00 UTC
    arrow_instance = api.get(timestamp)
    assert arrow_instance.year == 2021
    assert arrow_instance.month == 10
    assert arrow_instance.day == 1

def test_api_get_with_string():
    date_str = '2021-10-01T00:00:00'
    arrow_instance = api.get(date_str)
    assert arrow_instance.year == 2021
    assert arrow_instance.month == 10
    assert arrow_instance.day == 1

def test_factory_create_arrow():
    arrow_factory = factory.ArrowFactory()
    arrow_instance = arrow_factory.get(2023, 10, 5)
    assert arrow_instance.year == 2023
    assert arrow_instance.month == 10
    assert arrow_instance.day == 5

def test_formatter_format():
    arrow_instance = Arrow(2023, 10, 5, 12, 30, 45)
    formatted_date = formatter.DateTimeFormatter().format(arrow_instance._datetime, 'YYYY-MM-DD HH:mm:ss')
    assert formatted_date == '2023-10-05 12:30:45'

def test_locales_get_locale():
    locale_instance = locales.get_locale('en')
    assert locale_instance.names[0] == 'en'

def test_parser_parse_iso():
    date_str = '2021-10-12T14:30:00'
    parsed_date = parser.DateTimeParser().parse_iso(date_str)
    assert parsed_date.year == 2021
    assert parsed_date.month == 10
    assert parsed_date.day == 12
    assert parsed_date.hour == 14
    assert parsed_date.minute == 30
