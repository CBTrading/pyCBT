import locale, string
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyCBT.common.timezone import parse_tz, timezone_shift

# define the base URL, with formatting options for name of the calendar and id
BASE_URL = "https://www.investing.com/economic-calendar/{calendar}-{id}"
# define base table name (HTML id)
TABLE_ID = "eventHistoryTable{id}"
# define base show more link (HTML id)
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

def get_calendar(*args, **kwargs):
    locale.setlocale(locale.LC_TIME, "en_US")
    from_date = parse_tz(kwargs.get("from_date"), in_tz=kwargs.get("timezone"))
    to_date = parse_tz(kwargs.get("to_date"), in_tz=kwargs.get("timezone"))

    _ = kwargs.get("calendar").split("-")
    calendar, id = string.join(_[:-1], "-"), _[-1]

    browser = webdriver.Chrome()
    browser.get(BASE_URL.format(calendar=calendar, id=id))

    inv_table = browser.find_element(By.ID, TABLE_ID.format(id=id))
    last_date_str = inv_table.find_element_by_css_selector("tbody tr:last-child td").text
    last_record_date = parse_tz(remove_pattern(last_date_str, r"\(\w+\)"), in_tz="America/New_York")

    wait = WebDriverWait(browser, 10)
    while last_record_date > from_date:
        show_more = wait.until(EC.element_to_be_clickable((By.ID, SHOW_MORE_ID.format(id=id))))
        browser.execute_script("arguments[0].click();", show_more)

        inv_table = wait.until(inventory_table_has_changed_from((By.ID, TABLE_ID.format(id=id)), inv_table))
        last_date_str = inv_table.find_element_by_css_selector("tbody tr:last-child td").text
        last_record_date = parse_tz(remove_pattern(last_date_str, r"\(\w+\)"), in_tz="America/New_York")

    table = pd.read_html(u"<table>"+inv_table.get_attribute("innerHTML")+u"</table>")[0]
    table.insert(0, "Datetime", value=table["Release Date"]+" "+table["Time"])
    better = map(lambda span: "better" in span.get_attribute("title").lower() if span.get_attribute("title").strip() else None, inv_table.find_elements_by_css_selector("tbody tr td:nth-child(3) span"))
    table.insert(table.columns.size, "Better", value=better)
    table["Datetime"] = table["Datetime"].apply(remove_pattern, args=(r"\(\w+\)",))
    table["Datetime"] = table["Datetime"].apply(
        timezone_shift,
        args=("America/New_York", kwargs.get("timezone"), kwargs.get("datetime_format"))
    )
    mask = [not (from_date <= parse_tz(release_date, in_tz="America/New_York") <= to_date) for release_date in table["Datetime"]]
    table.drop(table.index[mask], axis="index", inplace=True)
    table.drop(["Release Date", "Time", "Unnamed: 5"], axis="columns", inplace=True)
    table.set_index("Datetime", inplace=True)
    table = table.applymap(lambda cell: eval(cell.strip("KM%")) if type(cell) == str else cell)
    locale.resetlocale(locale.LC_TIME)
    return table
