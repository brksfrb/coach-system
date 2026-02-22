from datetime import date as pydate, datetime as dt
from .configs import Hour

days_of_week_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
days_of_week_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

def en_to_tr_day(eng_day: str) -> str:
    """Return the Turkish translation of an English weekday name."""
    try:
        index = days_of_week_en.index(eng_day.lower())
        return days_of_week_tr[index]
    except ValueError:
        return eng_day  # fallback if not found

class CustomDate:
    def __init__(self, day, month, year):
        self._day = day
        self._month = month
        self._year = year
        self._month_mappings = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }
        self._month_mappings_tr = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }
    def __repr__(self):
        return f"{self.day_as_int}/{self.month_as_int}/{self.year_as_int}"
    def __eq__(self, other):
        if isinstance(other, CustomDate):
            return (self._day, self._month, self._year) == (other.day, other.month, other.year)
        else: return False
    def __lt__(self, other):
        if isinstance(other, CustomDate):
            return (self._day, self._month, self._year) < (other.day, other.month, other.year)
        else: return False

    def __hash__(self):
        return hash((self.year, self.month, self.day))

    @classmethod
    def date_to_customdate(self, dt: pydate) -> 'CustomDate':
        """Convert a datetime.date object to a CustomDate object."""
        return CustomDate(day=dt.day, month=dt.month, year=dt.year)
    @property
    def day_as_int(self):
        return self._day

    @property
    def day_as_name(self):
        """Return weekday name like 'Monday', 'Tuesday', etc."""
        dt = pydate(self._year, self._month, self._day)
        return dt.strftime("%A").lower()  # %A gives full weekday name

    @property
    def day_as_turkish_name(self):
        """Return Turkish weekday name."""
        mapping = {
            "monday": "pazartesi",
            "tuesday": "salı",
            "wednesday": "çarşamba",
            "thursday": "perşembe",
            "friday": "cuma",
            "saturday": "cumartesi",
            "sunday": "pazar"
        }
        return mapping.get(self.day_as_name, self.day_as_name)

    @property
    def month_as_int(self):
        return self._month
    @property
    def month_as_name(self):
        return self._month_mappings.get(self._month)
    @property
    def month_as_turkish_name(self):
        return self._month_mappings_tr.get(self._month)
    @property
    def year_as_int(self):
        return self._year
    @property
    def day(self):
        return self._day
    @property
    def month(self):
        return self._month
    @property
    def year(self):
        return self._year

def get_today():
    today = pydate.today()
    return CustomDate(today.day, today.month, today.year)

def get_now():
    now = dt.now()
    return Hour(hour=f"{now.hour:02}", minute=f"{now.minute:02}")

def str_to_date(date_str: str) -> CustomDate | None:
    """
    Convert 'YYYY-MM-DD' string into Date object.
    Returns None if input is None or invalid.
    """
    if not date_str:
        return None

    if not isinstance(date_str, str):
        try:
            date_str = str(date_str)
        except Exception:
            return None

    try:
        year, month, day = map(int, date_str.split("-"))
        return CustomDate(day, month, year)  # or datetime.date(year, month, day)
    except (ValueError, AttributeError):
        return None