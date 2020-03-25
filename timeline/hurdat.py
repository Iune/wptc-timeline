from dataclasses import dataclass
from typing import List, Type
from datetime import datetime

from geopy.distance import distance
from joblib import Parallel, delayed
from bearing import calculate_initial_compass_bearing as get_bearing

import csv

@dataclass
class Record:
    date: str
    record_identifier: str
    phase: str
    latitude: float
    longitude: float
    winds: int
    pressure: int

    def get_nearest_breakpoint(self, breakpoints):
        def bearing_to_direction(bearing):
            # From: https://gist.github.com/RobertSudwarts/acf8df23a16afdb5837f, by @Lauszus
            dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
            ix = round(bearing / (360. / len(dirs)))
            return dirs[ix % len(dirs)]

        def calculate_distance(bp):
            bp_distance = distance((bp.latitude, bp.longitude), (self.latitude, self.longitude))
            bp_bearing = round(get_bearing((bp.latitude, bp.longitude), (self.latitude, self.longitude)), 3)
            bp_direction = bearing_to_direction(bp_bearing)
            return {
                "breakpoint": bp,
                "distance": bp_distance,
                "direction": bp_direction
            }

        # distances = [calculate_distance(bp) for bp in breakpoints]   
        distances = Parallel(n_jobs=4)(delayed(calculate_distance)(bp) for bp in breakpoints)
        return sorted(distances, key = lambda x: x["distance"])[0]

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