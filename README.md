# influx_inspect_utility

## Description

The Inspect Utility is for running the `influx_inspect` InfluxDB disk utility on a regular cadence and writing the results to InfluxDB.  It is designed to be used as an external plugin for Telegraf (*first iteration does not have native ability to write to InfluxDB without Telegraf*).

## Motivation

The `influx_inspect` utility is a fantastic tool for ad hoc looks into the file storage behavior of InfluxDB.  That said, it is a common need to want to compare the state you're seeing now to a state it was in prior to now...and potentially to a state in the future.  Enter time series data!

By running the utility and recording results to a time series database, you can now analyze the changes in this file system behavior over time.  This is important for monitoring the existence of anomalous performance degredation.

## Usage

Telegraf external plugin:
* Version 1.X:
  - In-mem index
    - [parameters for configuration]
  - TSI index
    - [parameters for configuration]
* Version 2.X:
  - [parameters for configuration]


### *Standalone (TBD)*
