#!/usr/bin/python
import docker
import argparse
import logging
import sys
import json


logging.basicConfig()


def get_client(*args, **kwargs):
    try:
        client = docker.Client(*args, **kwargs)
    except AttributeError:
        client = docker.APIClient(*args, **kwargs)
    return client


def lld_container():
    client = get_client()
    containers = client.containers()
    data = []
    for container in containers:
        name = container['Names'][0][1:]
        data.append({"{#NAME}": name})
    return json.dumps({'data': data})


def get_container_stat(name, resource):
    client = get_client()
    stats = client.stats(name, stream=False)
    func_mapping = {
        'pids': lambda x: x['pids_stats']['current'],
        'ram': lambda x: x['memory_stats']['usage']
            }
    return func_mapping[resource](stats)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices=['list', 'get'],
                        help='action')
    parser.add_argument('container_name',
                        nargs='?',
                        help='container name')
    parser.add_argument('resource',
                        nargs='?',
                        choices=['pids', 'ram'],
                        help='Resource name')
    conf = parser.parse_args(sys.argv[1:])
    if conf.action == 'list' and not conf.resource:
        print(lld_container())
    elif conf.action == 'get' and conf.container_name and conf.resource:
        print(get_container_stat(conf.container_name,
                                 conf.resource))
    else:
        raise ValueError('Unknow parameters:%s', sys.argv[1:])


if __name__ == "__main__":
    main()
