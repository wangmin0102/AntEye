---
layout: page
title: Logging
order: 30
---

Loggers are used by AntEye to record the state of all monitors after each interval.

The types of loggers are:

* [db](#db): Records the result of every monitor, every iteration (maintaining a history) in a SQLite database.
* [dbstatus](#dbstatus): Records a snapshot of the current state of every monitor in a SQLite database.
* [logfile](#logfile): Records a logfile of the result of every monitor, or only the monitors which failed. Each line is preceeded by the current UNIX timestamp.
* [html](#html): Writes an HTML file showing the status of all monitors (including remote ones).
* [network](#network): Sends status of all monitors to a remote host.
* [json](#json): Writes a JSON file describing the state of all the monitors
* [mqtt](#mqtt): Send monitor state via MQTT

## Defining a logger

The section name should be the name of your logger. This is the name you should give in the "loggers" setting in the "reporting" section of the configuration. All loggers take these two parameters.

| setting | description | required | default |
|---|---|---|---|
| type | the type of logger to create. Choose one of the five in the list above. | yes | |
| depend | lists (comma-separated, no spaces) the names of the monitors this logger depends on. Use this if the database file lives over the network. If a monitor it depends on fails, no attempt will be made to update the database.| no | |
| groups | comma-separated list of monitor groups this logger should operate for | no | "default" |
| tz | The [timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) the logger should convert date/times to. | no | UTC |

### <a name="db"></a><a name="dbstatus"></a>db and dbstatus loggers

| setting | description | required | default |
|---|---|---|---|
| path | the path/filename of the SQLite database file. You should initialise the schema of this file using the monitor.sql file in the distribution. You can use the same database file for many loggers.| yes | |

### <a name="logfile"></a>logfile loggers

| setting | description | required | default |
|---|---|---|---|
| filename | the filename to write to. Rotating this file underneath AntEye will likely result in breakage (this will be addressed later). | yes | |
| buffered | set to 1 if you aren’t going to watch the logfile in real time. If you want to watch it with something like tail -f then set this to 0. | no | 1 |
| only_failures | set to 1 if you only want failures to be written to the file. | no | 0 |
| dateformat | The date format to write for log lines. Supported values are "timestamp" (UNIX timestamp) or "iso8601" (YYYY-MM-DDTHH:MM:SS). | no | timestamp |

### <a name="html"></a>html loggers

| setting | description | required | default |
|---|---|---|---|
| source_folder | the folder in which all the needed files live. You only need this if you're customising the files | no | "html" in the distribution |
| folder | the folder in which to write the file(s). Must already exist. | yes | |
| filename | the filename to write out. The file will be updated once per interval (as defined in the main configuration). Relative to the *folder*. | yes | |
| header | the header include file which is sucked in when writing the output file. Relative to folder. | no | footer.html |
| footer | the footer include file. Relative to folder. | no | header.html |
| upload_command | a command to run to e.g. upload the generated files to another location | no | |
| copy_resources | set to 0 if AntEye should not copy needed supporting files (e.g. CSS) to the output folder | no | 1 |

The supplied header file includes JavaScript to notify you if the page either doesn’t auto-refresh, or if AntEye has stopped updating it. This requires your machine running AntEye and the machine you are browsing from to agree on what the time is (timezone doesn’t matter)!

You can use the `upload_command` setting to specify a command to push the generated files to another location (e.g. a web server, an S3 bucket etc). I'd suggest putting the commands in a script and just specifying that script as the value for this setting.

### <a name="network"></a>network logger

This logger is used to send status reports of all monitors to a remote instance. The remote instance must be configured to listen for connections. The *key* parameter is a shared secret used to generate a hash of the network traffic so the receiving instance knows to trust the data. (Note that the traffic is not encrypted, just given a hash.)

| setting | description | required | default |
|---|---|---|---|
| host | the remote host to send to. | yes | |
| port | the port on the remote host to connect to. | yes | |
| key | shared secret to protect communications | yes | |

### <a name="json"></a>json logger

| setting | description | required | default |
|---|---|---|---|
| filename | the path of the JSON file to write. | yes | |

### <a name="mqtt"></a>mqtt logger

| setting | description | required | default |
|---|---|---|---|
| host | The host to connect to | yes | |
| port | The port to connect on | no | 1883 |
| hass | Specific configuration for Home Assistant MQTT discovery | no | false |
| topic | The topic to post to | no | `AntEye` (`homeassistant/binary_sensor` if hass is set) |
| username | The username to use | no | |
| password | The password to use | no | |

See <https://www.home-assistant.io/docs/mqtt/discovery/> for more information on HASS/
