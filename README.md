# influx_inspect_utility

## Description

The Inspect Utility is for running the `influx_inspect` InfluxDB disk utility on a regular cadence and writing the results to InfluxDB.  It is designed to be used as an external plugin for Telegraf (*first iteration does not have native ability to write to InfluxDB without Telegraf*).

## Motivation

The `influx_inspect` utility is a fantastic tool for ad hoc looks into the file storage behavior of InfluxDB.  However, it only provides a look at a single state.  There is also a need to compare the state you're seeing now to a state it was in prior to now...and a state in the future.  Enter time series data!

By running the utility and recording results to a time series database, you can now analyze the changes in TSM file system behavior over time.  This is important for monitoring and catching anomalous storage performance degredation.

## How it works

Ad hoc, a user/admin of InfluxDB might inspect the stats of a file with the below command:
```</path/to/shard/>$ influx_inspect dumptsm -blocks 000000001-000000001.tsm```
This spits out a lot of data (example output shown in "Examples" below).  By default this script trims that data down a lot by not collecting per block information.  If the user/admin opts for per-block data, they can configure this by setting `per-block` true ("Usage" describes this).  

*Note: If configuring per-block data, pay attention to how much data this will actually be.  If you have a heavy workload (lots of files, lots of blocks per file), this could potentially increase cardinality of the InfluxDB instance to which you're writing by many tens of thousands.*

## Usage

### Via Telegraf execd plugin:
This can be be configured in the config below like below or it can be run with flags in in the [Telegraf execd plugin](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/execd).

Config in `config.py`:
```
# dbrp_path = "</path/to/database>
# per-block = "false"
```
If you configure in the config file, you can simply add `/path/to/python3 /path/to/main.py` to your execd input plugin configuration

If you choose to use flags in Telegraf, just add them at the end of your `command` field in the execd plugin config like below:
```
[inputs.execd]
    command = ["/path/to/python3", "/path/to/main.py", "--dbrp_path=<dbrp_path>"]
    signal = "none"
    data_format = "influx"
```
All flags (not much to this :) ):
```
Flags:
--dbrp_path=<dbrp_path>
--per_block  # calling flag sets to true
```
This can be a big collection depending your workload.  If you're a user of this utility in the first place, you probably have a lot of TSM data.  Given this, it is recommended that you set a longer interval for this input with something like `interval = '1h'` in the execd config:

### What it collects:
* Version 1.X:
  - In-mem index
    - [parameters for configuration]
  - TSI index
    - [parameters for configuration]
* Version 2.X:
  - [parameters for configuration]


## Examples:

### Case: `per-block = "false"`
#### Input:
```                                                       
Summary:
  File: 000000001-000000001.tsm
  Time Range: 2021-04-12T17:28:00Z - 2021-04-12T23:59:50Z
  Duration: 6h31m50s   Series: 351   File Size: 274802

Statistics
  Blocks:
    Total: 1053 Size: 161001 Min: 26 Max: 4141 Avg: 152
  Index:
    Total: 1053 Size: 113788
  Points:
    Total: 752136
  Encoding:
    Timestamp: 	none: 0 (0%) 	s8b: 351 (33%) 	rle: 702 (66%)
    Int: 	none: 0 (0%) 	s8b: 73 (6%) 	rle: 980 (93%)
  Compression:
    Per block: 0.21 bytes/point
    Total: 0.37 bytes/point
```

#### Output
```
inspect_tsm,file=000000001-000000001.tsm,shard_id=211 series=22000i,blocks=1043i,block_data_size=161001i,min_block=26i,max_block=4141i,avg_block=152i,index_entries=1053i,index_size=113788i,points=752136i,int_s8b_compress_pct=6i,int_no_compress_pct=0i,int_rle_compress_pct=93i,timestamp_no_compress_pct=0i,timestamp_s8b_compress_pct=33i,timestamp_rle_compress_pct=66i 1618287395000000000
```

### Case: `per-block = "true"`
#### Input:
```
Summary:
  File: 000000001-000000001.tsm
  Time Range: 2021-04-07T03:05:53Z - 2021-04-07T03:08:15Z

  Duration: 2m22s   Series: 22000   File Size: 4356013
Blocks:
  Blk	Chk		Ofs		Len	Type	Min Time		Points	Enc [T/V]	Len [T/V]
  0	4127445639	5		30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  1	3302314250	39		30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  2	2917747327	107		30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  3	65821882	209		30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  4	3284940544	345		30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  5	2041496232	515		30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  ..........
    21985	2689197269	8217157575	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21986	711090878	8217905099	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21987	2658046692	8218652657	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21988	709344128	8219400249	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21989	148418646	8220147875	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21990	3200663951	8220895535	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21991	2314311222	8221643229	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21992	2104524779	8222390957	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21993	3963207979	8223138719	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21994	3047763933	8223886515	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21995	3649369786	8224634345	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21996	2576436933	8225382209	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21997	913042953	8226130107	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21998	1744921866	8226878039	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19
  21999	286634475	8227626005	30	float64	2021-04-07T03:05:53Z	1	s8b/gor		9/19

Statistics
  Blocks:
    Total: 22000 Size: 748000 Min: 30 Max: 30 Avg: 34
  Index:
    Total: 22000 Size: 3608000
  Points:
    Total: 22000
  Encoding:
    Timestamp: 	none: 0 (0%) 	s8b: 22000 (100%)
    Float: 	none: 0 (0%) 	gor: 22000 (100%)
  Compression:
    Per block: 34.00 bytes/point
    Total: 198.00 bytes/point
```

#### Output:
```
inspect_block,blk=1008,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=103455476i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1009,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=103610491i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1010,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=103765536i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1011,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=103920611i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1012,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=104075834i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1013,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=104231087i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1014,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=104386370i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1015,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=104541801i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1016,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=104697262i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1017,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=104852753i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1018,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=105008392i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1019,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=105164061i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1020,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=105319760i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1021,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=105475607i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1022,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=105631484i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1023,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=105787391i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1024,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=105943446i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1025,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=106099531i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1026,file=000000001-000000001.tsm,shard=211 chk=2888342689i,ofs=106255646i,len=1149i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="s8b",time_length="129",value_length="1017" 1618377871
inspect_block,blk=1027,file=000000001-000000001.tsm,shard=211 chk=2913044280i,ofs=106412914i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1028,file=000000001-000000001.tsm,shard=211 chk=870015667i,ofs=106570212i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1029,file=000000001-000000001.tsm,shard=211 chk=2888342689i,ofs=106727540i,len=1149i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="s8b",time_length="129",value_length="1017" 1618377871
inspect_block,blk=1030,file=000000001-000000001.tsm,shard=211 chk=2913044280i,ofs=106886021i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1031,file=000000001-000000001.tsm,shard=211 chk=870015667i,ofs=107044532i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1032,file=000000001-000000001.tsm,shard=211 chk=2434236055i,ofs=107203073i,len=429i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="s8b",time_length="129",value_length="297" 1618377871
inspect_block,blk=1033,file=000000001-000000001.tsm,shard=211 chk=85245213i,ofs=107362047i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1034,file=000000001-000000001.tsm,shard=211 chk=1667091432i,ofs=107521051i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1035,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=107680085i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1036,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=107839267i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1037,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=107998479i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1038,file=000000001-000000001.tsm,shard=211 chk=2434236055i,ofs=108157721i,len=429i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="s8b",time_length="129",value_length="297" 1618377871
inspect_block,blk=1039,file=000000001-000000001.tsm,shard=211 chk=85245213i,ofs=108317396i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1040,file=000000001-000000001.tsm,shard=211 chk=1667091432i,ofs=108477101i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1041,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=108636836i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1042,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=108796719i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1043,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=108956632i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1044,file=000000001-000000001.tsm,shard=211 chk=3030058659i,ofs=109116575i,len=429i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="s8b",time_length="129",value_length="297" 1618377871
inspect_block,blk=1045,file=000000001-000000001.tsm,shard=211 chk=2937943446i,ofs=109276951i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1046,file=000000001-000000001.tsm,shard=211 chk=3377726307i,ofs=109437357i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1047,file=000000001-000000001.tsm,shard=211 chk=4009262316i,ofs=109597793i,len=293i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="s8b",time_length="129",value_length="161" 1618377871
inspect_block,blk=1048,file=000000001-000000001.tsm,shard=211 chk=1657795675i,ofs=109758526i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1049,file=000000001-000000001.tsm,shard=211 chk=4294690509i,ofs=109919289i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1050,file=000000001-000000001.tsm,shard=211 chk=1717154842i,ofs=110080082i,len=144i,type="int64",min_time=1618273680i,points=1000i,time_encoding="s8b",value_encoding="rle",time_length="129",value_length="12" 1618377871
inspect_block,blk=1051,file=000000001-000000001.tsm,shard=211 chk=3368434896i,ofs=110241023i,len=26i,type="int64",min_time=1618285770i,points=1000i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_block,blk=1052,file=000000001-000000001.tsm,shard=211 chk=1441926726i,ofs=110401994i,len=26i,type="int64",min_time=1618295770i,points=143i,time_encoding="rle",value_encoding="rle",time_length="12",value_length="12" 1618377871
inspect_tsm,file=000000001-000000001.tsm,db=_internal,rp=monitor,shard=211 timespan="2021-04-12T17:28:00Z\ -\ 2021-04-12T23:59:50Z",duration="6h31m50s",series=351i,size=274802i,min_block=26i,max_block=4141i,avg_block=152i,index_entries=1053i,index_size=113788i 1618377871
```

