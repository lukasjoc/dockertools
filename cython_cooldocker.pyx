#!/usr/bin/env cython

import docker
from tabulate import tabulate
from termcolor import colored

cdef __format_timedelta(time_str, pattern="%Y-%m-%dT%H:%M:%S"):
    from datetime import timedelta, datetime
    delta = abs(datetime.strptime(datetime.strftime(datetime.today(), pattern), pattern)
                - datetime.strptime(time_str.split(".")[0], pattern))
    if delta.days >= 1:
        return f"> {delta.days} days ago"
    return f"{str(timedelta(seconds=int(delta.total_seconds())-3600))} ago"

cdef container_info(client):
    container_data = []
    for container in client.containers.list():
        attrs = container.attrs
        def get_container_ports():
            ports = attrs["NetworkSettings"]["Ports"]
            formatted_ports = ""
            for port, mapping in ports.items():
                if mapping != None:
                    for item in mapping:
                        formatted_ports += f"{item['HostIp']}:{item['HostPort']}->{port} "
                else:
                    formatted_ports += f"{port} "
            return formatted_ports

        def get_container_ip():
            net_id = attrs["NetworkSettings"]["IPAddress"]
            if net_id != "":
                return net_id
            if attrs["HostConfig"]["NetworkMode"] != "default":
                network_name = attrs["HostConfig"]["NetworkMode"]
                return attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]

        def get_docker_status():
            status = attrs["State"]["Status"]
            if "Health" in attrs["State"]:
                return f"{status} ({attrs['State']['Health']['Status']})"
            return status



        container_data.append([
            attrs["Config"]["Hostname"],
            attrs["Config"]["Image"],
            __format_timedelta(time_str=attrs["Created"]),
            get_docker_status(),
            get_container_ports(),
            attrs["Name"][1:],
            get_container_ip(),
        ])

    container_cols = [ "CONTAINER ID", "IMAGE", "CREATED", "STATUS", "PORTS", "NAMES", "IP ADDRESS" ]
    return container_data, container_cols

cdef image_info(client):
    image_data = []
    for image in client.images.list(filters={"dangling": False}):
        attrs = image.attrs
        def get_image_repo():
           if len(attrs["RepoTags"]) >= 1:
               return attrs["RepoTags"][0].split(":")[0]

        def get_image_tag():
           if len(attrs["RepoTags"]) >= 1:
               return attrs["RepoTags"][0].split(":")[1]

        def get_image_size():
            return attrs["Size"]/8/(1024**2)

        image_data.append([
            get_image_repo(),
            get_image_tag(),
            __format_timedelta(time_str=attrs["Created"]),
            get_image_size(),
        ])

    image_cols = [ "REPOSITORY", "TAG", "CREATED", "SIZE(MiB)" ]
    return image_data, image_cols

cdef net_info(client):
    net_data = []
    for net in client.networks.list(filters={"dangling": True}):
        attrs = net.attrs
        net_data.append([
            attrs['Id'][:7],
            attrs["Name"],
            attrs["Driver"],
            __format_timedelta(time_str=attrs["Created"]),
            attrs["Scope"],
            attrs["Internal"],
            attrs["Attachable"],
        ])

    net_cols = [ "NET ID", "NAME", "DRIVER", "CREATED", "SCOPE", "INTERNAL", "ATTACHABLE"]
    return net_data, net_cols

cdef vol_info(client):
    vol_data = []
    for vol in client.volumes.list():
        attrs = vol.attrs
        vol_data.append([
            attrs["Name"],
            attrs["Driver"],
            attrs["Scope"],
        ])

    vol_cols = [ "NAME", "DRIVER", "VOLUME", "SCOPE"]
    return vol_data, vol_cols

def cooldocker():
    try:
        cl = docker.from_env()
        container_data, container_cols = container_info(client=cl)
        print(f"[{colored(str(len(container_data)), color='cyan')}] {colored('CONTAINER', color='cyan')}:")
        print(tabulate(container_data, headers=container_cols))

        image_data, image_cols = image_info(client=cl)
        print(f"\n[{colored(str(len(image_data)), color='green')}] {colored('IMAGES', color='green')}:")
        print(tabulate(image_data, headers=image_cols))

        net_data, net_cols = net_info(client=cl)
        print(f"\n[{colored(str(len(net_data)), color='blue')}] {colored('NETS', color='blue')}:")
        print(tabulate(net_data, headers=net_cols))

        vol_data, vol_cols = vol_info(client=cl)
        if len(vol_data) >= 1:
            print(f"\n[{colored(str(len(net_data)), color='yellow')}] {colored('VOLUMES', color='yellow')}:")
            print(tabulate(vol_data, headers=vol_cols))
    except Exception as err:
        print(f"Docker Engine/Daemon not running. Please start it. ERR: {err}")

