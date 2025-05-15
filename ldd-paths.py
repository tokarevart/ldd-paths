#!/usr/bin/env python3
import subprocess
import os
import sys
import argparse
from typing import NoReturn


def abort(msg: str) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(1)


def ldd(binary_path: str) -> list[str]:
    try:
        output = subprocess.run(['ldd', binary_path],
                                text=True, capture_output=True, check=True)
        return output.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        abort(f'ldd failed: exit code = {e.returncode}, error = {e}')


def ldd_paths(binary_path: str) -> tuple[list[str], list[str]]:
    default_dirs = ['/lib', '/usr/lib', '/lib64', '/usr/lib64']

    not_found: list[str] = []
    paths: list[str] = []
    for line in ldd(binary_path):
        if 'ld-linux' in line or 'linux-vdso' in line:
            continue

        line = line.strip()
        parts = line.split(' => ')
        if len(parts) == 1:
            [dep_name, _] = line.split(' (')
            if os.path.isabs(dep_name):
                paths.append(dep_name)
                continue

            found = False
            for dir in default_dirs:
                path = os.path.join(dir, dep_name)
                if os.path.exists(path):
                    paths.append(path)
                    found = True
                    break

            if not found:
                not_found.append(dep_name)
                continue

        elif len(parts) == 2:
            [dep_name, abs] = line.split(' => ')

            if ' (' not in abs:
                not_found.append(dep_name)
                continue

            [abs, _] = abs.split(' (')
            paths.append(abs)

        else:
            abort(f'unexpected line format: {line}')

    return (paths, not_found)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Resolve and print absolute paths of dynamic dependencies using ldd'
    )
    parser.add_argument('binary_path',
                        help='Path to the binary file to analyze')
    args = parser.parse_args()

    (paths, not_found) = ldd_paths(args.binary_path)

    print('\n'.join(paths))
    if not_found:
        abort('\n'.join([x + ' NOT FOUND' for x in not_found]))
