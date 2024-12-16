#!/usr/bin/python3

import os
import requests


def main():
    ranges_url = os.environ.get('RANGES_URL', 'https://ip-ranges.amazonaws.com/ip-ranges.json')
    region_prefix = os.environ.get('REGION_PREFIX', 'eu-west')
    ip_whitelist = os.environ.get('IP_WHITELIST', '/var/ranges/ip_whitelist.txt')

    ranges = requests.get(ranges_url).json()

    with open(ip_whitelist, 'w') as file:
        for r in ranges['prefixes']:
            if r['region'].startswith(region_prefix):
                file.write(r['ip_prefix'] + '\n')


if __name__ == "__main__":
    main()
