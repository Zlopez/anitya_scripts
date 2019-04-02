#!/usr/bin/env python3
"""
This script will retrieve project id for every package provided in PACKAGES_FILE.
One package per line. It will assume, that the package name is representing Fedora
package.

**Example file**:
    0ad
    python-requests
"""

import requests


PACKAGES_FILE = "packages"
SERVER_URL = "https://stg.release-monitoring.org/"


def get_project_name(package):
    """
    Get name of the project for provided package

    Params:
        package (str): Name of the package

    Returns:
        (str): Name of the project
    """
    result = None
    params = {
        "name": package,
        "distribution": "Fedora"
    }
    resp = requests.get(SERVER_URL + "api/v2/packages", params=params)
    if resp.status_code == 200:
        response_dict = resp.json()
        if response_dict["items"]:
            result = response_dict["items"][0]["project"]
            print("Package '{}' belongs to project '{}'".format(package, result))
        else:
            print("Package '{}' doesn't belongs to any project".format(package))
    else:
        print("ERROR: Wrong arguments for request")

    return result


def get_project_id(project):
    """
    Get project id from name.

    Params:
        project (str): Project name

    Returns:
        (str): Project id
    """
    result = None
    if not project:
        print("Project name is empty")
        return result

    params = {
        "name": project
    }
    resp = requests.get(SERVER_URL + "api/v2/projects", params=params)
    if resp.status_code == 200:
        response_dict = resp.json()
        if response_dict["items"]:
            result = response_dict["items"][0]["id"]
            print("Project '{}' has id '{}'".format(project, result))
        else:
            print("Package '{}' not found".format(project))
    else:
        print("ERROR: Wrong arguments for request")

    return result


if __name__ ==  "__main__":
    packages = []
    with open(PACKAGES_FILE, "r") as f:
        packages = f.readlines()

    project_ids = []
    for package in packages:
        project_name = get_project_name(package)
        project_id = get_project_id(project_name)
        if project_id:
            project_ids.append(project_id)

    for project_id in project_ids:
        print(project_id)
