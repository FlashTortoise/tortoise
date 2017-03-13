import os

import json
import cv2
import string
import random
from contextlib import contextmanager

from .globals import ctx
from . import config

ctx.recorder = None


@contextmanager
def a_recorder(name=None):
    if ctx.recorder is not None:
        raise Exception('Already exist a recorder')

    ctx.recorder = Recorder(name)

    # noinspection PyProtectedMember
    with ctx.recorder._recoding():
        yield

    ctx.recorder = None


def get_recorder():
    if ctx.recorder is None:
        raise Exception('No recorder in this context')
    elif not isinstance(ctx.recorder, Recorder):
        raise Exception('It is not a recorder')
    else:
        return ctx.recorder


class Recorder(object):
    def __init__(self, name=None):
        if name is None:
            name = ''.join(random.sample(string.hexdigits, 8))
        self.name = name

        self.name_count = None
        self.data = None
        self.group_cache = None
        self._insert = self._insert_one

    def _get_storage_path(self):
        return os.path.join(config.RECORDER_PATH, self.name)

    def _get_incremental_name(self):
        if self.name_count is None:
            file_names = [
                int(name) for name in os.listdir(self._get_storage_path())
                if name.split()[0].isdigit()]
            if len(file_names) == 0:
                self.name_count = 0
            else:
                self.name_count = max(file_names)

        return self.name_count

    def _insert_one(self, key, val):
        self.data.append({key: val})

    def _insert_group(self, key, val):
        self.group_cache[key] = val

    def record_img(self, name, img):
        file_name = self._get_incremental_name() + '.jpg'
        cv2.imwrite(
            os.path.join(
                self._get_storage_path(),
                file_name
            ), img
        )

        self._insert(name, file_name)

    def record_plain(self, name, var):
        self._insert(name, var)

    @contextmanager
    def a_group(self):
        self.group_cache = {}
        self._insert = self._insert_group
        yield
        self._insert = self._insert_one
        self.group_cache = None

    @contextmanager
    def _recording(self):
        file_path = os.path.join(self._get_storage_path(), self.name + 'json')
        try:
            with open(file_path) as f:
                self.data = json.load(f)
        except IOError as e:
            if e.errno == 2:
                self.data = []
            else:
                raise e

        yield

        f = open(file_path, 'w')
        json.dump(self.data, f)
        f.close()
