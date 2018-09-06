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
from .getToken import GetToken



class Token:

    def __init__(self, config, comm):

        super().__init__()

        self._comm = comm
        self._gpio = None
        self._cfg = config

        self._is_trigger = False
        self._is_enabled = config.getBool('OAuth', 'use_oauth')

        self.initOAuth(config)

    def initOAuth(self, config):

        while self._is_enabled:
            GetToken(self._cfg)
            time.sleep(1800)
        #else:
         #   logging.info('GPIO disabled')

    def run(self):

        return True

