from __future__ import annotations

from dataclasses import dataclass


class Time:
    def __init__(self, hours: int = 0, mins: int = 0) -> None:
        self.mins = (hours * 60) + mins

    def __add__(self, other: Time) -> Time:
        return Time(mins=self.mins + other.mins)

    def __mul__(self, i: int) -> Time:
        return Time(mins=self.mins * i)

    def __str__(self) -> str:
        hours = self.mins // 60
        mins = self.mins % 60
        return f"{hours:02}:{mins:02}"

    def __lt__(self, other: Time) -> bool:
        return self.mins < other.mins

    def __eq__(self, other: Time) -> bool:
        return self.mins == other.mins

    def __le__(self, other: Time) -> bool:
        return (self < other) or (self == other)


class Day:
    MON = "Mon"
    TUES = "Tues"
    WED = "Wed"
    THUR = "Thur"
    FRI = "Fri"

    DAYS = (MON, TUES, WED, THUR, FRI)


@dataclass
class ClassTime:
    """A single block of class time on a day."""

    day: str
    start_time: Time
    end_time: Time

    def __str__(self) -> str:
        return f"{self.day} {self.start_time}-{self.end_time}"

    def overlaps(self, other: ClassTime) -> bool:
        # NOTE: considers one class ending and the other starting at the same time to be overlapping.
        # This may be too restrictive if your schedule is packed.
        same_day = self.day == other.day
        start_in_other = (self.start_time >= other.start_time) and (self.start_time <= other.end_time)
        end_in_other = (self.end_time >= other.start_time) and (self.end_time <= other.end_time)
        return same_day and (start_in_other or end_in_other)


@dataclass
class UnrealizedClass:
    """An unrealized class with options for class times."""

    name: str
    time_options: list[list[ClassTime]]

    def __str__(self) -> str:
        times = "\n".join(", ".join(list(map(str, t))) for t in self.time_options)
        return f"{self.name}\n{times}\n"


def multi_day_same_time(days: tuple[str], start_times: tuple[Time], duration: Time):
    return [[ClassTime(day, start_time, start_time + duration) for day in days] for start_time in start_times]


def multi_times(day: str, start_times: tuple[Time], duration: Time):
    return [[ClassTime(day, start_time, start_time + duration)] for start_time in start_times]


@dataclass
class Class:
    """A realized class with set times."""

    name: str
    times: list[ClassTime]

    def __str__(self) -> str:
        return f"{self.name}: {list(map(str, self.times))}"


def build_schedules(class_options: list[UnrealizedClass]) -> list[list[Class]]:
    schedules = [[]]
    for c in class_options:
        new_schedules = []
        for schedule in schedules:
            fitting_classes = get_fitting_classes(schedule, c)
            for fitting_class in fitting_classes:
                new_schedules.append(schedule.copy() + [fitting_class])
        schedules = new_schedules
    return schedules


def get_fitting_classes(schedule: list[Class], new_class: UnrealizedClass) -> list[Class]:
    fitting_classes = []
    for time_option in new_class.time_options:
        if new_class_time_fits(schedule, time_option):
            fitting_classes.append(Class(new_class.name, time_option))
    return fitting_classes


def new_class_time_fits(schedule: list[Class], new_times: list[ClassTime]) -> bool:
    for new_time in new_times:
        for c in schedule:
            for time in c.times:
                if time.overlaps(new_time):
                    return False
    return True


def print_schedule(schedule: list[Class]) -> None:
    for day in Day.DAYS:
        classes = [(c, t) for c in schedule for t in c.times if t.day == day]
        classes.sort(key=lambda x: x[1].start_time)
        for c, t in classes:
            print(str(t), "\t", c.name)
        print()


if __name__ == "__main__":
    # Define your own classes.
    cse_4502 = UnrealizedClass(
        name="CSE 4502: Big Data Analytics",
        time_options=multi_day_same_time((Day.TUES, Day.THUR), (Time(11), Time(12, 30)), Time(1, 15)),
    )
    cse_4705 = UnrealizedClass(
        name="CSE 4705: Artificial Intelligence",
        time_options=multi_day_same_time((Day.TUES, Day.THUR), (Time(9, 30), Time(14)), Time(1, 15)),
    )
    cse_3000 = UnrealizedClass(
        name="CSE 3000: Contemporary Issues",
        time_options=(
            multi_times(
                Day.MON,
                (Time(10, 10), Time(11, 15), Time(12, 20), Time(13, 25)),
                Time(0, 50),
            )
            + multi_times(Day.WED, (Time(10, 10), Time(11, 15)), Time(0, 50))
        ),
    )

    lecture_times = multi_day_same_time((Day.TUES, Day.THUR), (Time(15, 30), Time(12, 30)), Time(1, 15))
    lab_times = multi_times(Day.MON, (Time(i) for i in range(9, 17)), Time(0, 50))
    cse_3150 = UnrealizedClass(
        name="CSE 3150: C++",
        time_options=[
            lecture_times[int(i >= (len(lab_times) // 2))] + lab_time for (i, lab_time) in enumerate(lab_times)
        ],
    )

    lecture_times = multi_day_same_time((Day.TUES, Day.THUR), (Time(14), Time(12, 30)), Time(1, 15))
    lab_times = multi_times(Day.WED, (Time(13, 25) + (Time(1, 5) * i) for i in range(4)), Time(0, 50)) + multi_times(
        Day.WED, (Time(12, 20) + (Time(1, 5) * i) for i in range(4)), Time(0, 50)
    )
    cse_3666 = UnrealizedClass(
        name="CSE 3666: Intro to Computer Architecture",
        time_options=[
            lecture_times[int(i >= (len(lab_times) // 2))] + lab_time for (i, lab_time) in enumerate(lab_times)
        ],
    )

    discussion_time = [ClassTime(Day.WED, Time(15, 45), Time(17, 45))]
    lecture_time = multi_day_same_time((Day.MON, Day.WED, Day.FRI), (Time(10, 10),), Time(0, 50))[0]
    lab_times = sum(
        [multi_times(day, (Time(9) + (Time(2) * i) for i in range(4)), Time(1, 45)) for day in (Day.TUES, Day.THUR)],
        start=[],
    )
    ece_2001 = UnrealizedClass(
        name="ECE 2001: Circuits",
        time_options=[discussion_time + lecture_time + lab_time for lab_time in lab_times],
    )

    unrealized_classes = [cse_4502, cse_4705, cse_3000, cse_3150, cse_3666, ece_2001]
    for c in unrealized_classes:
        print(c)

    schedules = build_schedules(unrealized_classes)
    print(f"{len(schedules)} schedule options.")
    for i, schedule in enumerate(schedules):
        print("=" * 40)
        print(f"Schedule {i}:")
        print_schedule(schedule)
