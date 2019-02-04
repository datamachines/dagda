#
# Licensed to Dagda under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Dagda licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import argparse
import sys
from log.dagda_logger import DagdaLogger


class MonitorCLIParser:

    # -- Public methods

    # MonitorCLIParser Constructor
    def __init__(self):
        super(MonitorCLIParser, self).__init__()
        self.parser = DagdaMonitorParser(prog='dagda.py monitor', usage=monitor_parser_text)
        self.parser.add_argument('container_id', metavar='CONTAINER_ID', type=str)
        self.parser.add_argument('--start', action='store_true')
        self.parser.add_argument('--stop', action='store_true')
        self.args, self.unknown = self.parser.parse_known_args(sys.argv[2:])
        # Verify command line arguments
        status = self.verify_args(self.args)
        if status != 0:
            exit(status)

    # -- Getters

    # Gets docker container id
    def get_container_id(self):
        return self.args.container_id

    # Gets if start is requested
    def is_start(self):
        return self.args.start

    # Gets if stop is requested
    def is_stop(self):
        return self.args.stop

    # -- Static methods

    # Verify command line arguments
    @staticmethod
    def verify_args(args):
        if not args.start and not args.stop:
            DagdaLogger.get_logger().error('Missing arguments.')
            return 1
        elif args.start and args.stop:
            DagdaLogger.get_logger().error('Arguments --start & --stop: Both arguments can not be together.')
            return 2
        # Else
        return 0


# Custom parser

class DagdaMonitorParser(argparse.ArgumentParser):

    # Overrides the error method
    def error(self, message):
        self.print_usage()
        exit(2)

    # Overrides the format help method
    def format_help(self):
        return monitor_parser_text


# Custom text

monitor_parser_text = '''usage: dagda.py monitor [-h] CONTAINER_ID [--start] [--stop]

Your personal docker security monitor.

Positional Arguments:
  CONTAINER_ID          the input docker container id

Optional Arguments:
  -h, --help            show this help message and exit
  --start               start the monitoring over the container with
                        the input id
  --stop                stop the monitoring over the container with the
                        input id
'''