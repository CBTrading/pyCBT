import re, locale, string
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyCBT.common.timezone import parse_tz, timezone_shift

locale.setlocale(locale.LC_ALL, "en_US")


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

class EconomicCalendar(object):
    URL = "https://www.investing.com/economic-calendar/{calendar}-{id}"
    TABLE_ID = "eventHistoryTable{id}"
    SHOW_MORE_ID = "showMoreHistory{id}"

    def __init__(self, calendar, from_date, to_date, datetime_format="%Y-%m-%d", browser=None):
        self.timezone = "America/New_York"
        self.datetime_format = datetime_format
        self.from_date = parse_tz(from_date, in_tz=self.timezone)
        self.to_date = parse_tz(to_date, in_tz=self.timezone)

        _ = calendar.split("-")
        self.calendar, self.id = string.join(_[:-1], "-"), _[-1]

        self.browser = webdriver.Chrome() if not browser else browser

        self.html_table = None
        self.table = None

    def _filter_html(self):
        table = self.browser.find_element(By.ID, self.TABLE_ID.format(id=self.id))
        date = parse_tz(
            datetime_str=table.find_element_by_css_selector("tbody tr:last-child td").text,
            in_tz=self.timezone,
            remove_pattern=r"\(Q\d\)",
            replace_pattern=(r"^\w{3}", r"\(\w{3}\)")
        )
        return table, date

    def _parse_units(self, series):
        """Returns a dataframe with numeric column.
        """
        unit = {
            "K": 1000.0,
            "M": 1000000.0,
            "%": 1.0
        }
        series = series.apply(lambda cell: locale.atof(cell.strip(cell[-1]))*unit.get(cell[-1], 1.0)
                                if type(cell) == str else cell)
        return series

    def set_html_table(self):
        self.browser.get(self.URL.format(calendar=self.calendar, id=self.id))

        html_table, last_record_date = self._filter_html()

        wait = WebDriverWait(self.browser, 10)
        while last_record_date > self.from_date:
            try:
                show_more = wait.until(EC.element_to_be_clickable((By.ID, self.SHOW_MORE_ID.format(id=self.id))))
            except:
                if not show_more.is_displayed(): break
            else:
                self.browser.execute_script("arguments[0].click();", show_more)
                html_table, last_record_date = self._filter_html()

        self.html_table = html_table

        return None

    def as_dataframe(self, index_name="Date"):
        # check if already defined
        if self.table: return self.table
        # parse HTML
        if not self.html_table: self.set_html_table()

        table, = pd.read_html(u"<table>{}</table>".format(self.html_table.get_attribute("innerHTML")))
        # parse dates
        table.insert(0, index_name, value=table["Release Date"]+" "+table["Time"])
        if re.search(r"\(Q\d\)", table["Release Date"][0]):
            quarter = table["Release Date"].apply(
                                                lambda dt: eval(re.findall(r"\(Q\d\)", dt)[0].strip("(Q)"))
                                                if re.search(r"\(Q\d\)", datetime_str) else None
            )
            table.insert(loc=1, column="Quarter", value=quarter)
        table[index_name] = table[index_name].apply(
            timezone_shift,
            args=(
                self.timezone,
                self.timezone,
                self.datetime_format,
                r"\(Q\d\)", (r"^\w{3}",r"\(\w{3}\)")
            )
        )
        # insert better
        better = map(lambda span: "better" in span.get_attribute("title").lower()
                        if span.get_attribute("title").strip()
                        else None, self.html_table.find_elements_by_css_selector("tbody tr td:nth-child(3) span"))
        table.insert(table.columns.size, "Better", value=better)
        # filter by date range & cleaning
        mask = [not (self.from_date <= parse_tz(rd, in_tz=self.timezone) <= self.to_date) for rd in table[index_name]]
        table.drop(table.index[mask], axis="index", inplace=True)
        table.drop(["Release Date", "Time", "Unnamed: 5"], axis="columns", inplace=True)
        # set index
        table.set_index(index_name, inplace=True)
        table.sort_index(inplace=True)

        self.table = table.apply(self._parse_units)
        return self.table
