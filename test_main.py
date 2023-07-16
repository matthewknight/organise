import os
import shutil
from os.path import join as join
from os import mkdir
from os.path import exists as file_exists

import pytest
from constants import *

from main import get_episode_season_episode_identifier, main, search_for_tvshow, get_details_from_janky_title_v2

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
    ("For All Mankind (2019) Season 3 S03 (1080p ATVP WEB-DL x265 HEVC 10bit EAC3 Atmos 5.1 t3nzin)", ("For All Mankind", "Season 3")),
    ("South.Park.S15.1080p.BluRay.x264-FilmHD[rartv]", ("South Park", "Season 15")),
    ("Silicon.Valley.S06.1080p.AMZN.WEBRip.DDP5.1.x264-NTb[rartv]", ("Silicon Valley", "Season 6")),
    ("Its.Always.Sunny.In.Philadelphia.S05.BDRip.x264-ION10", ("It's Always Sunny in Philadelphia", "Season 5")),
    ("'Its.Always.Sunny.in.Philadelphia.S16E02.Frank.Shoots.Every.Member.of.the.Gang.1080p.AMZN.WEB-DL.DDP5.1.H.264-NTb[TGx]'", ("It's Always Sunny in Philadelphia", "Season 16")),
    ("Star.Trek.Discovery.S03.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]", ("Star Trek: Discovery", "Season 3")),
    ('The Bear (2022) Season 2 S02 (1080p HULU WEB-DL x265 HEVC 10bit EAC3 5.1 Silence)', ("The Bear", "Season 2")),
    ('Its.Always.Sunny.in.Philadelphia.S16E04.Frank.vs.Russia.1080p.AMZN.WEB-DL.DDP5.1.H.264-NTb[TGx]', ("It's Always Sunny in Philadelphia", "Season 16")),
])
def test_get_details_from_janky_title_v2(janky_title, expected):
    assert get_details_from_janky_title_v2(janky_title) == expected

@pytest.mark.parametrize("janky_title, expected", [
    ("'Its.Always.Sunny.in.Philadelphia.S16E02.Frank.Shoots.Every.Member.of.the.Gang.1080p.AMZN.WEB-DL.DDP5.1.H.264-NTb[TGx]'", ("S16E02")),
    ("'Its.Always.Sunny.in.Philadelphia.s16e15.Frank.Shoots.Every.Member.of.the.Gang.1080p.AMZN.WEB-DL.DDP5.1.H.264-NTb[TGx]'", ("S16E15")),
])
def test_get_episode_season_episode_identifier(janky_title, expected):
    assert get_episode_season_episode_identifier(janky_title) == expected

def test_half_show_moved():
    ## Arrange
    test_tv_show_path = join(TODO_DIR, "Star.Trek.Discovery.S03.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")
    mkdir(test_tv_show_path)

    mkfile(join(test_tv_show_path, "S03E03.mp4"))
    mkfile(join(test_tv_show_path, "S03E04.mp4"))
    mkfile(join(test_tv_show_path, "S03E05.mp4"))

    show_dest_dir = join(TV_DIR, "Star Trek: Discovery")
    season_dest_dir = join(show_dest_dir, "Season 3")
    mkdir(show_dest_dir)
    mkdir(season_dest_dir)
    mkfile(join(season_dest_dir, "Star Trek: Discovery S03E01.mp4"))
    mkfile(join(season_dest_dir, "Star Trek: Discovery S03E02.mp4"))

    ## Act
    main(MEDIA_DIR)

    ## Assert
    assert file_exists(join(season_dest_dir, "Star Trek: Discovery S03E01.mp4"))
    assert file_exists(join(season_dest_dir, "Star Trek: Discovery S03E02.mp4"))
    assert file_exists(join(season_dest_dir, "Star Trek: Discovery S03E03.mp4"))
    assert file_exists(join(season_dest_dir, "Star Trek: Discovery S03E04.mp4"))
    assert file_exists(join(season_dest_dir, "Star Trek: Discovery S03E05.mp4"))


    assert file_exists(test_tv_show_path) == False


def test_single_episode_moved():
    test_tv_show_path_s16e03 = join(TODO_DIR, "Its.Always.Sunny.in.Philadelphia.S16E03.The.Gang.Gets.Cursed.1080p.AMZN.WEB-DL.DDP5.1.H.264-NTb[TGx]")

    mkdir(test_tv_show_path_s16e03)

    mkfile(join(test_tv_show_path_s16e03, "torretnt-sdasdasd-S16E03.mp4"))
    ## Act
    main(MEDIA_DIR)

    ## Assert
    dest_dir = join(TV_DIR, "It's Always Sunny in Philadelphia")
    assert file_exists(join(dest_dir, "Season 16", "It's Always Sunny in Philadelphia S16E03.mp4"))


def test_multiple_seasons_tv_show():
    ## Arrange
    test_tv_show_path_s01 = join(TODO_DIR, "Star.trek.discovery.S01.720p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")
    test_tv_show_path_s02 = join(TODO_DIR, "Star.Trek.Discovery.S02.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")
    test_tv_show_path_s03 = join(TODO_DIR, "Star.Trek.Discovery.S03.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-BTN[rartv]")

    mkdir(test_tv_show_path_s01)
    mkdir(test_tv_show_path_s02)
    mkdir(test_tv_show_path_s03)

    mkfile(join(test_tv_show_path_s01, "S01E01.mp4"))
    mkfile(join(test_tv_show_path_s01, "S01E02.mp4"))
    mkfile(join(test_tv_show_path_s01, "S01E03.mp4"))

    mkfile(join(test_tv_show_path_s02, "S02E01.mp4"))
    mkfile(join(test_tv_show_path_s02, "S02E02.mp4"))
    mkfile(join(test_tv_show_path_s02, "S02E03.mp4"))

    mkfile(join(test_tv_show_path_s03, "S03E01.mp4"))
    mkfile(join(test_tv_show_path_s03, "S03E02.mp4"))
    mkfile(join(test_tv_show_path_s03, "S03E03.mp4"))

    ## Act
    main(MEDIA_DIR)

    ## Assert
    dest_dir = join(TV_DIR, "Star Trek: Discovery")
    assert file_exists(join(dest_dir, "Season 1", "Star Trek: Discovery S01E01.mp4"))
    assert file_exists(join(dest_dir, "Season 1", "Star Trek: Discovery S01E02.mp4"))
    assert file_exists(join(dest_dir, "Season 1", "Star Trek: Discovery S01E03.mp4"))

    assert file_exists(join(dest_dir, "Season 2", "Star Trek: Discovery S02E01.mp4"))
    assert file_exists(join(dest_dir, "Season 2", "Star Trek: Discovery S02E02.mp4"))
    assert file_exists(join(dest_dir, "Season 2", "Star Trek: Discovery S02E03.mp4"))

    assert file_exists(join(dest_dir, "Season 3", "Star Trek: Discovery S03E01.mp4"))
    assert file_exists(join(dest_dir, "Season 3", "Star Trek: Discovery S03E02.mp4"))
    assert file_exists(join(dest_dir, "Season 3", "Star Trek: Discovery S03E03.mp4"))