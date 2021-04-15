from os import listdir, getcwd
import subprocess
import datetime
import re
from dataclasses import dataclass
from influx_line_protocol import Metric

# For testing
# v1_shard_path = f"{v1_dbrp_path}/210" 
# v1_file_path = f"{v1_shard_path}/000000001-000000001.tsm"

def load_shard_names(dbrp_path):
    shard_names = listdir(dbrp_path)
    return shard_names

def load_filenames(shard_path):
    files = listdir(shard_path)
    return files

def load_shard_paths(dbrp_path):
    paths = []
    for name in load_shard_names(dbrp_path):
        paths.append(f"{dbrp_path}/{name}/")
    return paths

def load_file_paths(dbrp_path):
    file_paths = []
    for shard_path in load_shard_paths(dbrp_path):
        for name in load_filenames(shard_path):
            if name.endswith(".tsm"):
                file_paths.append(shard_path+name)
    return file_paths

def to_tuples(dictionary):
    for header, vals in dictionary.items():
        tups = []
        for val in vals:
            tups.append((header, val))
        yield tups

def to_lines(tuples, per_block=True):
    lines = []
    if per_block:
        for tup in zip(*tuples):
            line = Metric("inspect_block")
            for k, v in tup:
                if k == 'blk':
                    line.add_tag(k, v)
                else:
                    line.add_value(k, v)
                lines.append(line)
            yield line
    return lines

def create_timestamp(precision = 's'):
    '''
    Generates a timestamp to be used at end of line of Line Protocol.
    The precision can be set to seconds, milliseconds, microseconds, or nanoseconds.
    Less precision is achieved with rounding the timestamp to the passed precison
    and then adding zeros as  necessary to keep the timestamp length constant.
    '''
    now  = datetime.datetime.now()
    ts = now.timestamp()
    if precision == ('s' or 'S'):
        ts = round(ts)
        return(ts*10**9)
    elif precision == ('ms' or 'MS'):
        ts = round(ts*10**3)
        return(ts*10**6)
    elif precision == ('us' or 'US'):
        ts = round(ts*10**6)
        return(ts*10**3)
    elif precision == ('ns' or 'NS'):
        ts = round(ts*10**9)
        return(ts)

@dataclass
class TSMInspection:
    file: str
    db: str
    rp: str
    shard: str
    headers: list
    timespan: str
    duration: str
    series: str
    size: str
    body: dict
    blocks: int
    blocks_size: int
    min_block: int
    max_block: int
    avg_block: int
    index_entries: int
    index_size: int

    def __len__(self):
        return len(self.__dict__)

def parse_header(line: str):
    line_list = line.lstrip().split('\t')
    line_list = [i for i in line_list if i] # remove empties
    return line_list

def get_body_rows(lines: list):
    rows = []
    for line in lines:
        line = line.lstrip()
        if line[0].isnumeric():
            rows.append(line)
    return rows

def parse_body_rows(rows: list):
    parsed_rows = [row.split('\t') for row in rows]
    clean_rows = [tuple(filter(None, row)) for row in parsed_rows]
    return clean_rows

def create_body_dict(headers: list, cleaned_rows: list) -> dict:
    body_dict = dict()
    for i, header, in enumerate(headers):
        body_dict[header] = [row[i] for row in cleaned_rows]

    return body_dict

def str_to_datetime(string):
    dt = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
    return round(dt.timestamp())

def format_values(dictionary):
    new_dict = {}
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    for k, values in dictionary.items():
        if values[0].isnumeric():
            new_values = [int(val) for val in values]
            new_dict[k] = new_values
        elif re.match(pattern, values[0]):
            new_values = [str_to_datetime(val) for val in values]
            new_dict[k] = new_values
        else:
            new_dict[k] = values

    return new_dict

def split_encoding_column(value_list, delim="/"):
    t_vals, v_vals = [], []
    for val in value_list:
        t_val, v_val = val.split(delim)
        t_vals.append(t_val)
        v_vals.append(v_val)
    return t_vals, v_vals

def inspect(v1_file) -> TSMInspection:
    proc = subprocess.run(f"influx_inspect dumptsm -blocks {v1_file}",
                          shell=True,
                          text=True,
                          capture_output=True)

    path_info = v1_file.split("/")
    db = path_info[-4]
    rp = path_info[-3]
    shard = path_info[-2]
    # A bunch of parsing
    inspect_output = proc.stdout
    lines = inspect_output.splitlines()
    file_name = lines[0][-23:]
    timespan = lines[1][-43:]
    duration = lines[2].lstrip().split()[1]
    series = int(lines[2].lstrip().split()[3])
    size = int(lines[2].lstrip().split()[-1])
    
    # Parse core table data
    headers = parse_header(lines[3])
    headers = [header.lower().replace(" ","_").replace("[t/v]", "tv") for header in headers] # format headers

    # Parse per-block raw data
    raw_rows = get_body_rows(lines)
    cleaned_rows = parse_body_rows(raw_rows)
    body = create_body_dict(headers, cleaned_rows)
    body = format_values(body) # infer numerics and time
    # Split encoding columns (i.e. `enc_tv` -> ['time_encoding', 'value_encoding'])
    for key, values in body.copy().items():
        if key == 'enc_tv':
            body['time_encoding'],body['value_encoding'] = split_encoding_column(values)
        if key == 'len_tv':
            body['time_length'], body['value_length'] = split_encoding_column(values)
    del body['enc_tv']
    del body['len_tv']

    # Parse remaining lines with inspection statistics
    rem_lines = lines[(4+len(raw_rows)):] 
    # Per file block stats
    blocks = int(rem_lines[2].lstrip().split()[1])
    blocks_size = int(rem_lines[2].lstrip().split()[3])
    min_block = int(rem_lines[2].lstrip().split()[5])
    max_block = int(rem_lines[2].lstrip().split()[7])
    avg_block = int(rem_lines[2].lstrip().split()[9])
    # Per file index stats
    index_entries = int(rem_lines[4].lstrip().split()[1])
    index_size = int(rem_lines[4].lstrip().split()[3])

    return TSMInspection(file=file_name,
                      db=db,
                      rp=rp,
                      shard=shard,
                      timespan=timespan,
                      duration=duration,
                      series=series,
                      size=size,
                      headers=headers,
                      body=body,
                      blocks=blocks,
                      blocks_size=blocks_size,
                      min_block=min_block,
                      max_block=max_block,
                      avg_block=avg_block,
                      index_entries=index_entries,
                      index_size=index_size)


def create_lines(insp: TSMInspection, per_block=False):
    timestamp = create_timestamp()

    if per_block:
        tups = to_tuples(insp.body)
        per_block_lines = to_lines(tups)
        new_block_lines = []
        for line in per_block_lines:
            line.add_tag('file', insp.file)
            line.add_tag('shard', insp.shard)
            line.with_timestamp(timestamp)
            new_block_lines.append(line)

    file_line = Metric("inspect_tsm")
    file_line.add_tag('file', insp.file)
    file_line.add_tag('db', insp.db)
    file_line.add_tag('rp', insp.rp)
    file_line.add_tag('shard', insp.shard)
    # file_line.add_value('timespan', insp.timespan)
    file_line.add_value('duration', insp.duration)
    file_line.add_value('series', insp.series)
    file_line.add_value('size', insp.size)
    file_line.add_value('min_block', insp.min_block)
    file_line.add_value('max_block', insp.max_block)
    file_line.add_value('avg_block', insp.avg_block)
    file_line.add_value('index_entries', insp.index_entries)
    file_line.add_value('index_size', insp.index_size)
    file_line.with_timestamp(timestamp)


    if per_block:
        lines = []
        for line in new_block_lines:
            lines.append(line)
        lines.append(file_line)
        return lines
    else:
        return file_line





