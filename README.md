# Anitya scripts
Various useful scripts for [Anitya](https://github.com/release-monitoring/anitya)

## anitya_del_last_version
This script removes last version from list of project ids specified in a file.
This script is useful, if you need to send update messages again for large amount of projects.
Anitya FAS account with admin rights is needed to be able to do this.

## anitya_get_projects_by_packages
Script for receiving project ids in Anitya for list of packages.

## anitya_get_projects_by_ecosystem
Script for receiving project ids in Anitya for specific ecosystem.

## anitya_get_packages_by_partial_name
Script for receiving packages names in Anitya by partial name of the package. For example,
it will allow you to find all packages ending with "-delete".
