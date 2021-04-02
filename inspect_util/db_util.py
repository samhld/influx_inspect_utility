from os import listdir
import subprocess
import datetime
from dataclasses import dataclass

v1_dbrp = "/Users/samdillard/.influxdb/data/telegraf/autogen"
# For testing
v1_shard = f"{v1_dbrp}/106" 
v1_file = f"{v1_shard}/000000001-000000001.tsm"

def load_shard_names(dbrp_dir):
    shard_names = listdir(dbrp_dir)
    return shard_names

def load_filenames(shard_dir):
    files = listdir(shard_dir)
    return files

def load_shard_paths(dbrp_dir):
    paths = []
    for name in load_shard_names(dbrp_dir):
        paths.append(f"{dbrp_dir}/{name}/")
    return paths

def load_file_paths(dbrp_dir):
    file_paths = []
    for shard_path in load_shard_paths(dbrp_dir):
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
class RawInspection:
    header: str
    body: str
    file_stats: str

    def __len__(self):
        return len(self.__dict__)

def gather(v1_file):
    proc = subprocess.run(f"influx_inspect dumptsm -blocks {v1_file}",
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    text=True)
    inspect_output = proc.stdout
    return inspect_output



def parse_header(line: str):
    line_list = line.lstrip().split('\t')
    line_list = [i for i in line_list if i] # remove empties
    return line_list


# for file_path in load_file_paths(DBRP_DIR):
#     subprocess.run(f"influx_inspect dumptsm -blocks {file_path}", shell=True)

 

