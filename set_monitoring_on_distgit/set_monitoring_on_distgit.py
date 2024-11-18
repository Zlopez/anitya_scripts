#!/usr/bin/env python3
"""
Script for setting monitoring value on dist-git.

This script will set monitoring value on dist-git to MONITORING_OPTION for
every package provided in PACKAGES_FILE.

One package per line. It will assume, that the package name is representing
Fedora package.

**Example file**:
    0ad
    python-requests
"""
import json

import requests

from requests.adapters import HTTPAdapter


PACKAGES_FILE = "packages"
DISTGIT_URL = "https://src.stg.fedoraproject.org/"
DISTGIT_API_KEY = "token"
MONITORING_OPTION = "monitoring"

if __name__ == "__main__":
    packages = []
    with open(PACKAGES_FILE, "r") as f:
        packages = f.readlines()

    # Create a requests session
    requests_session = requests.Session()

    requests_session.mount("https://", HTTPAdapter(max_retries=5))

    headers = {
        "Authorization": f"token {DISTGIT_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    for package in packages:
        resp = requests_session.post(
            DISTGIT_URL + f"_dg/anitya/rpms/{package.strip()}",
            data=json.dumps({"anitya_status": MONITORING_OPTION}),
            headers=headers
        )
        if resp.status_code != requests.codes.ok:
            try:
                print(f"Request {resp.url} failed with {resp.json()}")
            except json.decoder.JSONDecodeError:
                print(f"Request {resp.url} failed with {resp.content}")
        else:
            print(
                "Changed monitoring status to "
                f"{MONITORING_OPTION} for {package.strip()}"
            )
