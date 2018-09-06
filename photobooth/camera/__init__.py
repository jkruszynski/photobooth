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

from PIL import Image, ImageOps

from .PictureDimensions import PictureDimensions
from .. import StateMachine
from ..Threading import Workers
import time

# Available camera modules as tuples of (config name, module name, class name)
modules = (
    ('python-gphoto2', 'CameraGphoto2', 'CameraGphoto2'),
    ('gphoto2-cffi', 'CameraGphoto2Cffi', 'CameraGphoto2Cffi'),
    ('gphoto2-commandline', 'CameraGphoto2CommandLine',
     'CameraGphoto2CommandLine'),
    ('opencv', 'CameraOpenCV', 'CameraOpenCV'),
    ('picamera', 'CameraPicamera', 'CameraPicamera'),
    ('dummy', 'CameraDummy', 'CameraDummy'))


class Camera:

    def __init__(self, config, comm, CameraModule):

        super().__init__()

        self._comm = comm
        self._cfg = config
        self._cam = CameraModule

        self._cap = None
        self._pic_dims = None

        self._is_preview = self._cfg.getBool('Photobooth', 'show_preview')
        self._is_keep_pictures = self._cfg.getBool('Picture', 'keep_pictures')
        self._add_banner = self._cfg.getBool('Picture','add_banner')
        self._banner_location = config.get('Picture', 'banner_location')
        self._num_pics = int(config.get('Picture', 'num_pics'))
        self._add_background = self._cfg.getBool('Picture','add_background')
        self._background_location = config.get('Picture', 'background_location')

    def startup(self):

        self._cap = self._cam()
        self._pic_dims = PictureDimensions(self._cfg,
                                           self._cap.getPicture().size)
        self._is_preview = self._is_preview and self._cap.hasPreview

        logging.info('Using camera {} preview functionality'.format(
            'with' if self._is_preview else 'without'))

        self.setIdle()

        self._comm.send(Workers.MASTER, StateMachine.CameraEvent('ready'))

    def teardown(self, state):

        if self._cap is not None:
            self._cap.cleanup()

    def run(self):

        for state in self._comm.iter(Workers.CAMERA):
            self.handleState(state)

        return True

    def handleState(self, state):

        if isinstance(state, StateMachine.StartupState):
            self.startup()
        elif isinstance(state, StateMachine.GreeterState):
            self.prepareCapture()
        elif isinstance(state, StateMachine.CountdownState):
            self.capturePreview()
        elif isinstance(state, StateMachine.CaptureState):
            self.capturePicture(state)
        elif isinstance(state, StateMachine.AssembleState):
            self.assemblePicture()
        elif isinstance(state, StateMachine.TeardownState):
            self.teardown(state)

    def setActive(self):

        self._cap.setActive()

    def setIdle(self):

        if self._cap.hasIdle:
            self._cap.setIdle()

    def prepareCapture(self):

        self.setActive()
        self._pictures = []

    def capturePreview(self):

        if self._is_preview:
            while self._comm.empty(Workers.CAMERA):
                picture = ImageOps.mirror(self._cap.getPreview())
                self._comm.send(Workers.GUI,
                                StateMachine.CameraEvent('preview', picture))

    def capturePicture(self, state):

        self.setIdle()
        picture = self._cap.getPicture()
        self._pictures.append(picture)
        self.setActive()

        if self._is_keep_pictures:
            self._comm.send(Workers.WORKER,
                            StateMachine.CameraEvent('capture', picture))

        if state.num_picture < self._num_pics:
            self._comm.send(Workers.MASTER,
                            StateMachine.CameraEvent('countdown'))
        else:
            self._comm.send(Workers.MASTER,
                            StateMachine.CameraEvent('assemble'))

    def assemblePicture(self):
        # time.sleep(3) #creating collage was corrupting 4th image. Added sleep to give more proc time
        time.sleep(3)
        self.setIdle()

        #newSize = (self._pic_dims.outputSize[0], self._pic_dims.outputSize[1])

        if (self._add_background):
            picture = Image.open(self._background_location)
        else:
            picture = Image.new('RGB', self._pic_dims.outputSize, (255, 255, 255))

        for i in range(self._num_pics):
            resized = self._pictures[i].resize(self._pic_dims.thumbnailSize)
            picture.paste(resized, self._pic_dims.thumbnailOffset[i])

        if (self._add_banner):
            picture = self.addBanner(picture)

        
        self._comm.send(Workers.MASTER,
                        StateMachine.CameraEvent('review', picture))
        self._pictures = []
        
    def addBanner(self, picture):

        try:
            banner = Image.open(self._banner_location)
        except:
            banner = Image.new('RGB', (picture.size[0], round(picture.size[0] * .1)), (255, 255, 255))

        images = [picture, banner]
        logging.info('image 1 size ' + str(images[0].size) + '\nimage 2 size ' + str(images[1].size))
        widths, heights = zip(*(i.size for i in images))

        total_height = sum(heights)
        max_width = max(widths)

        new_im = Image.new('RGB', (max_width, total_height), (255, 255, 255))

        y_offset = 0
        for im in images:
          new_im.paste(im, (0,y_offset))
          y_offset += im.size[1]
        
        return new_im
        
        
        
        
