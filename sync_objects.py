#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# sync this openshift objects:
# *
#
# assume oc login and oc project has done before
#
# input:
# * config to apply
import sys
import yaml
import subprocess

object_operation = {
    "Service": {
        "alias": "svc",
        "create": "create",
        "patch": "apply",
        "delete": "delete",
        "get": "get"
    },
    "Route": {
        "alias": "route",
        "create": "create",
        "patch": "apply",
        "delete": "delete",
        "get": "get"
    },
    "DeploymentConfig": {
        "alias": "dc",
        "create": "create",
        "patch": "apply",
        "delete": "delete",
        "get": "get"
    },
    "HorizontalPodAutoscaler": {
        "alias": "hpa",
        "create": "create",
        "patch": "replace",
        "delete": "delete",
        "get": "get"
    },
}

with open(sys.argv[1]) as _:
    objects = yaml.load_all(_)

    synced_objects = []
    object_names = ""
    for object in objects:
        # get object name
        object_name = object["metadata"]["name"]
        # Check object exists in openshift
        p = subprocess.Popen(["oc", object_operation[object["kind"]]["get"],
                             object_operation[object["kind"]]["alias"],
                             object["metadata"]["name"],
                             "-o", "yaml"], stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
        res = p.stdout.readlines()
        #print res
        #print len(res)
        #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
        if (len(res) > 0):
            # it exists -> patch
            print (("patch: oc " + object_operation[object["kind"]]["patch"] +
                    " " + "-f -"))

            p = subprocess.Popen(["oc", object_operation[object["kind"]]["patch"],
                                  "-f", "-"],
                                  stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            p.stdin.write(yaml.dump(object, default_flow_style=False))
            p.stdin.close()
        else:
            # it does not exists -> create it
            print (("create: oc " + object_operation[object["kind"]]["create"] +
                    " " + "-f -"))
            sys.stdout.flush()
            p = subprocess.Popen(["oc", object_operation[object["kind"]]["create"],
                                 "-f", "-"],
                                 stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            p.stdin.write(yaml.dump(object, default_flow_style=False))
            p.stdin.close()

        synced_objects.append(object["kind"])

    # Remove not existent objects
    print synced_objects
    for object_kind in object_operation.keys():
        if not(object_kind in synced_objects):
            # Check if the object exists in openshift and remove it
            p = subprocess.Popen(["oc", object_operation[object_kind]["get"],
                                 object_operation[object_kind]["alias"],
                                 object_name,
                                 "-o", "yaml"], stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
            res = p.stdout.readlines()
            #print res
            #print len(res)
            #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
            if (len(res) > 0):
                # it must not exists -> removeit
                print (("delete: oc " + object_operation[object_kind]["delete"] +
                        " " + "-f -"))
                sys.stdout.flush()
                p = subprocess.Popen(["oc", object_operation[object_kind]["delete"],
                                     object_operation[object_kind]["alias"],
                                     object_name], stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE)


