import threading
from sys import argv

import let_tortoise_move as move
import recording

move_process = threading.Thread(target=move.working_loop)
move_process.daemon = True
move_process.start()

# eye_server_process = threading.Thread(
#     target=observe_with_tortoise_eye.tortoise_working_loop)
# eye_server_process.daemon = True
# eye_server_process.start()


if __name__ == '__main__':
    if len(argv) == 1:
        recording.record_working_loop()
    elif len(argv) == 2:
        recording.record_working_loop(argv[1])
    else:
        print '''Too many arguments\n
        Usage:
            python <path to this file> [name]'''
