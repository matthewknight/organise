import configparser
import glob
import os
from os.path import join as join
from os.path import isdir as dir_exists
import re
import shutil
from tmdbv3api import TMDb, TV

config = configparser.ConfigParser()
config.read('secret.cfg')
tmdb = TMDb().api_key = config.get('ClientSecrets', 'tmdb_api_key')

from constants import *

def get_movie_dir(media_dir):
    return join(media_dir, MOVIE_DIR_NAME)

def get_tv_dir(media_dir):
    return join(media_dir, TV_DIR_NAME)

def get_tv_todo_dir(media_dir):
    return join(media_dir, TV_DIR_NAME, TV_TODO_DIR_NAME)

def search_for_tvshow(search_term):
    result = TV().search(search_term)[0].name
    print(f"Found '{result}' for TMDB search '{search_term}'")
    return result

def get_segment_season_identifer(segment):
    season_re = r'S\d{1,2}'
    search = re.search(season_re, segment)
    if search is None:
        return None
    
    return f'Season {search.string.lstrip("S").lstrip("0")}'

def get_details_from_janky_title(janky_title):
    split_title = [str.capitalize(i) for i in janky_title.split(".")]
    for index, segment in enumerate(split_title):
        season = get_segment_season_identifer(segment)
        if season != None:
            title = " ".join(split_title[:index])
            return (search_for_tvshow(title), season)

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
        (parsed_title, season) = get_details_from_janky_title(series_dir_name)
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
            shutil.move(os.path.join(series_dir, file_name), season_dir)
            files_moved += 1
        print(f"Moved {files_moved} files to {season_dir}")

        ## Delete empty todo dir
        os.rmdir(series_dir)
        print(f"Deleting {series_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Media organiser')
    parser.add_argument('--mediapath', metavar='path', required=True,
                        help='the path to the media folder')
    args = parser.parse_args()
    main(media_path=args.mediapath)