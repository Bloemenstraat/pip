from __future__ import absolute_import

import errno
import logging
import operator
import os
import shutil
from optparse import SUPPRESS_HELP

from pip._vendor import pkg_resources

from pip._internal.cache import WheelCache
from pip._internal.cli import cmdoptions
from pip._internal.cli.base_command import RequirementCommand
from pip._internal.cli.status_codes import ERROR
from pip._internal.exceptions import (
    CommandError, InstallationError, PreviousBuildDirError,
)
from pip._internal.locations import distutils_scheme, virtualenv_no_global
from pip._internal.operations.check import check_install_conflicts
from pip._internal.operations.prepare import RequirementPreparer
from pip._internal.req import RequirementSet, install_given_reqs
from pip._internal.req.req_tracker import RequirementTracker
from pip._internal.resolve import Resolver
from pip._internal.utils.filesystem import check_path_owner
from pip._internal.utils.misc import (
    ensure_dir, get_installed_version,
    protect_pip_from_modification_on_windows,
)
from pip._internal.utils.temp_dir import TempDirectory
from pip._internal.wheel import WheelBuilder

#My imports !!!
from .list import ListCommand
import json
import subprocess
import os
from pip._internal.commands import commands_dict

logger = logging.getLogger(__name__)


class UpdateCommand(RequirementCommand):
    """
    New command added by Bloemenstraat 21.02.2019.

    Upgrades all packages installed to the newest version.
    """
    name = 'update'

    usage = """
      %prog
      No options available (or needed)."""

    summary = 'Upgrades all packages.'

    def __init__(self, *args, **kw):
        super(UpdateCommand, self).__init__(*args, **kw)

    def run(self, options, args):

        try:
            logger.info('Fetching the list of outdated packages...')
            packs = subprocess.check_output(['pip', 'list', '--outdated', '--format', 'json'])
            packs = json.loads(packs)

        except FileNotFoundError as e:
            logger.info('The \'pip\' command doesn\'t on your system.')
        except subprocess.CalledProcessError as e:
            pass

        else:
            if (os.getuid() == 0):
                cmd = ['sudo', 'pip', 'install', '--upgrade']
            else:
                cmd = ['pip', 'install', '--upgrade']

            not_updated = []

            for pack in packs:
                try:
                    subprocess.check_call(cmd + [pack['name']])
                except subprocess.CalledProcessError:
                    logger.info('{} couldn\'t be updated'.format(pack['name']))
                    not_updated.append(pack['name'])

            #Print the packages that couldn't be installed
            if not_updated:
                logger.info('The following packages could not be installed : {}'.format(str(not_updated)))
