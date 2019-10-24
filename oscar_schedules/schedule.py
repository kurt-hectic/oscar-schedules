import datetime
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger()


class Schedule:

    STATUS_OP = "operational"

    def compute_overlap_period_day(self, lower, upper, mydate):
        # check if candidate schedule is possible on the date
        if mydate.month < self.month_from or mydate.month > self.month_to:
            return None
        if mydate.weekday() + 1 < self.week_from or mydate.weekday() + 1 > self.week_to:
            return None

        # check if candidate schedule overlaps with period
        cand_lower = datetime.datetime(
            mydate.year, mydate.month, mydate.day, self.hour_from, self.min_from
        )
        cand_upper = datetime.datetime(
            mydate.year, mydate.month, mydate.day, self.hour_to, self.min_to
        )

        max_lower = max(cand_lower, lower)
        min_upper = min(cand_upper, upper)

        if max_lower <= min_upper:  # overlap
            return {"from": max_lower, "to": min_upper, "interval": self.interval}
        else:
            return None

    def compute_overlap_periods(self, lower, upper):
        logger.debug(
            "computing overlap between schedule {} and period: l:{}, u:{}, month from:{} month to:{} ".format(
                self, lower, upper, self.month_from, self.month_to
            )
        )

        # compute candidate schedules
        schedules = []
        if (
            not self.international or self.status != Schedule.STATUS_OP
        ):  # not international or not operational
            return schedules

        if lower.date() == upper.date():  # period is on same day
            mydate = lower.date()

            s = self.compute_overlap_period_day(lower, upper, mydate)
            if s:
                schedules.append(s)

        else:  # critical period as it overlaps two days

            left_period = self.compute_overlap_period_day(lower, upper, lower.date())
            right_period = self.compute_overlap_period_day(lower, upper, upper.date())

            if (
                left_period and right_period
            ):  # check if valid in both periods. If yes, construct a single period
                if (
                    left_period["to"] + datetime.timedelta(minutes=1)
                    == right_period["from"]
                ):  # continuous
                    s = {
                        "from": left_period["from"],
                        "to": right_period["to"],
                        "interval": right_period["interval"],
                    }
                    schedules.append(s)
                else:  # not continous, need both with gap
                    schedules += [left_period, right_period]
            elif left_period:  # but not right
                schedules.append(left_period)
            elif right_period:  # but not left
                schedules.append(right_period)

        logger.debug("result: {}".format(schedules))

        return schedules

    def create_default_schedule(self):

        return Schedule()

    def __str__(self):
        return "from {month_from}/{week_from} {hour_from}:{min_from}  to: {month_to}/{week_to} {hour_to}:{min_to} interval: {interval}".format(
            **self.__dict__
        )

    def __init__(
        self,
        month_from=1,
        week_from=1,
        hour_from=0,
        min_from=0,
        month_to=12,
        week_to=7,
        hour_to=23,
        min_to=59,
        interval=60 * 60 * 6,
        international=True,
        status=STATUS_OP,
    ):

        if not interval or int(interval) == 0:
            raise ValueError("interval cannot be 0 and must be a number")

        self.month_from = int(month_from)
        self.week_from = int(week_from)
        self.hour_from = int(hour_from)
        self.min_from = int(min_from)

        self.month_to = int(month_to)
        self.week_to = int(week_to)
        self.hour_to = int(hour_to)
        self.min_to = int(min_to)

        self.international = international
        self.status = status
        self.interval = interval
