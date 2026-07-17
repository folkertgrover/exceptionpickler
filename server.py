#! /usr/bin/env python3

from flask import Flask, request
import json
import servicemanager
import socket
import sqlite3
import time
import win32serviceutil
import win32service
import win32event


db_file = 'data.db'

def create_db(file):
    try:
        con = sqlite3.connect(file)
        cur = con.cursor()
        cur.execute('PRAGMA journal_mode=wal')
        cur.execute('CREATE TABLE exceptions(id INTEGER PRIMARY KEY, `when` DOUBLE, details TEXT)')
        cur.execute("CREATE INDEX idx_text ON exceptions (json_extract(details, '$.text'))")
        cur.execute("CREATE INDEX idx_line ON exceptions (json_extract(details, '$.line'))")
        cur.execute("CREATE INDEX idx_traceback ON exceptions (json_extract(details, '$.traceback'))")
        cur.close()
        con.commit()
        con.close()
    except Exception as e:
        pass


app = Flask(__name__)

@app.route('/put', methods=['POST'])
def put():
    j = json.loads(request.json)

    when = j['when']
    del j['when']

    con = sqlite3.connect(db_file)
    cur = con.cursor()
    cur.execute('INSERT INTO exceptions(`when`, details) VALUES(?, ?)', (when, json.dumps(j)))
    cur.close()
    con.commit()
    con.close()

    return 'OK'

@app.route('/', methods=['GET'])
def index():
    rc = '<HTML>'
    rc += '<head><link rel="stylesheet" href="/stylesheet.css"></head>'
    rc += '<BODY>'
    rc += '<TABLE border="1">'
    rc += '<tr><th>latest</th><th># occurences</th><th>what</th><th>where</th></tr>'
    con = sqlite3.connect(db_file)
    cur = con.cursor()  # FIXME dict cursor
    cur.execute('SELECT MAX(`when`), details, COUNT(*) AS n_occurences, id FROM exceptions GROUP BY details ORDER BY `when` DESC')
    for row in cur:
        j = json.loads(row[1])
        where = j['traceback'][-2]
        rc += f'<tr><td><a href="/details?id={row[3]}">{time.ctime(row[0])}</a></td><td>{row[2]}</td><td>{j["text"]}</td><td>{where}</td></tr>'
    cur.close()
    con.close()

    rc += '</TABLE>'
    rc += '</BODY>'
    rc += '</HTML>'

    return rc


@app.route('/details', methods=['GET'])
def details():
    id_ = request.args.get('id')

    rc = '<HTML>'
    rc += '<head><link rel="stylesheet" href="/stylesheet.css"></head>'
    rc += '<BODY>'
    con = sqlite3.connect(db_file)
    cur = con.cursor()  # FIXME dict cursor
    cur.execute('SELECT details FROM exceptions WHERE id=?', (id_,))
    row = cur.fetchone()
    j = json.loads(row[0])
    rc += f'<pre>{"\n".join(j["traceback"])}</pre>'
    cur.close()
    con.close()
    rc += '</BODY>'
    rc += '</HTML>'

    return rc


@app.route('/stylesheet.css', methods=['GET'])
def stylesheet_css():
    return '''
/* Color palette */
:root {
          --tbl-bg: #05060a;          /* deep black */
            --tbl-bg-alt: #0b0f18;      /* slightly lighter black */
              --tbl-border: #1c2433;      /* subtle dark border */
                --tbl-text: #ffffff;        /* white */
                  --tbl-muted: #a9b3c5;       /* soft gray */
                    --tbl-blue: #1e90ff;        /* bright blue */
                      --tbl-blue-soft: #3a6fd8;   /* softer blue */
                      }

/* Table container */
table {
          width: 100%;
            border-collapse: collapse;
              background: var(--tbl-bg);
                color: var(--tbl-text);
                  border: 1px solid var(--tbl-border);
                    border-radius: 10px;
                      overflow: hidden;
                        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.6);
                        }

/* Header */
thead th {
          background: linear-gradient(135deg, #0b0f18, #05060a);
                                        padding: 0.9rem;
                                        text-align: left;
                                        font-weight: 600;
                                        color: var(--tbl-blue);
                                        border-bottom: 1px solid var(--tbl-border);
                                        letter-spacing: 0.03em;
                                      }

          /* Body cells */
          tbody td {
                padding: 0.75rem;
                  border-bottom: 1px solid var(--tbl-border);
                    color: var(--tbl-muted);
                    }

          /* Alternating rows */
          tbody tr:nth-child(even) {
                background: var(--tbl-bg-alt);
                }

          /* Hover effect */
          tbody tr:hover {
                background: rgba(30, 144, 255, 0.08);
                  transition: background 0.2s ease;
                  }

          /* Highlighted / active row */
          tbody tr.active {
                background: rgba(30, 144, 255, 0.18);
                  color: var(--tbl-text);
                  }

          /* Borders for compact tables */
          table.compact td,
          table.compact th {
                padding: 0.5rem;
                }

          /* Optional: blue focus outline for clickable rows */
          tbody tr.clickable:hover {
                cursor: pointer;
                  box-shadow: inset 0 0 0 1px var(--tbl-blue-soft);
                  }
          /* Color palette */
          :root {
                --tbl-bg: #05060a;          /* deep black */
                  --tbl-bg-alt: #0b0f18;      /* slightly lighter black */
                    --tbl-border: #1c2433;      /* subtle dark border */
                      --tbl-text: #ffffff;        /* white */
                        --tbl-muted: #a9b3c5;       /* soft gray */
                          --tbl-blue: #1e90ff;        /* bright blue */
                            --tbl-blue-soft: #3a6fd8;   /* softer blue */
                            }

          /* Table container */
          table {
                    width: 100%;
                      border-collapse: collapse;
                        background: var(--tbl-bg);
                          color: var(--tbl-text);
                            border: 1px solid var(--tbl-border);
                              border-radius: 10px;
                                overflow: hidden;
                                  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.6);
                                  }

          /* Header */
          thead th {
                    background: linear-gradient(135deg, #0b0f18, #05060a);
                                                  padding: 0.9rem;
                                                  text-align: left;
                                                  font-weight: 600;
                                                  color: var(--tbl-blue);
                                                  border-bottom: 1px solid var(--tbl-border);
                                                  letter-spacing: 0.03em;
                                                }

                    /* Body cells */
                    tbody td {
                          padding: 0.75rem;
                            border-bottom: 1px solid var(--tbl-border);
                              color: var(--tbl-muted);
                              }

                    /* Alternating rows */
                    tbody tr:nth-child(even) {
                          background: var(--tbl-bg-alt);
                          }

                    /* Hover effect */
                    tbody tr:hover {
                          background: rgba(30, 144, 255, 0.08);
                            transition: background 0.2s ease;
                            }

                    /* Highlighted / active row */
                    tbody tr.active {
                          background: rgba(30, 144, 255, 0.18);
                            color: var(--tbl-text);
                            }

                    /* Borders for compact tables */
                    table.compact td,
                    table.compact th {
                          padding: 0.5rem;
                          }

                    /* Optional: blue focus outline for clickable rows */
                    tbody tr.clickable:hover {
                          cursor: pointer;
                            box-shadow: inset 0 0 0 1px var(--tbl-blue-soft);
                            }
'''


class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "ExceptionPickler"
    _svc_display_name_ = "Python exception collector"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                          servicemanager.PYS_SERVICE_STARTED,
                          (self._svc_name_,''))
        self.main()

    def main(self):
        create_db(db_file)

        app.run(host='0.0.0.0', port=4009)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)
