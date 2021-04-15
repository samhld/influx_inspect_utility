import inspect_util.db_util as util
import config as cfg
from influx_line_protocol import Metric

dbrp_path = cfg.dbrp_path
shard_names = util.load_shard_names(dbrp_path)
file_paths = util.load_file_paths(dbrp_path)
# per_block = False

if cfg.loop:
    while True:
        inspections = [util.inspect(file_path) for file_path in file_paths]
        all_lines = []
        for insp in inspections:
            if isinstance(lines, Metric):
                print(lines)
            else:
                all_lines += lines

        batch = ""
        for line in all_lines:
            batch += f"{line}\n"
        print(batch)


else:
    inspections = [util.inspect(file_path) for file_path in file_paths]

    all_lines = []
    for insp in inspections:
        lines = util.create_lines(insp, per_block=cfg.per_block)
        if isinstance(lines, Metric):
            print(lines)
        else:
            all_lines += lines

    batch = ""
    for line in all_lines:
        batch += f"{line}\n"
    print(batch)