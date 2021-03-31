from os import listdir
import subprocess
import datetime
from dataclasses import dataclass

DBRP_DIR = "/Users/samdillard/.influxdb/data/telegraf/autogen"

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
    blk: int
    chk: int
    offs: int
    blen: int
    dtype: str
    min_time: datetime.datetime
    max_time: datetime.datetime
    pts: int
    enc: str
    tag_len: int
    val_len: int

@dataclass
class TSMFile:
    blks: int
    idx_size: int
    min_blk: int
    max_blk: int
    idx_type: str


    

for file_path in load_file_paths(DBRP_DIR):
    subprocess.run(f"influx_inspect dumptsm -blocks {file_path}", shell=True)
    
    

