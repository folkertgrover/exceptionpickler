import sys
import threading


exceptionpickler_server = 'http://localhost:4009/put'


def excepthook(exc_type, exc_value, exc_tb):
    try:
        import json
        import requests
        import time
        import traceback

        details = {
               'when': time.time(),
               'cause': exc_value.__cause__,
               'args': exc_value.args,
               'text': str(exc_value),
               'line': exc_value.__traceback__.tb_lineno,
               'traceback': [row.strip('\n') for row in traceback.format_exception(exc_value)]
               }

        requests.post(url=exceptionpickler_server, json=json.dumps(details))

    except Exception as e:
        print(f'Failed transmitting exception to exceptionpickler server: {e} at {e.__traceback__.tb_lineno}')

    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = excepthook
threading.excepthook = excepthook
