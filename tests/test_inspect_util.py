import pytest
import sys
print(sys.path)
from inspect_util.db_util import Block, TSMFile

# Paths
# v1 tsm
v1_dbrp = "/Users/samdillard/.influxdb/data/telegraf/autogen"
v1_shard = f"{v1_dbrp}/106"
v1_file = f"{v1_shard}/000000006-000000002.tsm"

#v2 tsm
v2_dbrp= "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/autogen"
v2_shard = f"{v2_dbrp}/1"
v2_file = f"{v2_shard}/000000006-000000002.tsm"

# v2 tsi index
v2_series_dir = "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/_series"
v2_tsi_dbrp = "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/autogen/1"
v2_tsi_shard = f"{v2_tsi_dbrp}/1"
v2_tsi_file = f"{v2_tsi_shard}/index/7/L0-00000001.tsl"

# @pytest
def test_constructor():
    b = Block()
    assert len(b) == 0
    t = TSMFile()
    assert len(t) == 0

def test_gather():
    inspect_output = gather()
    assert len(inspect_output) > 0 
