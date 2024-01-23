# Using Neopex Tracker

1. Download the repository, unzip it and save it somewhere you will remember. If you are just using the exe, you will only need the `dist` folder.
2. Request an API key from https://portal.apexlegendsapi.com/ (this is used as the `api_key`)
3. Follow the instructions in [Quick Setup with EXE](#Quick-Setup-with-EXE).

## Quick Setup with EXE

### neopex_config.yaml

1. Open `dist/neopex_config.yaml`
2. At a minimum fill out the values for `api_key`, `user`, and `platform`. It is also recommended to fill out `--root` with a folder path that you want the files saved to.
3. Double click `dist/neopex.exe` to run. You may have to approve it to run as Windows sometimes wants to consider it a threat.
4. Leave the exe running as long as you need. `CTRL+C` or close out of the terminal when done.

### CLI arguments

The tool can be ran via commandline as well. If a value is not specified in the subcommands, it will instead check the config file for those values. Subcommand values take priority over config values.

Example command
```
neopex.exe --platform=PC --user=SuperAwesomeApexPlayer --root=C:\Users\admin\Desktop\neopex\
```

`--new`: Start a new tracker. Resets the LP root count to the current LP the account has and the counter resets to 0. This should be ran the first time you start neopex.

`--user`: The account to check against

`--root`: The path that neopex should store 

configuration files to (this defaults to the path that you run the exe from)

`--api_mins`: Usually should not be touched. The number of minutes that be between API calls. 

`--api_key`: The API key used to authorize with the API server.

`--help`: List subcommands available to use


## Setting up in OBS/Streamlabs
1. Use the `root` location to find the config files that you want to read into OBS.
2. Create separate Text sources for each item you want to track and set it as 
Read from file". Choose the appropriate file for the tracking you want to use.

### OBS Config Files

`current_lp_counter.txt`: The amount of LP you have lost or gained since you started the tracker.

`lp_to_next_rank.txt`: How much LP is needed until you fully rank up to the next rank.

`root_lp.txt`: How much LP you started with when the tracker started.


## Running with Python / Extending Development
```
# setup venv
python -m venv venv
# activate venv
./venv/Scripts/activate
# install depends
pip install -r requirements.txt
# run neopex.py
python neopex.py --help
```

## Important Notes

> To avoid writing your `api_key` in plaintext in CLI or the `yaml` file, you can instead set it as a system enviornment variable.