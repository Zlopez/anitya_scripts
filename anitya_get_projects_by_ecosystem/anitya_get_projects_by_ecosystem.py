#!/usr/bin/env python3
"""
This script will retrieve every project id for ecosystem in ECOSYSTEM constant.
"""
import math
import time

import requests


ECOSYSTEM = "crates.io"
SERVER_URL = "https://stg.release-monitoring.org/"
ITEMS_PER_PAGE = 250
WAIT_TIME = 0.5


def get_total_items():
    """
    Get total amount of projects in ecosystem.

    Returns:
        (int): Total amount of items
    """
    result = 0
    params = {
        "ecosystem": ECOSYSTEM,
        "items_per_page": 1
    }
    resp = requests.get(SERVER_URL + "api/v2/projects", params=params)
    if resp.status_code == 200:
        response_dict = resp.json()
        if response_dict["total_items"]:
            result = response_dict["total_items"]
            print("Ecosystem '{}' contain '{}' projects".format(ECOSYSTEM, result))
        else:
            print("Didn't found expected key 'total_items' in json '{}':".format(response_dict))
    else:
        print("ERROR: Wrong arguments for request")

    return result


def get_project_ids(page, items_per_page):
    """
    Get project ids for ecosystem.

    Params:
        page (int): Page index
        items_per_page (int): Items per page

    Returns:
        (:obj:`list` of :obj:`str`): List of project ids
    """
    result = []

    params = {
        "ecosystem": ECOSYSTEM,
        "page": page + 1,
        "items_per_page": items_per_page
    }
    resp = requests.get(SERVER_URL + "api/v2/projects", params=params)
    if resp.status_code == 200:
        response_dict = resp.json()
        if response_dict["items"]:
            for item in response_dict["items"]:
                result.append(item["id"])
                print("Project '{}' has id '{}'".format(item["name"], item["id"]))
        else:
            print("Didn't found expected key 'items' in json '{}':".format(response_dict))
    else:
        print("ERROR: Wrong arguments for request")

    return result


if __name__ == "__main__":
    project_ids = set()
    total_items = get_total_items()
    pages = math.ceil(total_items/ITEMS_PER_PAGE)
    print("Number of pages '{}' = '{}'/'{}'".format(pages, total_items, ITEMS_PER_PAGE))
    for index in range(0, pages):
        checked = False
        while not checked:
            try:
                project_id_list = get_project_ids(index, ITEMS_PER_PAGE)
                checked = True
            except requests.ConnectionError:
                print("Connection error occurred, waiting for '{}' second before retry".format(
                    WAIT_TIME
                ))
                time.sleep(WAIT_TIME)
        if project_id_list:
            project_ids.update(project_id_list)

    for project_id in project_ids:
        print(project_id)
