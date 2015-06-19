#!/usr/bin/python
#coding: utf-8 -*-

# (c) 2015, Michael Kashin <m.kashin84@gmail.com>
#
# This file is part of Ansible
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
DOCUMENTATION = '''
---
module: cisco_scenarios
short_description: parses the scenario file and stores it in global variable
'''
EXAMPLES = '''
- local_action: cisco_scenarios_combine
'''

import yaml
import re

SCENARIO_FILE = "scenarios/all.txt"
GROUP_VAR_FILE = "group_vars/all.yml"

class ScenarioParser(object):

    def __init__(self):
        self.rc = 0
        self.storage = dict()
        self.file_content = dict()

    def open(self):
       try:
            with open(GROUP_VAR_FILE, 'r') as fileObj:
                self.file_content = yaml.load(fileObj)
       except:
           open(GROUP_VAR_FILE, 'w').close()

    def read(self):
        scenario_number = 0
        scenario_step   = 0
        scenario_name   = ''
        # compile regex pattern matching scenario name
        name_pattern = re.compile(r'^(\d+)\.?\s+(.*)')
        # compile regex pattern matching scenario step
        step_pattern = re.compile(r'.*from\s+([\d\w]+)\s+to\s+([\d\w]+)\s+via\s+([\d\w]+,*\s*[\d\w]+)*')
        with open(SCENARIO_FILE, 'r') as fileObj:
            for line in fileObj:
                # ignore commented and empty lines
                if not line.startswith('#') and len(line) > 3:
                    # lowercase all for simplicity
                    line = line.lower()
                    name_match = name_pattern.match(line)
                    step_match = step_pattern.match(line)
                    if name_match:
                        scenario_number = name_match.group(1) 
                        scenario_name   = name_match.group(2)
                        scenario_steps  = [scenario_name, []] 
                        self.storage[scenario_number] = scenario_steps
                    elif step_match:
                        from_device = step_match.group(1)
                        to_device = step_match.group(2)
                        via = step_match.group(3)
                        via_devices = [device_name.strip() for device_name in via.split(',')]
                        # if scenario number and name are set
                        if not scenario_number == 0 or scenario_name:
                            scenario_steps[1].append([from_device, to_device, via_devices]) 
                    else:
                        #something went wrong
                        self.rc = 1 
                    
                    
        
    def write(self):
       self.file_content['scenarios'] = self.storage
       if self.rc == 0:
           with open(GROUP_VAR_FILE, 'w+') as fileObj:
               yaml.safe_dump(self.file_content, fileObj, explicit_start=True, indent=3, allow_unicode=True)

def main():
    # creating module instance. accepting raw text output and abbreviation of command
    module = AnsibleModule(argument_spec=dict())
    parser = ScenarioParser()
    parser.open()
    parser.read()
    parser.write()
    if not parser.rc == 0:
        module.fail_json(msg="Failed to parse. Incorrect input.")
    else:
        module.exit_json(changed=False)

# import module snippets
from ansible.module_utils.basic import *
main()