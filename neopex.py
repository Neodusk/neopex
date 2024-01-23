"""Neopex - Tracks LP loss/gains in Apex"""

from dataclasses import dataclass, field
from requests.adapters import HTTPAdapter, Retry
import requests
import sys
import json
import os
import yaml
import time
import click


req = requests.Session()

retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])

req.mount('http://', HTTPAdapter(max_retries=retries))
@dataclass
class Ranks():
    """Apex Rank LP"""
    rookie = [0, 3999]
    bronze = [4000, 7999]
    silver = [8000, 11999]
    gold = [12000, 15999]
    platinum = [16000, 19999]
    diamond = [20000, 23999]
    master = [24000, 27999]
    predator: int = 750 # top 750 leaderboard

@dataclass
class Config():
    """Config values"""
    new: bool = False
    api_key: str = ""
    root: str = ""
    user: str = ""
    platform: str = ""

def read_config():
    """
    Read in the neopex_config.yaml
    Assumes the config is a sibling to the exe
    """
    config = ""
    with open("neopex_config.yaml", "r", encoding="utf8") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config

def write_to_file(file_path: str, value_to_write):
    """Write to file and close it"""
    file = open(file=file_path, mode="w+", encoding="utf-8")
    file.write(str(value_to_write))
    file.close()

def initialize_lp(new: bool,
                  response: json,
                  root_lp_file_path: str,
                  current_lp_counter_path: str,
                  root: str) -> int:
    """Init LP"""
    original_score = 0
    root_lp_file = open(file=root_lp_file_path, mode="r+", encoding="utf-8")
    current_lp_counter_path = f"{root}current_lp_counter.txt"
    if new:
        # get original amount of LP
        # contains the root lp from start of tracking
        original_score = int(response.json()["global"]["rank"]["rankScore"])
        root_lp_file.write(str(original_score))
        write_to_file(current_lp_counter_path, str(0))
    else:
        # read contents into memory
        original_score = int(root_lp_file.read()) # check this syntax
        print(str(original_score))
    root_lp_file.close()
    return original_score


def get_lp(response: json,
           original_score: int,
           current_lp_counter_path: str):
    """
    retrieves the LP fromm the API and calculates the total changed LP
    returns the total changed lp and the new total lp score
    """
    new_score = int(response.json()["global"]["rank"]["rankScore"])
    total_changed_score = 0
    print(f"new_score {new_score} og score: {original_score}")
    if new_score != original_score:
        # get the difference of the scores and add to running change
        if new_score < original_score:
            total_changed_score = new_score - original_score
        else:
            total_changed_score = abs(new_score - original_score)
        write_to_file(current_lp_counter_path, str(total_changed_score))
        print(total_changed_score)
    return total_changed_score, new_score

def get_rank_name(response):
    """Returns name of current rank"""
    return response.json()["global"]["rank"]["rankName"].lower()

def get_total_lp_to_next_tier(current_lp):
    """Get total LP to next tier"""
    return 1000-(current_lp%1000)

def get_total_lp_to_next_rank(rank_name, current_lp):
    """Get total LP to next rank"""
    ranks = Ranks()
    rank_lp_value_min, rank_lp_value_max = getattr(ranks, rank_name)
    return rank_lp_value_max - current_lp + 1

def create_obs_files(paths):
    """Creates OBS files"""
    for file in paths:
        if not os.path.exists(file):
            write_to_file(file, 0)

def setup_environment(new, user, platform, root, api_key):
    """Setup variables needed for neopex_tracker to run"""
    config_dict = read_config()
    config = Config(config_dict.get("new", False),
                    config_dict["api_key"],
                    config_dict["root"],
                    config_dict["user"],
                    config_dict["platform"])

    new_ = new if new is not False else config.new
    api_key_ = api_key if api_key != "" else config.api_key
    apex_api = api_key_ if api_key_ != "" else os.environ.get("apex_api")
    root_ = root if root != "" else config.root
    user_ = user if user != "" else config.user
    platform_ = platform if platform != "" else config.platform

    if not apex_api:
        print("Failed to get API key")
        sys.exit()

    return new_, user_, platform_.upper(), root_, apex_api

def output_stats(response):
    """Used to output various things from API response"""
    is_online = response.json()["realtime"]["isOnline"]
    current_state = response.json()["realtime"]["currentStateAsText"]
    legend = response.json()["legends"]["selected"]["LegendName"]
    print(f"Online: {is_online}")
    print(f"Current State: {current_state}")
    print(f"Legend: {legend}")

@click.command()
@click.option('--new', is_flag=True, default=False, required=False, help='Start new LP tracker')
@click.option('--user', default="", required=False, help='User to check against')
@click.option('--platform', default="", required=False, help='Platform to check against')
@click.option('--root', default="", required=False, help='Platform to check against')
@click.option('--api_mins', default=1, required=False, help='How many mins between API calls')
@click.option('--api_key', default="", required=False, help='API key')
def main(new, user, platform, root, api_mins, api_key):
    """
    API docs can be found https://apexlegendsapi.com/  
    """
    new_, user_, platform_, root_, apex_api_ = setup_environment(new, user, platform, root, api_key)

    root_lp_file_path = f"{root_}root_lp.txt"
    current_lp_counter_path = f"{root_}current_lp_counter.txt"
    lp_to_next_rank_path = f"{root_}lp_to_next_rank.txt"
    paths = [root_lp_file_path, current_lp_counter_path, lp_to_next_rank_path]
    create_obs_files(paths)

    response = req.get(f"https://api.mozambiquehe.re/bridge?auth={apex_api_}&player={user_}&platform={platform_}&merge=true")

    if str(response.status_code).startswith("401"):
        print("Failed to auth, please check API key and try again")
        print(response.json()["Error"])
        sys.exit()
    if str(response.status_code).startswith("400"):
        print("Issue with query, please check configs")
        print(response.json()["Error"])
        print(f"https://api.mozambiquehe.re/bridge?auth=<hidden>&player={user_}&platform={platform_}&merge=true")
        sys.exit()
    
    original_score = initialize_lp(new=new_,
                                   response=response,
                                   root_lp_file_path=root_lp_file_path,
                                   current_lp_counter_path=current_lp_counter_path,
                                   root=root_)

    # main loop
    while True:
        # grab full response from API
        response = req.get(f"https://api.mozambiquehe.re/bridge?auth={apex_api_}&player={user_}&platform={platform_}&merge=true")
        current_lp_counter, current_actual_lp = get_lp(response=response,
                                                       original_score=original_score,
                                                       current_lp_counter_path=current_lp_counter_path)
        print(f"Current LP Gain/Loss: {current_lp_counter}")
        output_stats(response)
        print(f"Total LP to next tier: {get_total_lp_to_next_tier(current_actual_lp)}")
        rank_name = get_rank_name(response=response)
        lp_to_next_rank = get_total_lp_to_next_rank(rank_name, current_actual_lp)
        write_to_file(lp_to_next_rank_path, lp_to_next_rank)
        print(f"lp to next rank: {lp_to_next_rank}")
        time.sleep(api_mins*60)

if __name__ == "__main__":
    main()
