import os

import string
import random
from contextlib import contextmanager
import json
import cv2
import numpy

from .globals import ctx
from . import config

import os
if not os.path.exists(config.RECORDER_PATH):
    raise Exception('Recording dir is not exist')

ctx.recorder = None


def finalize_recorders():
    if isinstance(ctx.recorder, Recorder):
        ctx.recorder.close()
ctx.finalization.append(finalize_recorders)


def get_recorder(name=None):
    # type: (str) -> Recorder
    """
    Use this function to get a recorder
    :param name: the name of recorder. If there is not specified,
    a random name will be used.
    :return: instance of Recorder
    """
    rec = ctx.recorder
    if rec is None:
        ctx.recorder = Recorder(name)
    else:
        if isinstance(rec, Recorder):
            if rec.name == name:
                pass
            else:
                rec.close()
                ctx.recorder = Recorder(name)
        else:
            raise Exception('It is not a recorder')
    return ctx.recorder


class Recorder(object):
    def __init__(self, name=None):
        if name is None:
            name = ''.join(random.sample(string.hexdigits, 8))
        self.name = name

        # Assign paths
        self._folder_path = os.path.join(config.RECORDER_PATH, self.name)
        self._record_path = os.path.join(self._folder_path, self.name + '.json')

        # Members initialization
        self.name_count = None
        self.data = None
        self.group_cache = None
        self._insert = self._insert_one

        # Make one if record folder is not exist
        if not os.path.exists(self._folder_path):
            os.mkdir(self._folder_path)

        # Load Json data if exist in the folder
        try:
            with open(self._record_path) as f:
                self.data = json.load(f)
        except IOError as e:
            if e.errno == 2:
                self.data = []
            else:
                raise e

    def _get_incremental_name(self):
        if self.name_count is None:
            # Case: the first run
            # Init the name count with the largest filename number + 1
            file_names = [
                int(name.split('.')[0])
                for name in os.listdir(self._folder_path)
                if name.split('.')[0].isdigit()
                ]
            if len(file_names) == 0:
                self.name_count = 0
            else:
                self.name_count = max(file_names) + 1
        else:
            # Case: non-first
            self.name_count += 1

        return str(self.name_count).rjust(8, '0')

    def _insert_one(self, key, val):
        self.data.append({key: val})

    def _insert_group(self, key, val):
        self.group_cache[key] = val

    def close(self):
        """
        Finalize a recorder. Call when destroy instances
        """
        f = open(self._record_path, 'w')
        json.dump(self.data, f)
        f.close()

    def record_img(self, name, img):
        # type: (str, numpy.ndarray) -> None
        """
        Record an image
        :param name: Specifying name of image
        :param img: The actual image data in type numpy.ndarray
        """
        file_name = self._get_incremental_name() + '.jpg'
        cv2.imwrite(
            os.path.join(
                self._folder_path,
                file_name
            ), img
        )

        self._insert(name, file_name)

    def record_plain(self, name, var):
        # type: (str, object) -> None
        """
        Record any non-image data like string and numbers
        :param name: Specifying name of variable
        :param var: The var that need recording
        """
        self._insert(name, var)

    @contextmanager
    def a_group(self):
        """
        Record data in a group
        Typical usage:
            with <some recorder>.a_group():
                <do some recording>
        """
        self.group_cache = {}
        self._insert = self._insert_group
        yield
        self._insert = self._insert_one
        self.data.append(self.group_cache)
        self.group_cache = None
