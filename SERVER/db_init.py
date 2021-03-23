# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 14:27:27 2020
@author: Max Renaudon
"""

import sqlite3

con = sqlite3.connect('chat_user_storage.db')
cur = con.cursor()
cur.executescript("""
    create table logins(
        name,
        password
    );
    insert into logins(name, password)
    values ('max', '1234');
    
    insert into logins(name, password)
    values ('thomas', 'pass');
    
    insert into logins(name, password)
    values ('amel', 'super');
    
    insert into logins(name, password)
    values ('Michel', 'okay');
    
    insert into logins(name, password)
    values ('Philippe', 'professeur');
    
    insert into logins(name, password)
    values ('zizou', '1998');
    
    """)

con.commit()
con.close()