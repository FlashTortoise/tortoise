from unittest import TestCase

import cv2

from tortoise.effectors import Wheels
from tortoise.sensors import Eye


class TestWheelsHardware(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w = Wheels()

    def test_mq(self):
        self._motor_test(self.w.mq, 'q')

    def test_ma(self):
        self._motor_test(self.w.ma, 'a')

    def test_mw(self):
        self._motor_test(self.w.mw, 'w')

    def test_ms(self):
        self._motor_test(self.w.ms, 's')

    def _motor_test(self, motor, motor_name):
        hint = 'Motor {} {} is okay [y]/n'
        motor.value = 0.5
        if raw_input(hint.format(motor_name, 'forward')) in ['', 'y']:
            pass
        else:
            self.fail()

        motor.value = -0.5
        if raw_input(hint.format(motor_name, 'backward')) in ['', 'y']:
            pass
        else:
            self.fail()

        motor.value = 0


class TestEyeHardware(TestCase):
    def test_see(self):
        e = Eye()
        e._cap.set(3, 320)
        e._cap.set(4, 240)
        cv2.imshow('Test eye', e.see())
        if cv2.waitKey(0) & 0xFF == 27:
            self.fail()
        else:
            pass
