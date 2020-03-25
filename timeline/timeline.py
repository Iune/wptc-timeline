from joblib import Parallel, delayed
from tqdm import tqdm

from breakpoints import load_breakpoints
from hurdat import load_hurdat

import argparse

def write_output(output_file_path, storms, breakpoints):
    def get_record_output(storm, record):
        nearest_bp = record.get_nearest_breakpoint(breakpoints)
        line = [
            storm.storm_id,
            storm.name,
            record.date.strftime("%Y-%m-%d %H:%M"),
            record.record_identifier,
            record.phase,
            str(record.latitude),
            str(record.longitude),
            str(record.winds),
            str(record.pressure),
            nearest_bp["breakpoint"].name,
            nearest_bp["breakpoint"].state,
            nearest_bp["breakpoint"].country,
            str(round(nearest_bp["distance"].mi, 0)),
            str(round(nearest_bp["distance"].km, 0)),
            nearest_bp["direction"],
        ]
        return line

    records = [(storm, record) for storm in storms for record in storm.records]
    lines = Parallel(n_jobs=4)(delayed(get_record_output)(storm, record) for (storm, record) in tqdm(records))
    lines = sorted(lines, key = lambda x: [x[0], x[2]])
        
    with open(output_file_path, "w") as f:
        header = [
            "Storm",
            "Name",
            "Date",
            "Record Identifier",
            "Type",
            "Latitude",
            "Longitude",
            "Winds",
            "Pressure",
            "Breakpoint",
            "State",
            "Country",
            "Miles",
            "Kilometers",
            "Direction"
        ]
        f.write("{}\n".format("\t".join(header)))
        for line in lines:
            f.write("{}\n".format("\t".join(line)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input hurdat2 file location")
    parser.add_argument("-o", "--output", help="Output tsv file location")
    parser.add_argument("-y", "--year", help="Year to process", type=int, required=True)
    args = parser.parse_args()

    breakpoints_file_path = "resources/breakpoints/breakpoints.shp"
    breakpoints = load_breakpoints(breakpoints_file_path)

    storms = list(filter(lambda storm: storm.year == args.year, load_hurdat(args.input)))
    write_output(args.output, storms, breakpoints)

if __name__ == "__main__":
    main()
