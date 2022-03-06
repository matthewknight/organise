import os
import shutil
from os.path import join as join
from os import mkdir
from os.path import exists as file_exists

import pytest
from constants import *

from main import get_details_from_janky_title, main, search_for_tvshow

TEST_ROOT_DIR = join(os.getcwd(), "test_root")
MEDIA_DIR = join(TEST_ROOT_DIR, "media")
MOVIE_DIR = join(MEDIA_DIR, MOVIE_DIR_NAME)
TV_DIR = join(MEDIA_DIR, TV_DIR_NAME)
TODO_DIR = join(MEDIA_DIR, TV_DIR, TV_TODO_DIR_NAME)

def setup_function():
    """ Unit test directory setup
    """
    mkdir(TEST_ROOT_DIR)
    mkdir(MEDIA_DIR)
    mkdir(MOVIE_DIR)
    mkdir(TV_DIR)
    mkdir(TODO_DIR)

def teardown_function():
    """ Unit test directory teardown
    """
    path_cwd = os.getcwd()
    shutil.rmtree(os.path.join(path_cwd, TEST_ROOT_DIR))

def mkfile(full_path):
    with open(full_path, 'w') as _:
        pass

@pytest.mark.parametrize("title, expected", [
    ("Euphoria Us", "Euphoria"),
    ("South Park", "South Park")
])
def test_search(title, expected):
    assert search_for_tvshow(title) == expected

@pytest.mark.parametrize("janky_title, expected", [
    ("South.Park.S15.1080p.BluRay.x264-FilmHD[rartv]", ("South Park", "Season 15")),
    ("Silicon.Valley.S06.1080p.AMZN.WEBRip.DDP5.1.x264-NTb[rartv]", ("Silicon Valley", "Season 6")),
    ("Its.Always.Sunny.In.Philadelphia.S05.BDRip.x264-ION10", ("It's Always Sunny in Philadelphia", "Season 5")),
    ("Its.Always.Sunny.in.Philadelphia.S05.1080p.BluRay.x264-TENEIGHTY[rartv]", ("It's Always Sunny in Philadelphia", "Season 5")),
    ("Star.Trek.Discovery.S03.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]", ("Star Trek: Discovery", "Season 3")),
    ("Euphoria.US.S01.1080p.WEBRip.x265-RARBG", ("Euphoria", "Season 1")),
    ("The.Sopranos.S06.1080p.BluRay.x265-RARBG", ("The Sopranos", "Season 6")),
    ("Arrested.Development.S04.REMIX.1080p.NF.WEBRip.DD5.1.x264-SKGTV[rartv]", ("Arrested Development", "Season 4"))
])
def test_get_details_from_janky_title(janky_title, expected):
    assert get_details_from_janky_title(janky_title) == expected

def test_simple_tv_show():
    ## Arrange
    test_tv_show_path = join(TODO_DIR, "Star.Trek.Discovery.S03.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")
    mkdir(test_tv_show_path)

    mkfile(join(test_tv_show_path, "ep1.mp4"))
    mkfile(join(test_tv_show_path, "ep2.mp4"))
    mkfile(join(test_tv_show_path, "ep3.mp4"))

    ## Act
    main(MEDIA_DIR)

    ## Assert
    dest_dir = join(TV_DIR, "Star Trek: Discovery", "Season 3")
    assert file_exists(join(dest_dir, "ep1.mp4"))
    assert file_exists(join(dest_dir, "ep2.mp4"))
    assert file_exists(join(dest_dir, "ep3.mp4"))

    assert file_exists(test_tv_show_path) == False

def test_half_show_moved():
    ## Arrange
    test_tv_show_path = join(TODO_DIR, "Star.Trek.Discovery.S03.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")
    mkdir(test_tv_show_path)

    mkfile(join(test_tv_show_path, "ep3.mp4"))
    mkfile(join(test_tv_show_path, "ep4.mp4"))
    mkfile(join(test_tv_show_path, "ep5.mp4"))

    mkdir 
    show_dest_dir = join(TV_DIR, "Star Trek: Discovery")
    season_dest_dir = join(show_dest_dir, "Season 3")
    mkdir(show_dest_dir)
    mkdir(season_dest_dir)
    mkfile(join(season_dest_dir, "ep1.mp4"))
    mkfile(join(season_dest_dir, "ep2.mp4"))

    ## Act
    main(MEDIA_DIR)

    ## Assert
    assert file_exists(join(season_dest_dir, "ep1.mp4"))
    assert file_exists(join(season_dest_dir, "ep2.mp4"))
    assert file_exists(join(season_dest_dir, "ep3.mp4"))
    assert file_exists(join(season_dest_dir, "ep4.mp4"))
    assert file_exists(join(season_dest_dir, "ep5.mp4"))


    assert file_exists(test_tv_show_path) == False


def test_empty_todo():
    ## Arrange

    ## Act
    main(MEDIA_DIR)


def test_multiple_seasons_tv_show():
    ## Arrange
    test_tv_show_path_s01 = join(TODO_DIR, "Star.trek.discovery.S01.720p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")
    test_tv_show_path_s02 = join(TODO_DIR, "Star.Trek.Discovery.S02.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")
    test_tv_show_path_s03 = join(TODO_DIR, "Star.Trek.Discovery.S03.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")

    mkdir(test_tv_show_path_s01)
    mkdir(test_tv_show_path_s02)
    mkdir(test_tv_show_path_s03)

    mkfile(join(test_tv_show_path_s01, "ep1.mp4"))
    mkfile(join(test_tv_show_path_s01, "ep2.mp4"))
    mkfile(join(test_tv_show_path_s01, "ep3.mp4"))

    mkfile(join(test_tv_show_path_s02, "ep1.mp4"))
    mkfile(join(test_tv_show_path_s02, "ep2.mp4"))
    mkfile(join(test_tv_show_path_s02, "ep3.mp4"))

    mkfile(join(test_tv_show_path_s03, "ep1.mp4"))
    mkfile(join(test_tv_show_path_s03, "ep2.mp4"))
    mkfile(join(test_tv_show_path_s03, "ep3.mp4"))

    ## Act
    main(MEDIA_DIR)

    ## Assert
    dest_dir = join(TV_DIR, "Star Trek: Discovery")
    assert file_exists(join(dest_dir, "Season 1", "ep1.mp4"))
    assert file_exists(join(dest_dir, "Season 1", "ep2.mp4"))
    assert file_exists(join(dest_dir, "Season 1", "ep3.mp4"))

    assert file_exists(join(dest_dir, "Season 2", "ep1.mp4"))
    assert file_exists(join(dest_dir, "Season 2", "ep2.mp4"))
    assert file_exists(join(dest_dir, "Season 2", "ep3.mp4"))

    assert file_exists(join(dest_dir, "Season 3", "ep1.mp4"))
    assert file_exists(join(dest_dir, "Season 3", "ep2.mp4"))
    assert file_exists(join(dest_dir, "Season 3", "ep3.mp4"))