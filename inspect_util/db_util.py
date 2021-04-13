from os import listdir
import subprocess
import datetime
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
class Inspection:
    file_name: str
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
    block: int=None

    def __len__(self):
        return len(self.__dict__)

def clean_collection(text):
    text = text.splitlines()
    parse_header(text)

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

def inspect(v1_file) -> Inspection:
    proc = subprocess.run(f"influx_inspect dumptsm -blocks {v1_file}",
                          shell=True,
                          stdout=subprocess.PIPE,
                          text=True)

    inspect_output = proc.stdout
    lines = inspect_output.splitlines()
    file_name = lines[0][-23:]
    timespan = lines[1][-43:]
    duration = lines[2].lstrip().split()[1]
    series = int(lines[2].lstrip().split()[3])
    size = int(lines[2].lstrip().split()[-1])
    # Parse core table data
    headers = parse_header(lines[3])
    raw_rows = get_body_rows(lines)
    cleaned_rows = parse_body_rows(raw_rows)
    body = create_body_dict(headers, cleaned_rows)

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

    return Inspection(file_name=file_name,
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



 

