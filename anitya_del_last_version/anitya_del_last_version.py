#!/usr/bin/env python3
"""
This script will allow you to remove latest version from projects
specified by id in PROJECTS_FILE. One id per line. This is useful
when you need to detect latest version again on some projects to
trigger the-new-hotness.

**Example file**:
    12345
    12345

"""

import getpass
import time

import requests
from bs4 import BeautifulSoup as BS

PROJECTS_FILE = "projects"
SERVER_URL = "https://stg.release-monitoring.org/"
LOGIN_URL = "https://id.fedoraproject.org/"
WAIT_TIME = 0.5


def login(session, username, password):
    """
    Log user to Anitya inside requests session.

    Params:
        session (`requests.Session`): Requests session HTTP
        username (str): FAS username
        password (str): FAS password
    """

    resp = session.get(SERVER_URL + "login/fedora/")
    bs = BS(resp.content, "html.parser")
    payload = dict((tag["name"], tag["value"]) for tag in bs.find_all("input", type="hidden"))
    resp = session.post(LOGIN_URL + "openid", data=payload)

    resp = session.get(resp.url, allow_redirects=True)
    bs = BS(resp.content, "html.parser")
    payload = {
        "login_name": username,
        "login_password": password,
        "ipsilon_transaction_id": bs.find(id="ipsilon_transaction_id")["value"]
    }
    resp = session.post(LOGIN_URL + "login/fas", data=payload)
    if resp.status_code == 200:
        print("Logged in")


def remove_latest_version(session, project):
    """
    Remove latest version from project.

    1) Open the project page
    2) Read the latest version
    3) Remove the latest version

    Params:
        session (`requests.Session`): Requests session
        project (str): Project id
    """

    resp = session.get(SERVER_URL + "project/" + project)
    if resp.status_code != 200:
        print("ERROR: Project '{}' not found. URL: '{}'".format(project, SERVER_URL + "project/" + project))
        return
    bs = BS(resp.content, "html.parser")
    try:
        latest_version_row = bs.findAll("tr", property="doap:release")[0]
        latest_version = latest_version_row.findAll("td")[2].string
    except IndexError:
        print("ERROR: No version found on {}".format(SERVER_URL + "project/" + project))
        return
    resp = session.get(SERVER_URL + "project/" + project + "/delete/" + latest_version, cookies=session.cookies)
    if resp.status_code != 200:
        print("ERROR: Version '{}' not found on project '{}'. URL: '{}'".format(
            latest_version, project, SERVER_URL + "project/" + project + "/delete/" + latest_version)
        )
        return
    bs = BS(resp.content, "html.parser")
    try:
        csrf_token = bs.find("input", id="csrf_token")["value"]
    except AttributeError:
        print("ERROR: CSRF token not found. Something is wrong")
        return
    payload = {
        "csrf_token": csrf_token,
        "confirm": "Yes"
    }
    resp = session.post(
        SERVER_URL + "project/" + project + "/delete/" + latest_version, data=payload
    )
    if resp.status_code == 200:
        print("Version '{}' deleted on project '{}'. URL: '{}'".format(
            latest_version, project, SERVER_URL + "project/" + project + "/delete/" + latest_version)
        )
    else:
        print("ERROR: Can't delete version '{}' on project '{}'. URL: '{}'".format(
            latest_version, project, SERVER_URL + "project/" + project + "/delete/" + latest_version)
        )


if __name__ ==  "__main__":
    projects = []
    with open(PROJECTS_FILE, "r") as f:
        projects = f.readlines()

    print("Please provide your credentials.")
    username = input("Username: ")
    password = getpass.getpass()

    with requests.Session() as r_session:
        login(r_session, username, password)
        for project in projects:
            checked = False
            while not checked:
                try:
                    remove_latest_version(r_session, project.strip())
                except requests.ConnectionError:
                    print("Connection error occurred, waiting for '{}' second before retry".format(
                        WAIT_TIME
                    ))
                    time.sleep(WAIT_TIME)
