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


# Examples:

## Case: `per-block = "false"`
### Input:
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

### Output
```
inspect_tsm,file=000000001-000000001.tsm,shard_id=211 series=22000i,blocks=1043i,block_data_size=161001i,min_block=26i,max_block=4141i,avg_block=152i,index_entries=1053i,index_size=113788i,points=752136i,int_s8b_compress_pct=6i,int_no_compress_pct=0i,int_rle_compress_pct=93i,timestamp_no_compress_pct=0i,timestamp_s8b_compress_pct=33i,timestamp_rle_compress_pct=66i 1618287395000000000
```

## Case: `per-block = "true"`
### Input:
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

### Output:
```
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21984i,chk=3584288089i,ofs=8216410085i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21985i,chk=2689197269i,ofs=8217157575i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21986i,chk=711090878i,ofs=8217905099i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21987i,chk=2658046692i,ofs=8218652657i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21988i,chk=709344128i,ofs=8219400249i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21989i,chk=148418646i,ofs=8220147875i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21990i,chk=3200663951i,ofs=8220895535i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21991i,chk=2314311222i,ofs=8221643229i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21992i,chk=2104524779i,ofs=8222390957i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21993i,chk=3963207979i,ofs=8223138719i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21994i,chk=3047763933i,ofs=8223886515i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_block,file=000000001-000000001.tsm,shard=210 blk=21995i,chk=3649369786i,ofs=8224634345i,len=30i,type="float64",min_time=1617789953i,points=1i,time_encoding="s8b",value_encoding="gor",time_length="9",value_length="19" 1618372723
inspect_tsm,file=000000001-000000001.tsm,db=float_int_low_card,rp=autogen,shard=210 timespan="2021-04-07T03:05:53Z\ -\ 2021-04-07T03:08:15Z",duration="2m22s",series=22000i,size=4356013i,min_block=30i,max_block=30i,avg_block=34i,index_entries=22000i,index_size=3608000i 1618373462
```

