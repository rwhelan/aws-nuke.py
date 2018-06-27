#!/usr/bin/env python3


import sys
import os

from lib import dependency_sort

if len(sys.argv) <= 1:
    print("No operation given", file = sys.stderr)
    sys.exit(1)

enable_global_services = True if (len(sys.argv) == 3) and (sys.argv[2] == 'global') else False


### Import all the nukers
from nukes import BaseNuker

base_path = '/'.join(sys.argv[0].split('/')[:-1])
if not base_path: base_path = os.getcwd()

module_path = base_path+'/nukes'

for module_file in os.listdir(module_path):
    if not module_file.endswith('.py'): continue
    if module_file in ("__init__.py"): continue

    module_name = module_file[:-3]
    __import__("nukes."+module_name)


if enable_global_services:
    enabled_modules = [i() for i in BaseNuker.__subclasses__() if i.enabled]
else:
    enabled_modules = [i() for i in BaseNuker.__subclasses__() if i.enabled and i.global_service == False]

sorted_modules = dependency_sort(enabled_modules)


### Setup and Parse command line options
def unknown_op(_):
    print(f"Unknown operation: {sys.argv[1]}", file = sys.stderr)
    sys.exit(1)

def list_resources(modules):
    for module in modules:
        print(f"============ {module.name} ============")
        for i in module.list_resources():
            print (f"    {i}")
        print()

def nuke_resources(modules):
    [i.nuke_resources() for i in modules]

ops = {
    "list": list_resources,
    "nuke": nuke_resources,
    "_unknown": unknown_op
}

op = ops.get(sys.argv[1], ops['_unknown'])

### Go!
op(sorted_modules)
