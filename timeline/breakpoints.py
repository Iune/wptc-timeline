from dataclasses import dataclass
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
