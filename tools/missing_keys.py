#!/usr/bin/env python3

import pathlib
import sys
import yaml

error_count = 0
nodepool_dir = pathlib.Path("nodepool")
for config_file in nodepool_dir.glob("*.zuul.ansible.com.yaml"):
    config = yaml.safe_load(config_file.open())
    root_label_names = [i["name"] for i in config["labels"]]
    for provider in config["providers"]:
        if "cloud-images" not in provider:
            print(
                (
                    "provider {name} does not have a `cloud-images` "
                    "section, skipping"
                ).format(**provider)
            )
            continue
        cloud_image_names = [i["name"] for i in provider["cloud-images"]]
        for pool in provider["pools"]:
            for label in pool["labels"]:
                if label["name"] not in root_label_names:
                    print(
                        ("{provider_name}: label `{name}` not found in root "
                            "labels section ").format(
                            provider_name=provider["name"],
                            **label
                        )
                    )
                    error_count += 1
                if "cloud-image" not in label:
                    continue
                if label["cloud-image"] not in cloud_image_names:
                    print(
                        ("{provider_name}: label `{name}`'s cloud-image key "
                            "refer to `{cloud-image}` that is not defined in "
                            "the cloud-images section of the provider.").format(
                            provider_name=provider["name"],
                            **label
                        )
                    )
                    error_count += 1
if error_count:
    sys.exit(1)
