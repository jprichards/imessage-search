#!/usr/bin/python

from SystemConfiguration import SCDynamicStoreCopyConsoleUser
import argparse
import sqlite3
import time
import sys

cfuser = SCDynamicStoreCopyConsoleUser(None, None, None)
defaultchatdb = '/Users/' + str(cfuser[0]) + '/Library/Messages/chat.db'


def main():
    ap = argparse.ArgumentParser(description='This tool searches iMessages \
                                 chat.db with a given search query and/or \
                                 contact number')
    ap.add_argument('-d', metavar='path', help='Set path to iMessage chat.db \
                    (Defaults to current console user chat.db)')
    ap.add_argument('-s', metavar='query', help='Search query')
    ap.add_argument('-c', metavar='number', help='Contact number')
    args = ap.parse_args()

    if len(sys.argv[1:]) == 0:
        ap.print_help()
        ap.exit()

    if args.d:
        message_conn = sqlite3.connect(args.d)
    else:
        message_conn = sqlite3.connect(defaultchatdb)

    m = message_conn.cursor()

    if args.c:
        m.execute('SELECT ROWID FROM handle WHERE id like \'%%%s%%\'' % args.c)
        handle = m.fetchall()
        ids = []
        for h in handle:
            ids.append(h[0])
        ids_query = '(' + ','.join((str(n) for n in ids)) + ')'

        if args.s:
            m.execute('SELECT * FROM message WHERE text like \'%%%s%%\' and \
                      handle_id in %s' % (args.s, ids_query))
            results = m.fetchall()
        else:
            m.execute('SELECT * FROM message WHERE handle_id in %s'
                      % ids_query)
            results = m.fetchall()
    else:
        if args.s:
            m.execute('SELECT * FROM message WHERE text like \'%%%s%%\''
                      % args.s)
            results = m.fetchall()
        else:
            print ap.print_help()
            sys.exit(1)

    print
    print 'ContactNum    Received/Sent   Date                 Result'
    print

    for r in results:
        message_time = time.strftime('%Y-%m-%d %H:%M:%S',     # add offset
                                     time.localtime(int(r[15])+977616000))
        message = r[2]
        handleid = r[5]

        if r[21] == 1:
            msgtype = 'sent          '
        elif r[21] == 0:
            msgtype = 'received      '

        if handleid == 0:
            pass
        else:
            m.execute('SELECT id FROM handle WHERE ROWID = %s' % handleid)
            contactnum = m.fetchone()
            print (contactnum[0] + '  ' + msgtype + '  ' + message_time +
                   '  ' + message)


if __name__ == '__main__':
    main()
