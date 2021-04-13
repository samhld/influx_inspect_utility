# influx_inspect_utility

## Description

The Inspect Utility is for running the `influx_inspect` InfluxDB disk utility on a regular cadence and writing the results to InfluxDB.  It is designed to be used as an external plugin for Telegraf (*first iteration does not have native ability to write to InfluxDB without Telegraf*).

## Motivation

The `influx_inspect` utility is a fantastic tool for ad hoc looks into the file storage behavior of InfluxDB.  That said, it is a common need to want to compare the state you're seeing now to a state it was in prior to now...and potentially to a state in the future.  Enter time series data!

By running the utility and recording results to a time series database, you can now analyze the changes in this file system behavior over time.  This is important for monitoring the existence of anomalous performance degredation.

## How it works

Ad hoc, a user/admin of InfluxDB might inspect the stats of a file with the below command:
```</path/to/shard/>$ influx_inspect dumptsm -blocks 000000001-000000001.tsm```
This spits out a lot of data (example output shown in "Examples" below).  By default this script trims that data down a lot by not collecting per block information.  If the user/admin opts for per-block data, they can configure this by setting `per-block` true ("Usage" describes this).  

*Note: If configuring per-block data, pay attention to how much data this will actually be.  If you have a heavy workload (lots of files, lots of blocks per file), this could potentially increase cardinality of the InfluxDB instance to which you're writing by many tens of thousands.*

## Usage

### Configuration:
In `config.py`:
```
# dbrp_path = "</path/to/database>
# per-block = "false"
```
Via Telegraf execd plugin:
```
</path/to/python3> </path/to/main.py> [flags]

Flags:
--dbrp_path=<dbrp_path>
--per-block  # calling flag sets to true
```
Telegraf external plugin:
* Version 1.X:
  - In-mem index
    - [parameters for configuration]
  - TSI index
    - [parameters for configuration]
* Version 2.X:
  - [parameters for configuration]

Standalone:
  - TBD


## Examples:

### Input (`per-block = "false"`):
```                                                       
Summary:

  File: 000000001-000000001.tsm
  Time Range: 2021-04-12T17:28:00Z - 2021-04-12T23:59:50Z
  Duration: 6h31m50s   Series: 351   File Size: 274802
Blocks:
  Blk   Chk             Ofs             Len     Type    Min Time                Points  Enc [T/V]       Len [T/V]
  0     1717154842      5               144     int64   2021-04-12T17:28:00Z    1000    s8b/rle         129/12
  1     3368434896      153             26      int64   2021-04-12T20:49:30Z    1000    rle/rle         12/12
  2     1441926726      331             26      int64   2021-04-12T23:36:10Z    143     rle/rle         12/12
  ...........

  1051  3368434896      110241023       26      int64   2021-04-12T20:49:30Z    1000    rle/rle         12/12
  1052  1441926726      110401994       26      int64   2021-04-12T23:36:10Z    143     rle/rle         12/12

Statistics
  Blocks:
    Total: 1053 Size: 161001 Min: 26 Max: 4141 Avg: 152
  Index:
    Total: 1053 Size: 113788
  Points:
    Total: 752136
  Encoding:
    Timestamp:  none: 0 (0%)    s8b: 351 (33%)  rle: 702 (66%) 
    Int:        none: 0 (0%)    s8b: 73 (6%)    rle: 980 (93%) 
  Compression:
    Per block: 0.21 bytes/point
    Total: 0.37 bytes/point

```

### Output (per-block = "false"):
```
inspect_tsm,file=000000001-000000001.tsm,shard_id=211 series=22000i,blocks=1043i,block_data_size=161001i,min_block=26i,max_block=4141i,avg_block=152i,index_entries=1053i,index_size=113788i,points=752136i,int_s8b_compress_pct=6i,int_no_compress_pct=0i,int_rle_compress_pct=93i,timestamp_no_compress_pct=0i,timestamp_s8b_compress_pct=33i,timestamp_rle_compress_pct=66i 1618287395000000000
```

### Input (per-block = "true")

