import pytest
import sys
import datetime
from inspect_util.db_util import Block, TSMFile, gather

# Paths
# v1 tsm
v1_dbrp = "/Users/samdillard/.influxdb/data/telegraf/autogen"
v1_shard = f"{v1_dbrp}/106"
v1_file = f"{v1_shard}/000000001-000000001.tsm"

#v2 tsm
v2_dbrp= "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/autogen"
v2_shard = f"{v2_dbrp}/1"
v2_file = f"{v2_shard}/000000006-000000002.tsm"

# v2 tsi index
v2_series_dir = "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/_series"
v2_tsi_dbrp = "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/autogen/1"
v2_tsi_shard = f"{v2_tsi_dbrp}/1"
v2_tsi_file = f"{v2_tsi_shard}/index/7/L0-00000001.tsl"

block_kwargs = {
                "blk": 0,
                "chk": 000,
                "offs": 500,
                "blk_len": 1_000,
                "dtype": "int",
                "min_time": datetime.datetime.now(),
                "max_time": datetime.datetime.now(),
                "pts": 50,
                "enc": "gorilla",
                "tag_len": 10,
                "tag_val_len": 10
                }

tsmfile_kwargs = {
                "blks": 100,
                "idx_size": 20,
                "min_blk": 40,
                "max_blk": 1_750,
                "idx_type": "in-mem"}
# @pytest
def test_constructor():
    b = Block(*block_kwargs)
    assert len(b) == 11
    t = TSMFile(*tsmfile_kwargs)
    assert len(t) == 5


def test_gather():
    inspect_output = gather(v1_file)
    assert len(inspect_output) > 0
