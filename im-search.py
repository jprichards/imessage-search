#!/usr/bin/python

from SystemConfiguration import SCDynamicStoreCopyConsoleUser
import argparse
import sqlite3
import time

cfuser = SCDynamicStoreCopyConsoleUser(None, None, None)
defaultchatdb = '/Users/' + str(cfuser[0]) + '/Library/Messages/chat.db'


def main():
    ap = argparse.ArgumentParser(description='This tool searches iMessages')
    ap.add_argument('-d', help='Specify path to iMessage chat.db')
    ap.add_argument('-s', help='Search query')
    ap.add_argument('-c', help='Contact number')
    args = ap.parse_args()

    if args.d:
        message_conn = sqlite3.connect(args.d)
    else:
        message_conn = sqlite3.connect(defaultchatdb)
    m = message_conn.cursor()

    if not args.c:
        m.execute('SELECT * FROM message WHERE text like \'%%%s%%\'' % args.s)
        results = m.fetchall()
    elif args.c:
        m.execute('SELECT ROWID FROM handle WHERE id like \'%%%s%%\'' % args.c)
        handle = m.fetchall()
        ids = []
        for h in handle:
            ids.append(h[0])
        ids_query = '(' + ','.join((str(n) for n in ids)) + ')'
        m.execute('SELECT * FROM message WHERE text like \'%%%s%%\' and \
                  handle_id in %s' % (args.s, ids_query))
        results = m.fetchall()

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
