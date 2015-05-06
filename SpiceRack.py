'''
SpiceRack.py
Using some simply wrapped sqlite calls, a textual user interface to allow the 
user to maintain a virtual spice rack. The user may add, add to, remove or use
a spice from his/her rack by following simple prompts. 
'''

import sqlite3, sys, os

def addSpice(cur,name=None,amount=None):
    '''Adds some amount of spice 'name' after checking to make sure the spice
    does not already exist in the rack 
    '''
    spices, amounts = getSpices(cur)
    if name is None:
        name = raw_input('Enter the name of the spice you would like to add:\n')
        print('\n')
    check = [spice for spice in spices if name.lower() == spice.lower()]
    if check:
        while check:
            confirm = raw_input('%s already exists in your rack. Would you like to rename it to %s? (y/n/x)\n' % (check[0],name))
            print('\n')
            if confirm.lower() == 'y':
                rnSpice(c,check[0],name)
                return
            elif confirm.lower() == 'n':
                print('Only one spice of a certain kind may be added to your rack')
                return
            elif confirm.lower() == 'x':
                return
            else:
                print('Invalid Parameter')
    if amount is None:
        amount = input('Enter the amount(g) of %s you are adding:\n' % name)
        print('\n')
    cur.execute('INSERT INTO Spices VALUES(?,?)',(name,amount))

def rmSpice(cur,name=None):
    spices, amounts = getSpices(cur)
    if name is None:
        name = raw_input('Enter the name of the spice you would like to remove:\n')
        print('\n')
    while name not in spices:
        match = [spice for spice in spices if name.lower() == spice.lower()]
        if not match:
            print('%s is not in your spice rack\n' % name)
            lsSpice(cur)
            break
        else:
            confirm = raw_input('Did you mean %s? (y/n/x)\n' % match[0])
            print('\n')
            if confirm.lower() == 'y':
                name = match[0]
                pass
            elif confirm.lower() == 'n':
                print('%s is not in your spice rack' % name)
                lsSpice(cur)
                name = raw_input('Enter the name of the spice you would like to remove:\n')
                print('\n')
            elif confirm.lower() == 'x':
                break
            else:
                print('Invalid Parameter\n')
        continue
    cur.execute('DELETE FROM Spices WHERE Spice = "%s"'%name)

def rnSpice(cur,oname=None,nname=None):
    cur.execute('UPDATE Spices SET Spice = ? WHERE Spice = ?',
                (nname,oname))

def chSpice(cur,name=None,amount=0,mode=0):
    spices, amounts = getSpices(cur)
    flag = 0
    if name is None:
        name = raw_input('Enter the name of the spice:\n')
        print('\n')
    while name not in spices:
        check = [spice for spice in spices if name.lower() == spice.lower()]
        if not check:
            print ('%s is not in your spice rack.' % name)
            flag = 1
        while check:
            confirm = raw_input('Did you mean %s? (y/n/x)\n' % check[0])
            print('\n')
            if confirm.lower() == 'y':
                name = check[0]
                check = None
            elif confirm.lower() == 'n':
                check = None
            elif confirm.lower() == 'x':
                return
            else:
                print('Invalid Parameter')
        while flag:
            fix = raw_input('Would you like to add %s to your rack? (y/n/x)\n' % name)
            print('\n')
            if fix.lower() == 'y':
                addSpice(c,name)
                flag = 0
                break
            elif fix.lower() == 'n':
                flag = 2
                break
            elif fix.lower() == 'x':
                return
            else:
                print('Invalid Parameter')
    if flag < 2:
        if mode:
            amount = amounts[spices.index(name)]
            print(' {0:20} {1:4}g'.format(name,amount))
            amount -= input('Enter the amount(g) of %s you are using:\n' % name)
            print('\n')
        else:
            if not amount:
                spices, amounts = getSpices(cur)
                amount = amounts[spices.index(name)]
                amount += input('Enter the amount(g) of %s you are adding:\n' % name)
                print('\n')
        cur.execute('UPDATE Spices SET Amount = ? WHERE Spice = ?',(amount,name))

def lsSpice(cur):
    spices, amounts = getSpices(cur)
    print(' {0:20} {1:4}'.format('Spice','Amount'))
    print('-'*30)
    for spice,amount in zip(spices,amounts):
        print ' {0:20} {1:4}g'.format(spice,amount)
    print('\n')

def getSpices(cur):
    cur.execute('SELECT * FROM Spices')
    db_spices = cur.fetchall()
    if db_spices:
        spices, amounts = zip(*db_spices)
    else:
        spices, amounts = [], []
    return spices, amounts
    
    

inprompt = ''.join(('\nChoose an action:\n',
'1: Add a spice to the rack\n',
'2: Add to an existing spice\n',
'3: Remove a spice from the rack\n',
'4: Use a spice from the rack\n',
'5: List all spices currently in rack\n',
'x: Exit program\n'))

if not 'SpiceRack.db' in os.listdir(os.getcwd()):
    with open('SpiceRack.db','w+') as newfile:
        pass

try:
    with sqlite3.connect('SpiceRack.db',isolation_level=None) as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS Spices (Spice TEXT,Amount FLOAT)')
        try:
            while True:
                choice = raw_input(inprompt)
                print('\n')
                try:
                    choiceint = int(choice)
                    if choiceint == 1:
                        addSpice(c)

                    if choiceint == 2:
                        chSpice(c)
                            
                    if choiceint == 3:
                        rmSpice(c)
                        
                    if choiceint == 4:
                        chSpice(c,mode = 1)
                        
                    if choiceint == 5:
                        lsSpice(c)
                        
                    if not isinstance(choiceint,int) or not 0 < choiceint < 6:
                        print('Invalid Parameter\n')
                        continue
                except ValueError:
                    if choice.lower() == 'x':
                        break
                    else:
                        print('Invalid Parameter\n')
                        continue
                    
        except KeyboardInterrupt:
            pass

except sqlite3.Error, e:
    print('Error %s:' % e.args[0])
    sys.exit(1)

finally:
    if conn:
        conn.close()