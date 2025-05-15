#!/usr/bin/env python3
import subprocess
import os
import sys


def ldd(binary_path: str) -> list[str]:
    output = subprocess.check_output(['ldd', binary_path], text=True)
    return output.splitlines()


def ldd_paths(binary_path: str) -> tuple[list[str], list[str]]:
    default_dirs = ['/lib', '/usr/lib', '/lib64', '/usr/lib64']
    
    not_found: list[str] = []
    paths: list[str] = []
    for line in ldd(binary_path):
        if 'ld-linux' in line or 'linux-vdso' in line:
            continue

        line = line.strip()

        try:
            [dep_name, abs] = line.split(' => ')

        except ValueError:
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
                
        else:
            if ' (' not in abs:
                not_found.append(dep_name)
                continue

            [abs, _] = abs.split(' (')
            paths.append(abs)

    return (paths, not_found)


if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f'Usage: {sys.argv[0]} <binary_path>', file=sys.stderr)
        sys.exit(1)
    
    (paths, not_found) = ldd_paths(sys.argv[1])
    print('\n'.join(paths))
    if not_found:
        print('\n'.join([x + ' NOT FOUND' for x in not_found]), file=sys.stderr)
        sys.exit(1)