import locale, string
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyCBT.common.timezone import parse_tz, timezone_shift


BASE_URL = "https://www.investing.com/economic-calendar/{calendar}-{id}"
TABLE_ID = "eventHistoryTable{id}"
SHOW_MORE_ID = "showMoreHistory{id}"


class table_has_changed_from(object):
    """An expectation for checking the table has changed.

    Parameters
    ----------
    locator: tuple
        value pair like (By.ID, "id_value") used to find the table
    current: <type: table>
        previus version of the table to compare to
    """
    def __init__(self, locator, current):
        self.locator = locator
        self.current_length = len(current.find_elements_by_css_selector("tbody tr"))

    def __call__(self, browser):
        new_table = browser.find_element(*self.locator)
        new_length = len(new_table.find_elements_by_css_selector("tbody tr"))
        if self.current_length < new_length:
            return new_table
        else:
            return False

def _get_table(browser, id):
    table = browser.find_element(By.ID, TABLE_ID.format(id=id))
    date_str = table.find_element_by_css_selector("tbody tr:last-child td").text
    date = parse_tz(
        datetime_str=date_str,
        in_tz="America/New_York",
        replace_pattern=(r"^\w{3}", r"\(\w{3}\)"),
        parse_quarter=True
    )
    return table, date

def _parse_units(series):
    """Returns a dataframe with numeric column.
    """
    mult = {
        "K": 1000.0,
        "M": 1000000.0,
        "%": 1.0
    }
    series = series.apply(lambda cell: eval(cell.strip(cell[-1]))*mult[cell[-1]] if type(cell) == str else cell)
    return series

def get_calendar(*args, **kwargs):
    locale.setlocale(locale.LC_TIME, "en_US")
    from_date = parse_tz(kwargs.get("from_date"), in_tz=kwargs.get("timezone"))
    to_date = parse_tz(kwargs.get("to_date"), in_tz=kwargs.get("timezone"))

    _ = kwargs.get("calendar").split("-")
    calendar, id = string.join(_[:-1], "-"), _[-1]

    browser = webdriver.Chrome()
    browser.get(BASE_URL.format(calendar=calendar, id=id))

    cal_table, last_record_date = _get_table(browser, id)

    wait = WebDriverWait(browser, 10)
    while last_record_date > from_date:
        try:
            show_more = wait.until(EC.element_to_be_clickable((By.ID, SHOW_MORE_ID.format(id=id))))
        except:
            if not show_more.is_displayed(): break
        else:
            browser.execute_script("arguments[0].click();", show_more)
            cal_table, last_record_date = _get_table(browser, id)

    table = pd.read_html(u"<table>"+cal_table.get_attribute("innerHTML")+u"</table>")[0]
    table.insert(0, "Datetime", value=table["Release Date"]+" "+table["Time"])
    better = map(lambda span: "better" in span.get_attribute("title").lower() if span.get_attribute("title").strip() else None, cal_table.find_elements_by_css_selector("tbody tr td:nth-child(3) span"))
    table.insert(table.columns.size, "Better", value=better)
    table["Datetime"] = table["Datetime"].apply(
        timezone_shift,
        args=(
            "America/New_York",
            kwargs.get("timezone"),
            kwargs.get("datetime_format"),
            None,
            (r"^\w{3}", r"\(\w{3}\)")
        )
    )
    mask = [not (from_date <= parse_tz(release_date, in_tz=kwargs.get("timezone")) <= to_date) for release_date in table["Datetime"]]
    table.drop(table.index[mask], axis="index", inplace=True)
    table.drop(["Release Date", "Time", "Unnamed: 5"], axis="columns", inplace=True)
    table.set_index("Datetime", inplace=True)

    table = table.apply(_parse_units)
    locale.resetlocale(locale.LC_TIME)
    return table
