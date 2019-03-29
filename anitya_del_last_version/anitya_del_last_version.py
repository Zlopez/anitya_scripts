#!/usr/bin/env python3

import sys
import getpass

import requests
from bs4 import BeautifulSoup as BS

PROJECTS_FILE = "projects"
SERVER_URL = "https://stg.release-monitoring.org/"
LOGIN_URL = "https://id.fedoraproject.org/"


def login(session, username, password):
    """
    Log user to Anitya inside requests session.

    Params:
        session (`requests.Session`): Requests session
        username (str): FAS username
        password (str): FAS password
    """
    resp = session.get(LOGIN_URL + "login", allow_redirects=True)
    bs = BS(resp.content, "html.parser")
    payload = {
        "login_name": username,
        "login_password": password,
        "ipsilon_transaction_id": bs.find(id="ipsilon_transaction_id")["value"]
    }
    session.post(LOGIN_URL + "login/fas", data=payload)


if __name__ ==  "__main__":
    with open(PROJECTS_FILE, "r") as f:
        projects = f.readlines()

    print("Please provide your credentials.")
    username = input("Username: ")
    password = getpass.getpass()

    with requests.Session() as r_session:
        login(r_session, username, password)

