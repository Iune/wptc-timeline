from dataclasses import dataclass
from typing import List, Type
from datetime import datetime
import csv
import shapefile


@dataclass
class Breakpoint:
    name: str
    state: str
    country: str
    latitude: float
    longitude: float


def load_breakpoints(breakpoints_file_path):
    shape = shapefile.Reader(breakpoints_file_path)
    return [Breakpoint(
        name=record["NAME"].strip(),
        state=record["State"].title().strip(),
        country=record["Country"].title().strip(),
        latitude=record["Latdbl"],
        longitude=record["Longdbl"]
    ) for record in shape.records()]


@dataclass
class Record:
    date: str
    record_identifier: str
    phase: str
    latitude: float
    longitude: float
    winds: int
    pressure: int


@dataclass
class Storm:
    storm_id: str
    name: str
    year: int
    records: List[Type[Record]]


def load_hurdat(hurdat_file_path):
    def is_header(line):
        return True if len(line) == 4 else False

    def get_datetime(line):
        date_string = "{}-{}-{} {}:{} UTC".format(
            line[0][:4], line[0][4:6], line[0][6:8], line[1].strip()[:2], line[1].strip()[2:4])
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M %Z")

    def get_latitude(line):
        lat_str = line[4].strip()
        hemisphere = 1 if lat_str[-1].upper() == "N" else -1
        return float(lat_str[:-1]) * hemisphere

    def get_longitude(line):
        lon_str = line[5].strip()
        hemisphere = 1 if lon_str[-1].upper() == "E" else -1
        return float(lon_str[:-1]) * hemisphere

    def get_pressure(line):
        pressure = int(line[7].strip())
        return None if pressure == -999 else pressure

    with open(hurdat_file_path, "r") as f:
        reader = csv.reader(f)
        storms = []
        for line in reader:
            if is_header(line):
                storms.append(Storm(
                    storm_id=line[0].strip(),
                    name=line[1].strip(),
                    year=int(line[0].strip()[4:8]),
                    records=[])
                )
            else:
                current_storm = storms[-1]
                current_storm.records.append(Record(
                    date=get_datetime(line),
                    record_identifier=line[2].strip(),
                    phase=line[3].strip(),
                    latitude=get_latitude(line),
                    longitude=get_longitude(line),
                    winds=int(line[6].strip()),
                    pressure=get_pressure(line)
                ))
        return storms


def main():
    breakpoints_file_path = "resources/breakpoints/breakpoints.shp"
    breakpoints = load_breakpoints(breakpoints_file_path)
    storms = load_hurdat(
        "resources/hurdat2/hurdat2-nepac-1949-2018-122019.txt")

    current_year = list(filter(lambda storm: storm.year == 2018, storms))
    print(len(current_year))


if __name__ == "__main__":
    main()
