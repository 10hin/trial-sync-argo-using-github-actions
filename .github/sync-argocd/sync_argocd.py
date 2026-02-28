#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from functools import partial

from kubernetes import client, config


APPS_API_GROUP = 'argoproj.io'
APPS_API_VERSION = 'v1alpha1'
APPS_RESOURCE_PLURAL = 'applications'


async def list_application_for_all_namespaces(client):
    loop = asyncio.get_event_loop()
    func = partial(
        client.list_custom_object_for_all_namespaces,
        APPS_API_GROUP,
        APPS_API_VERSION,
        APPS_RESOURCE_PLURAL,
    )
    return await loop.run_in_executor(None, func)


async def sync_applications(client, namespace, name):
    loop = asyncio.get_event_loop()
    func = partial(
        client.patch_namespaced_custom_object,
        APPS_API_GROUP,
        APPS_API_VERSION,
        namespace,
        APPS_RESOURCE_PLURAL,
        name,
        {
            'operation': {
                'initiatedBy': {
                    'username': 'github-actions',
                },
                'sync': {
                    'revision': 'main',
                    'prune': True,
                    'syncStrategy': {
                        'hook': {
                            'force': True,
                        },
                    },
                },
            },
        },
    )
    return await loop.run_in_executor(None, func)


async def main():
    config.load_kube_config()
    custom_objects_api = client.CustomObjectsApi()
    apps = await list_application_for_all_namespaces(custom_objects_api)

    synces = await asyncio.gather(*[
        sync_applications(
            custom_objects_api,
            app['metadata']['namespace'],
            app['metadata']['name']
        )
        for app in apps['items']
    ])
    print(synces)


if __name__ == '__main__':
    asyncio.run(main())
