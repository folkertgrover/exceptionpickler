## when / what

If you can't run docker or you're in the situation that you need to run your python exception-collector under windows, then this might be useful.


## requirements

* requests
* flask

e.g.:

```bash
pip install requests Flask
```


## how

On your server, run:

```bash
flask --app server run --port 4009 --host 0.0.0.0
```

In your code, add:

```python
import include_me
```

Then in each `try...except`, add:
```python
include_me.transmit_exception(e)
```
(assuming that you capture the exception into a variable called `e`).

Also make sure to change the `exceptionpickler_server` line in `include_me.py` to let it point to the exceptionpickler-server (see the flask invocation above).


Written by Folkert van Heusden for Grover Underdogs.
