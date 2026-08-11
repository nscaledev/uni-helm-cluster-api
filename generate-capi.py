#!/usr/bin/env python3

import argparse
import re
import sys

MANAGEMENT_KUBERNETES_VERSION = ">=1.32.0-0 <1.37.0-0"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', help="Chart version")
    parser.add_argument('-c', '--capi-version', help='Cluster API version')
    parser.add_argument('subcharts', nargs='+', help="Subcharts to include")

    args = parser.parse_args()

    chunks = []

    with open('charts/cluster-api/values.yaml.tmpl') as file:
        chunks.append(file.read())

    for chart in args.subcharts:
        chunk = [f"{chart}:\n"]

        with open(f'charts/{chart}/values.yaml') as file:
            chunk.extend(f"  {x}" for x in file.readlines())

        chunks.append(''.join(chunk))

    with open('charts/cluster-api/values.yaml', 'w') as file:
        file.write('\n'.join(chunks))

    with open(f'charts/cluster-api/Chart.yaml', 'w') as file:
        file.write("apiVersion: v2\n")
        file.write(f"appVersion: {args.capi_version}\n")
        file.write(f"kubeVersion: '{MANAGEMENT_KUBERNETES_VERSION}'\n")
        file.write("name: cluster-api\n")
        file.write("description: A Helm chart to deploy Cluster API\n")
        file.write("type: application\n")
        file.write(f"version: {args.version}\n")
        file.write("icon: https://assets.unikorn-cloud.org/assets/images/logos/dark-on-light/icon.png\n")
        file.write("\n")
        file.write("dependencies:\n")

        for chart in args.subcharts:
            file.write(f"- name: {chart}\n")
            file.write(f"  version: {args.version}\n")
            file.write(f"  repository: file://../{chart}\n")
            # Oh for want of a better way of doing this...
            matches = re.match(r'^cluster-api-(?:bootstrap|control-plane|provider)-(.*)', chart)
            if matches:
                file.write(f"  condition: {matches[1]}.enabled\n")

if __name__ == '__main__':
    main()
