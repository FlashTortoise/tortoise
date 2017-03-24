import os

import json
import cv2
import string
import random
from contextlib import contextmanager

import time

from .globals import ctx
from . import config

import os
if not os.path.exists(config.RECORDER_PATH):
    raise Exception('Recording dir is not exist')

ctx.recorder = None


def finalize_recorders():
    if isinstance(ctx.recorder, Recorder):
        ctx.recorder.teardown()
ctx.finalization.append(finalize_recorders)


def get_recorder(name=None):
    rec = ctx.recorder
    if rec is None:
        ctx.recorder = Recorder(name)
    else:
        if isinstance(rec, Recorder):
            if rec.name == name:
                pass
            else:
                rec.teardown()
                ctx.recorder = Recorder(name)
        else:
            raise Exception('It is not a recorder')
    return ctx.recorder


class Recorder(object):
    def __init__(self, name=None):
        if name is None:
            name = ''.join(random.sample(string.hexdigits, 8))
        self.name = name
        self.file_path = os.path.join(
            self._get_storage_path(), self.name + '.json')

        self.name_count = None
        self.data = None
        self.group_cache = None
        self._insert = self._insert_one

        self.startup()

    def _get_storage_path(self):
        return os.path.join(config.RECORDER_PATH, self.name)

    def _get_incremental_name(self):
        if self.name_count is None:
            file_names = [
                int(name.split('.')[0])
                for name in os.listdir(self._get_storage_path())
                if name.split('.')[0].isdigit()
            ]
            if len(file_names) == 0:
                self.name_count = 0
            else:
                self.name_count = max(file_names)
        else:
            self.name_count += 1

        return str(self.name_count).rjust(8, '0')

    def _insert_one(self, key, val):
        self.data.append({key: val})

    def _insert_group(self, key, val):
        self.group_cache[key] = val

    def startup(self):
        if not os.path.exists(self._get_storage_path()):
            os.mkdir(self._get_storage_path())

        try:
            with open(self.file_path) as f:
                self.data = json.load(f)
        except IOError as e:
            if e.errno == 2:
                self.data = []
            else:
                raise e

    def teardown(self):
        f = open(self.file_path, 'w')
        json.dump(self.data, f)
        f.close()

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
        self.data.append(self.group_cache)
        self.group_cache = None
