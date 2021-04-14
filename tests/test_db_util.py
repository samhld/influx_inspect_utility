import os
import inspect_util.db_util as util
from influx_line_protocol import Metric

cwd = os.getcwd()
tsm_file_path=f"{cwd}/tests/211/000000001-000000001.tsm"
insp = util.inspect(tsm_file_path)

def test_inspect():
    insp = util.inspect(tsm_file_path)
    assert len(insp) == 17
    type_tests = [type(values[0]) for values in insp.body.values()]
    assert len(list(filter(lambda x: x == int, type_tests))) > 0

def test_create_one_tsm_file_line():
    line = util.create_lines(insp)
    hasattr(line, 'tags')
    hasattr(line, 'timestamp')
    hasattr(line, 'measurement')
    hasattr(line, 'values')

def test_create_tsm_and_block_level_lines():
    lines = util.create_lines(insp, per_block=True)
    assert len(lines) > 1