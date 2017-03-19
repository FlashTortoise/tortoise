EYE_CAPTURE_ID = 0
EYE_SIGHT_HEIGHT = 640
EYE_SIGHT_WIDTH = 320

WHEELS_PINS_LF = (5, 13)
WHEELS_PINS_LB = (19, 26)
WHEELS_PINS_RF = (12, 16)
WHEELS_PINS_RB = (20, 21)

TORTOISE_WALK_PERIOD = 0.1

# fix it: it seems that only relative directory can by accessed by open
RECORDER_PATH = '.'

PERIPHERAL_SUPPORTED = {
    'eye': 'tortoise.sensors.Eye',
    'wheels': 'tortoise.effects.Wheels'
}
