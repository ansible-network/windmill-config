#!/usr/bin/env python3

import pathlib
import sys
import yaml


def search_dup_name(config_file, root, path):
    seens = []
    error_count = 0
    for i in root:
        if i["name"] in seens:
            print(
                ("{config_file}: duplicated name in {path}: {name}").format(
                    config_file=config_file, name=i["name"], path=path
                )
            )
            error_count += 1
        seens.append(i["name"])
    return error_count


error_count = 0
nodepool_dir = pathlib.Path("nodepool")
for config_file in nodepool_dir.glob("*.zuul.ansible.com.yaml"):
    config = yaml.safe_load(config_file.open())

    error_count += search_dup_name(config_file, config["labels"], "labels/")
    for provider in config["providers"]:
        for key in ["diskimages", "cloud-images", "pools"]:
            if key in provider:
                error_count += search_dup_name(
                    config_file,
                    provider[key],
                    "provider/{name}/{key}/".format(key=key, **provider),
                )

        for pool in provider.get("pools", []):
            error_count += search_dup_name(
                config_file,
                pool["labels"],
                "provider/{name}/pools/labels/".format(**provider),
            )

if error_count:
    sys.exit(1)
