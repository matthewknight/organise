import configparser
import glob
import os
from os.path import join as join
from os.path import isdir as dir_exists
import re
import shutil
from tmdbv3api import TMDb, TV
import openai
import ast

config = configparser.ConfigParser()
config.read('secret.cfg')
tmdb = TMDb().api_key = config.get('ClientSecrets', 'tmdb_api_key')
openai.api_key = config.get('ClientSecrets', 'openai_key')

from constants import *

def get_movie_dir(media_dir):
    return join(media_dir, MOVIE_DIR_NAME)

def get_tv_dir(media_dir):
    return join(media_dir, TV_DIR_NAME)

def get_tv_todo_dir(media_dir):
    return join(media_dir, TV_DIR_NAME, TV_TODO_DIR_NAME)

def search_for_tvshow(search_term):
    print(f"Searching TMDB for '{search_term}'")
    result = TV().search(search_term)[0].name
    print(f"Found '{result}' for TMDB search '{search_term}'")
    return result

def get_segment_season_identifer(segment):
    season_re = r'S\d{1,2}'
    search = re.search(season_re, segment)
    if search is None:
        return None
    
    return f'Season {search.string.lstrip("S").lstrip("0")}'

def get_details_from_janky_title_v2(janky_title):
    completion = openai.Completion.create(model="text-davinci-003", \
        prompt=f"Convert the following directory name into a Python tuple ('<Show Name>', 'Season <Number>'). Only show the season as the number, e.g. 'Season 5'. If you find the year, e.g. (2023), don't include it. '{janky_title}'")
    response = completion.choices[0].text
    print(f"Got raw response from OpenAI {response}")
    (title, season) = ast.literal_eval(response)
    print(f"OpenAI parsed {janky_title} to '{title}': '{season}'")

    return (search_for_tvshow(title), season)

def get_episode_season_episode_identifier(filename):
    season_episode_re = r'(?i)S\d{2}E\d{2}'
    search = re.search(season_episode_re, filename)
    if search is None:
        return None
    return search.group().upper()

def is_structure_valid(media_path):
    if (dir_exists(get_movie_dir(media_path)) and
        dir_exists(get_tv_dir(media_path)) and
        dir_exists(get_tv_todo_dir(media_path))):
        return True
    else:
        return False

def main(media_path):
    if not is_structure_valid:
        print("Media folder structure is invalid, exiting")

    ## Process TV Show todos
    for series_dir in glob.iglob(join(get_tv_todo_dir(media_path), "**")):
        series_dir_name = series_dir.split("/")[-1]
        (parsed_title, season) = get_details_from_janky_title_v2(series_dir_name)
        print(f"Found TV show: {parsed_title}, {season}")

        ## Make TV show dir if it doesn't exist
        tv_show_dir = join(get_tv_dir(media_path), parsed_title)
        if not os.path.exists(tv_show_dir):
            os.makedirs(tv_show_dir)
            print(f"Created {tv_show_dir}")

        ## Make the inner season dir
        season_dir = join(tv_show_dir, season)
        if os.path.exists(season_dir):
            print(f"{parsed_title}: {season} folder already exists, moving over additional files...")
        else:
            os.makedirs(season_dir)
            print(f"Created {season_dir}")

        ## Move the todo episodes into the new dir
        file_names = os.listdir(series_dir)
        files_moved = 0
        for file_name in file_names:
            file_extension = file_name.split(".")[-1]
            season_episode_identifier = get_episode_season_episode_identifier(file_name)
            if season_episode_identifier is None:
                print(f"Not moving {file_name}, can't find identifier")
                continue
            src = os.path.join(series_dir, file_name)
            dst = os.path.join(season_dir, f"{parsed_title} {season_episode_identifier}.{file_extension}")
            print(f"Moving {src} to {dst}")
            shutil.move(src, dst)
            files_moved += 1
        print(f"Moved {files_moved} files to {season_dir}")

        ## Delete empty todo dir
        shutil.rmtree(series_dir, ignore_errors=True)
        print(f"Deleting {series_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Media organiser')
    parser.add_argument('--mediapath', metavar='path', required=True,
                        help='the path to the media folder')
    args = parser.parse_args()
    main(media_path=args.mediapath)