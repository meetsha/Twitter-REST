import json
import twurl
import urllib
import sqlite3

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

conn = sqlite3.connect('spider.sqlite3')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS twitter
            (name TEXT, retrieved INTEGER, friends INTEGER)''')

while True:
    acct = raw_input('Enter twitter account, or quit:')
    if acct == 'quit' : break
    if len(acct)<1 :
        cur.execute('SELECT name FROM twitter WHERE retrieved = 0 LIMIT 1')
        try:
            acct = cur.fetchone()[0]
        except:
            print "No unretrieved accounts found."
            continue

    url = twurl.augment(TWITTER_URL,
            { 'screen_name':acct, 'count':'10'})
    connection = urllib.urlopen(url)
    data = connection.read()
    headers = connection.info().dict
    r = headers['x-rate-limit-remaining']
    if r<5 :  break
    print 'Remaining',r
    js = json.loads(data)
    print json.dumps(js)

    cur.execute('UPDATE twitter SET retrieved = 1 where name = ?',(acct,))
    
    countold = 0
    countnew = 0
    
    for u in js['users']:
        friend = u['screen_name']
        print friend
        cur.execute('SELECT friends FROM twitter WHERE name = ? LIMIT 1',(friend,))
        try:
            count = cur.fetchone()[0]
            cur.execute('UPDATE twitter SET friends = ? WHERE name = ?', (count+1, friend))
            countold += 1
        except:
            cur.execute('INSERT INTO twitter VALUES (?,0,1)', (friend,))
            countnew += 1
    
    print 'New account:',countnew,', Old Accounts:',countold
    conn.commit()

cur.close()



