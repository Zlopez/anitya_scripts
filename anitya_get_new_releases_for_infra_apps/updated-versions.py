#!/usr/bin/env python3

"""
Report which applications have been updated in the last $DAYS.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from glob import glob
from urllib.parse import urljoin

import click
import requests


DATAGREPPER = "https://apps.fedoraproject.org/datagrepper/"
DATAGREPPER_STG = "https://apps.stg.fedoraproject.org/datagrepper/"
TOPIC = "org.release-monitoring.prod.anitya.project.version.update.v2"


@dataclass
class App:
    name: str
    title: str
    release_notes_url: str


APPS = [
    App(
        name="noggin-aaa",
        title="Noggin",
        release_notes_url="https://github.com/fedora-infra/noggin/releases/tag/v{version}",
    ),
    App(
        name="fasjson",
        title="FASJSON",
        release_notes_url="https://github.com/fedora-infra/fasjson/releases/tag/v{version}",
    ),
    App(
        name="fasjson-client",
        title="FASJSON client",
        release_notes_url="https://github.com/fedora-infra/fasjson-client/releases/tag/v{version}",
    ),
    App(
        name="datagrepper",
        title="Datagrepper",
        release_notes_url="https://github.com/fedora-infra/datagrepper/releases/tag/{version}",
    ),
    App(
        name="datanommer.models",
        title="Datanommer models",
        release_notes_url="https://github.com/fedora-infra/datanommer/releases/tag/{version}",
    ),
    App(
        name="datanommer.consumer",
        title="Datanommer consumer",
        release_notes_url="https://github.com/fedora-infra/datanommer/releases/tag/{version}",
    ),
    App(
        name="datanommer.commands",
        title="Datanommer commands",
        release_notes_url="https://github.com/fedora-infra/datanommer/releases/tag/{version}",
    ),
    App(
        name="fedora-messaging",
        title="Fedora Messaging",
        release_notes_url="https://github.com/fedora-infra/fedora-messaging/releases/tag/v{version}",
    ),
    App(
        name="bodhi",
        title="Bodhi",
        release_notes_url="https://github.com/fedora-infra/bodhi/releases/tag/{version}",
    ),
    App(
        name="fmn",
        title="FMN",
        release_notes_url="https://github.com/fedora-infra/fmn/releases/tag/v{version}",
    ),
    App(
        name="anitya",
        title="Anitya",
        release_notes_url="https://github.com/fedora-infra/anitya/releases/tag/{version}",
    ),
    App(
        name="the-new-hotness",
        title="The New Hotness",
        release_notes_url="https://github.com/fedora-infra/the-new-hotness/releases/tag/{version}",
    ),
    App(
        name="maubot-fedora",
        title="Fedora Maubot",
        release_notes_url="https://github.com/fedora-infra/maubot-fedora/releases/tag/v{version}",
    ),
    App(
        name="koschei",
        title="Koschei",
        release_notes_url="https://github.com/fedora-infra/koschei/releases/tag/{version}",
    ),
    App(
        name="pagure",
        title="Pagure",
        release_notes_url="https://docs.pagure.org/pagure/changelog.html",
    ),
    App(
        name="mdapi",
        title="MD API",
        release_notes_url="https://github.com/fedora-infra/mdapi/releases/tag/{version}",
    ),
    App(
        name="fedora-infra/rpmautospec",
        title="RPM Autospec",
        release_notes_url="https://pagure.io/fedora-infra/rpmautospec/commits/main",
    ),
    App(
        name="pagure-dist-git",
        title="Dist Git",
        release_notes_url="https://pagure.io/pagure-dist-git/commits/{version}",
    ),
    App(
        name="monitor-gating",
        title="CI Monitor Gating",
        release_notes_url="https://pagure.io/fedora-ci/monitor-gating/commits/production",
    ),
    App(
        name="sigul",
        title="Sigul",
        release_notes_url="https://pagure.io/sigul/releases",
    ),
    App(
        name="robosignatory",
        title="Robosignatory",
        release_notes_url="https://pagure.io/robosignatory/commits/master",
    ),
    App(
        name="duffy",
        title="CentOS CI Duffy",
        release_notes_url="https://github.com/CentOS/duffy/compare/v{old_version}...v{version}",
    ),
]


@dataclass
class Update:
    app: App
    datetime: datetime
    version: str
    old_version: str

    def _compare_version_slot(self, slot):
        return self.old_version.split(".")[slot] == self.version.split(".")[slot]

    @property
    def is_major(self):
        return not self._compare_version_slot(0)

    @property
    def is_minor(self):
        return not self.is_major and not self._compare_version_slot(1)

    @property
    def update_type(self):
        if self.is_major:
            return "major"
        elif self.is_minor:
            return "minor"
        else:
            return "patch"

    @property
    def release_notes(self):
        return self.app.release_notes_url.format(**asdict(self))


def get_all_pages(url, params=None):
    http = requests.Session()
    params = params or {}
    params["rows_per_page"] = 100
    params["page"] = 1
    total_pages = None
    with click.progressbar(
        length=total_pages or 1,
        item_show_func=lambda p: f"Page {p or 1}/{total_pages or '?'}",
    ) as bar:
        while True:
            response = http.get(url, params=params)
            response.raise_for_status()
            response = response.json()
            total_pages = response["pages"]
            bar.length = total_pages
            yield response["raw_messages"]
            if params["page"] == total_pages:
                break
            params["page"] += 1
            bar.update(1, params["page"])


def get_messages_from_datagrepper(base_url, duration):
    url = urljoin(base_url, "v2/search")
    duration = 86400 * duration
    for messages in get_all_pages(url, {"topic": TOPIC, "delta": duration}):
        yield from messages


def get_messages_from_file(base_url, duration):
    for fn in sorted(glob("updates-today-*.json")):
        with open(fn) as fh:
            yield from json.load(fh)


def get_messages(base_url, duration):
    # yield from get_messages_from_file(base_url, duration)
    yield from get_messages_from_datagrepper(base_url, duration)


def get_updates(base_url, duration):
    apps_by_name = {a.name: a for a in APPS}
    for message in get_messages(base_url, duration):
        name = message["body"]["project"]["name"]
        try:
            app = apps_by_name[name]
        except KeyError:
            continue
        try:
            old_version = message["body"]["message"]["old_version"]
        except KeyError:
            try:
                old_version = message["body"]["project"]["versions"][1]
            except IndexError:
                print(name)
                print(message["body"]["project"])
                raise
        yield Update(
            app=app,
            datetime=datetime.fromtimestamp(message["body"]["project"]["updated_on"]),
            version=message["body"]["project"]["version"],
            old_version=old_version,
        )


@click.command()
@click.option("-d", "--duration", type=int, default=7)
@click.option("--staging", is_flag=True)
def main(duration, staging):
    base_url = DATAGREPPER_STG if staging else DATAGREPPER
    updates = []
    for update in get_updates(base_url, duration):
        updates.append(update)
    if not updates:
        print(f"None of our apps were released in the last {duration} days.")
    for update in updates:
        print(
            f"{update.update_type.title()} update of {update.app.title} from "
            f"{update.old_version or '?'} to {update.version} on "
            f"{update.datetime.strftime('%Y-%m-%d')}: {update.release_notes}"
        )


if __name__ == "__main__":
    main()
