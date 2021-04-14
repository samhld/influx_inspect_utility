from os import listdir
import subprocess
import datetime
import re
from dataclasses import dataclass
import typing

v1_dbrp_path = "/Users/samdillard/.influxdb/data/float_int_low_card/autogen"
# For testing
v1_shard_path = f"{v1_dbrp_path}/210" 
v1_file_path = f"{v1_shard_path}/000000001-000000001.tsm"

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

def to_lines(tuples):
    lines = []
    for tup in zip(*tuples):
        line = Metric("inspect_tsm")
        for k, v in tup:
            line.add_value(k, v)
            lines.append(line)
        yield line
    return lines

# def format_values(values):
#     formatted = []
#     if values[0].isnumeric():
#         formatted = [int(val) for val in values]
#     for val in values:
#         if val.isnumeric():
        


@dataclass
class Block:
    block: int
    checksum: int
    offset: int
    block_length: int
    data_type: str
    min_time: datetime.datetime
    max_time: datetime.datetime
    points: int
    encoding: str
    tag_length: int
    # tag_val_length: int

    def __len__(self):
        return len(self.__dict__)

@dataclass
class TSMFile:
    blks: int
    idx_size: int
    min_blk: int
    max_blk: int
    idx_type: str
    pts_per_blk: int
    bytes_per_point_block: int
    bytes_per_point_file: int

    def __len__(self):
        return len(self.__dict__)

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

@dataclass
class BlockInspection:
    file_name: str
    shard: str
    block_id: str
    offset: int
    length: int
    dtype: int
    min_time: str # datetime or int maybe?
    points: int
    encodings: str
    '''
    TO DO: split the encoding columns into below values
    # time_encoding: str
    # value_encoding: str
    # time_encoding_length: int
    # value_encoding_length: int
    '''

    
# def clean_collection(text):
#     text = text.splitlines()
#     parse_header(text)

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

    # for key, values in body_dict
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
    for val in values:
        t_val, v_val = val.split(delim)
        t_vals.append(t_val)
        v_vals.append(v_val)
    return t_vals, v_vals

# def split_dict_values(dictionary):
#     for key, values in dictionary.items():
#         if key in 

def inspect(v1_file) -> TSMInspection:
    proc = subprocess.run(f"influx_inspect dumptsm -blocks {v1_file}",
                          shell=True,
                          stdout=subprocess.PIPE,
                          text=True)

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
    print(f"raw_rows 1: {raw_rows[0]}")
    cleaned_rows = parse_body_rows(raw_rows)
    body = create_body_dict(headers, cleaned_rows)
    body = format_values(body) # infer numerics and time
    

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
    if per_block:
        tups = to_tuples(insp.body)
        lines = to_lines(tups)

    return lines





