import os
import subprocess
import pytest

# Paths
# v1 tsm
V1_DBRP_PATH = "/Users/samdillard/.influxdb/data/telegraf/autogen"
V1_SHARD_PATH = f"{V1_DBRP}/106"
V1_FILE_PATH = f"{V1_SHARD}/000000006-000000002.tsm"

#v2 tsm
V2_DBRP = "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/autogen"
V2_SHARD = f"{V1_DBRP}/1"
V2_FILE = f"{V1_SHARD}/000000006-000000002.tsm"

# v2 tsi index
V2_SERIES_DIR = "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/_series"
V2_TSI_DBRP = "/Users/samdillard/.influxdbv2/engine/data/1dfa96ad98401b9c/autogen/1"
V2_TSI_SHARD = f"{V2_TSI_DBRP}/1"
V2_TSI_FILE = "{V2_TSI_SHARD}/index/7/L0-00000001.tsl"

# @pytest
