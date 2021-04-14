import os
import inspect_util.db_util as util
from influx_line_protocol import Metric
import config as cfg

cwd = os.getcwd()
tsm_file_path=f"{cwd}/tests/211/000000001-000000001.tsm"
dbrp_path = cfg.dbrp_path
shard_names = util.load_shard_names(dbrp_path)
file_paths = util.load_file_paths(dbrp_path)

per_block = cfg.per_block

# def test_get_per_file_lines_per_file():
#     inspections = [util.inspect(file_path) for file_path in file_paths]
#     all_tsm_file_lines = []
#     for insp in inspections:
#         line = util.create_lines(insp)
#         all_tsm_file_lines += line
#     if len(file_paths) > 1:
#         assert len(all_tsm_file_lines) > 1
#     elif len(file_paths) == 1:
#         assert len(all_tsm_lines) == 1
