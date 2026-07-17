#! /usr/bin/env python3

import json
import requests
import time
import traceback

exceptionpickler_server = 'http://localhost:4009/put'


def transmit_exception(e: Exception):
    try:
        details = { 
               'when': time.time(),
               'cause': e.__cause__,
               'args': e.args,
               'text': str(e),
               'line': e.__traceback__.tb_lineno,
               'traceback': [row.strip('\n') for row in traceback.format_exception(e)]
               }

        requests.post(url=exceptionpickler_server, json=json.dumps(details))

    except Exception as e:
        print(f'Failed transmitting exception to exceptionpickler server: {e} at {e.__traceback__.tb_lineno}')


if __name__ == '__main__':
    try:
        def test():
            1 / 0
        def some_caller():
            test()

        some_caller()
    except Exception as e:
        transmit_exception(e)
