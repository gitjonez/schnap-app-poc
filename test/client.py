import re
import sys
import time
import requests
import concurrent.futures
from collections import Counter
from requests.exceptions import Timeout


def get_version(health_url, recomp, timeout=10):
    try:
        response = requests.get(health_url, timeout=timeout)
    except Timeout:
        return (-1, 'timeout')

    status = response.status_code
    match = recomp.search(response.text)
    if match:
        version = match.group(1)
    else:
        version = ''

    return (status, version)


if __name__ == '__main__':

    health_url = 'http://schnap.jonez.tech/health/'
    recomp = re.compile(r'Version: (\d+\.\d+\.\d+)')
    status_counts: Counter = Counter()
    version_counts: Counter = Counter()

    while True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for _ in range(20):
                futures.append(executor.submit(get_version, health_url,
                                               recomp))
            for future in concurrent.futures.as_completed(futures):
                status, version = future.result()
                status_counts[status] += 1
                version_counts[version] += 1

        print(f'statuses: ')
        for stat, cnt in status_counts.items():
            print(f' {stat}: {cnt}', end='')
        print(f'\nversions: ')
        for ver, cnt in version_counts.items():
            print(f' {ver}: {cnt}', end='')
        print('\n')

        time.sleep(5)
