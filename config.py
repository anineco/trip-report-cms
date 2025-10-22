#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path

HOME = os.path.expanduser("~")
REPO_DIR = os.path.dirname(os.path.abspath(__file__))

# directory for the outputs: html, json, etc.
DIST_DIR = f"{REPO_DIR}/dist"
# working directory: resource json files
WORK_DIR = f"{REPO_DIR}/work"
# data directory: database, change log, etc.
DATA_DIR = f"{REPO_DIR}/data"
# resource directory for photographic images
IMG_DIR = f"{HOME}/photo/tozan/original"
# resource directory for GPX files
GPX_DIR = f"{HOME}/Garmin"

# waypoint symbol in GPX files for summits
SYM_SUMMIT = "Summit"
# web service URL for mountain information database
DBURL = "https://map.jpn.org/share/mt.php"


def main():
    print(f"HOME={HOME}")
    print(f"REPO_DIR={REPO_DIR}")
    print(f"DIST_DIR={DIST_DIR}")
    print(f"WORK_DIR={WORK_DIR}")
    print(f"DATA_DIR={DATA_DIR}")
    print(f"IMG_DIR={IMG_DIR}")
    print(f"GPX_DIR={GPX_DIR}")
    print(f"SYM_SUMMIT={SYM_SUMMIT}")
    print(f"DBURL={DBURL}")


if __name__ == "__main__":
    main()

# __END__
