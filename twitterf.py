import urllib
import twurl
import json
import sqlite3

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

conn = sqlite3.connect('tspider.sqlite3')
cur = conn.cursor()

cur.executescript('''
    CREATE TABLE IF NOT EXISTS People(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE, retrieved INTEGER );
    
    CREATE TABLE IF NOT EXISTS Follows(
        from_id INTEGER,
        to_id INTEGER,
        UNIQUE (from_id, to_id))''')

while True:
    acct = raw_input('Enter a twitter account, or quit:')
    if acct == 'quit' : break
    if len(acct) < 1 :
        cur.execute('SELECT id,name FROM People WHERE retrieved = 0 LIMIT 1')
        try:
            (id,acct) = cur.fetchone()
        except:
            print "No more accounts to retrieve."
            continue
    else:
        cur.execute('SELECT id FROM People WHERE name = ? LIMIT 1',(acct,))
        try:
            id = cur.fetchone()[0]
        except:
            cur.execute('INSERT INTO People (name,retrieved) VALUES (?,0)',(acct,))
            conn.commit()
            if cur.rowcount!=1:
                print 'Error inserting account:',acct
                continue
            id = cur.lastrowid

    url = twurl.augment(TWITTER_URL,
            {'screen_name':acct, 'count':'20'})
    print 'Retrieving url', url
    connection = urllib.urlopen(url)
    data = connection.read()
    headers = connection.info().dict
    h = headers['x-rate-limit-remaining']
    print 'Remaining calls:',h
    if h<5 : break

    js = json.loads(data)
    #print json.dumps(js, indent = 4)
    cur.execute('UPDATE People SET retrieved = 1 WHERE name = ? LIMIT 1',(acct,))

    count_old = 0
    count_new = 0
    for u in js['users']:
        friend = u['screen_name']
        print friend
        cur.execute('SELECT id FROM People WHERE name = ? LIMIT 1',(friend,))
        try:
            friend_id = cur.fetchone()[0]
            count_old += 1
        except:
            cur.execute('''INSERT INTO People(name,retrieved) VALUES(?,0)''',
                          (friend,))
            conn.commit()
            if cur.rowcount!=1:
                print 'Error inserting account:',friend
                continue
            friend_id = cur.lastrowid
            count_new += 1
        cur.execute('INSERT OR IGNORE INTO Follows VALUES(?,?)',(id,friend_id))
    
    print 'New accounts:',count_new,' Old accounts:',count_old
    conn.commit()

cur.close()  
        
    
           
