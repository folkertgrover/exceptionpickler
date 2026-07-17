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

First change the line with `db_file` in it in `server.py` to include the path to where the server application should store its database.

Then, to install as a windows service:
```bash
python server.py --startup auto install
sc start ExceptionPickler
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


## results

You can see the collected tracebacks by pointing your web-browser to http://ip-adres-of-server:4009/


Written by Folkert van Heusden for Grover Underdogs.
