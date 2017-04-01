#!/usr/bin/python

import subprocess
import json
import argparse
import sys
import os


FILE_PATH = os.path.abspath(__file__)


def run(cmd):
    stdout = subprocess.check_output(cmd)
    return json.loads(stdout)


ceph_s_func_mapping = {
    'osd_num': lambda x: x['osdmap']['osdmap']['num_osds'],
    'osd_up_num': lambda x: x['osdmap']['osdmap']['num_up_osds'],
    'osd_in_num': lambda x: x['osdmap']['osdmap']['num_in_osds'],
    'total': lambda x: x['pgmap']['bytes_total'],
    'used': lambda x: x['pgmap']['bytes_used'],
    'pg_num': lambda x: x['pgmap']['num_pgs'],
    'read': lambda x: x['pgmap']['read_bytes_sec'],
    'write': lambda x: x['pgmap']['write_bytes_sec'],
    'read_iops': lambda x: x['pgmap']['read_op_per_sec'],
    'write_iops': lambda x: x['pgmap']['write_op_per_sec'],
    }


def ceph_s(key):
    cmd = ['docker', 'exec', 'ceph_mon', 'ceph', '-f', 'json', '-s']
    status = run(cmd)
    return ceph_s_func_mapping[key](status)


def ceph_health():
    cmd = ['docker', 'exec', 'ceph_mon', 'ceph', '-f', 'json', 'health']
    status = run(cmd)
    return status['overall_status']


def main():
    choices = list(ceph_s_func_mapping.keys()) + ['health']
    parse = argparse.ArgumentParser()
    parse.add_argument('--target', '-t',
                       required=False,
                       choices=choices)
    parse.add_argument('--print-usage',
                       '-p',
                       required=False,
                       action='store_true')
    parse.add_argument('-T', '--test',
                       required=False,
                       action='store_true')
    conf = parse.parse_args(sys.argv[1:])

    if conf.print_usage:
        str_format = 'UserParameter=ceph.%s,%s --target %s'
        usage = []
        for target in choices:
            usage.append(str_format % (target, FILE_PATH, target))
        print('\n'.join(usage))
        return

    if conf.test:
        for target in ceph_s_func_mapping:
            print('%s: %s' % (target, ceph_s(target)))
        print('%s: %s' % ('health', ceph_health()))
        return

    if conf.target in ceph_s_func_mapping.keys():
        print(ceph_s(conf.target))
    else:
        print(ceph_health())


if __name__ == "__main__":
    main()
