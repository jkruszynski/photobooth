#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging

import time
from ..Threading import Workers
from .uploadPhoto import UploadPhoto
import glob
import shutil



class Upload:

    def __init__(self, config, comm):

        super().__init__()

        self._comm = comm
        self._cfg = config

        self._is_enabled = config.getBool('OAuth', 'use_oauth')

        self.initUpload(config)

    def initUpload(self, config):


        while self._is_enabled:
            files = glob.glob('prep/*')
            if len(files) != 0:
                for file in files:
                    UploadPhoto(self._cfg, file)
                    dest = file.replace('prep','archive')
                    shutil.move(file, dest)
            time.sleep(30)

    def run(self):

        return True

