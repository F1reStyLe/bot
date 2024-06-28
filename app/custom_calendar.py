from datetime import datetime
import calendar

from aiogram_calendar.schemas import SimpleCalendarCallback, SimpleCalAct, highlight, superscript
from aiogram_calendar import SimpleCalendar
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def busy_highlight(text):
    return f'*{text}*'

class CustomCalendar(SimpleCalendar):

    async def start_calendar(
        self,
        year: int = datetime.now().year,
        month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with the provided year and month
        :param int year: Year to use in the calendar, if None the current year is used.
        :param int month: Month to use in the calendar, if None the current month is used.
        :return: Returns InlineKeyboardMarkup object with the calendar.
        """

        today = datetime.now()
        now_weekday = self._labels.days_of_week[today.weekday()]
        now_month, now_year, now_day = today.month, today.year, today.day

        def highlight_month():
            month_str = self._labels.months[month - 1]
            if now_month == month and now_year == year:
                return highlight(month_str)
            return month_str

        def highlight_weekday():
            if now_month == month and now_year == year and now_weekday == weekday:
                return highlight(weekday)
            return weekday

        def format_day_string():
            date_to_check = datetime(year, month, day)
            if self.min_date and date_to_check < self.min_date:
                return superscript(str(day))
            elif self.max_date and date_to_check > self.max_date:
                return superscript(str(day))
            return str(day)


        def highlight_day():
            day_string = format_day_string()
            busy_days = ["1","2","3"]

            if day_string in busy_days:
                return busy_highlight(day_string)
            if now_month == month and now_year == year and now_day == day:
                return highlight(day_string)
            return day_string

        # building a calendar keyboard
        kb = []

        # First row - Year
        years_row = []
        years_row.append(InlineKeyboardButton(
            text="<<",
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.prev_y, year=year, month=month, day=1).pack()
        ))
        years_row.append(InlineKeyboardButton(
            text=str(year) if year != now_year else highlight(year),
            callback_data=self.ignore_callback
        ))
        years_row.append(InlineKeyboardButton(
            text=">>",
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.next_y, year=year, month=month, day=1).pack()
        ))
        kb.append(years_row)

        # Month nav Buttons
        month_row = []
        month_row.append(InlineKeyboardButton(
            text="<",
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.prev_m, year=year, month=month, day=1).pack()
        ))
        month_row.append(InlineKeyboardButton(
            text=highlight_month(),
            callback_data=self.ignore_callback
        ))
        month_row.append(InlineKeyboardButton(
            text=">",
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.next_m, year=year, month=month, day=1).pack()
        ))
        kb.append(month_row)

        # Week Days
        week_days_labels_row = []
        for weekday in self._labels.days_of_week:
            week_days_labels_row.append(
                InlineKeyboardButton(text=highlight_weekday(), callback_data=self.ignore_callback)
            )
        kb.append(week_days_labels_row)

        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)

        for week in month_calendar:
            days_row = []
            for day in week:
                if day == 0:
                    days_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
                    continue
                days_row.append(InlineKeyboardButton(
                    text=highlight_day(),
                    callback_data=SimpleCalendarCallback(act=SimpleCalAct.day, year=year, month=month, day=day).pack()
                ))
            kb.append(days_row)

        # nav today & cancel button
        cancel_row = []
        cancel_row.append(InlineKeyboardButton(
            text=self._labels.cancel_caption,
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.cancel, year=year, month=month, day=day).pack()
        ))
        cancel_row.append(InlineKeyboardButton(text=" ", callback_data=self.ignore_callback))
        cancel_row.append(InlineKeyboardButton(
            text=self._labels.today_caption,
            callback_data=SimpleCalendarCallback(act=SimpleCalAct.today, year=year, month=month, day=day).pack()
        ))
        kb.append(cancel_row)
        return InlineKeyboardMarkup(row_width=7, inline_keyboard=kb)
