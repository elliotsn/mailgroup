#!/usr/bin/env python
#
# mailgroup.py -- Program to produce a string that can be pasted into a mail client. 
#                 The string is a list of email addresses that is constructed from 
#                 databases of .csv files.
#
def usage():
    print """
    ******************
    *  mailgroup.py  *
    ******************

    SUMMARY            
                        
    Program to produce a string that can be pasted into a mail client. The 
    string is a list of email addresses that is constructed from 2 linked csv 
    files: a database of email addresses, and a database of group names.
    
    USAGE
    
    mailgroup EMAIL_LIST GROUP_LIST [GROUPS]
    
    EMAIL_LIST is the path to a csv file containing the database of email
            addresses. The file must contain the colums (with a header row):
                    'Last name', 'First name', 'Email', 'Groups'
            Additional columns may be present (e.g. Position, Notes) but will
            not be used.
    
    GROUP_LIST is the path to a csv file containing the database of email 
            groups. The file must contain the columns (with a header row):
                'Group', 'Key'        
    
    [GROUPS]   is a logical expression built using the logical operators & | ~ 
            and parentheses (), as well as group names that exist in 
            the GROUP_LIST file. Note that if the expression contains operators
            that are interpreted by the shell then the expression should be 
            enclosed in quotes (e.g. 'GROUP1&GROUP2' ).
            
    If no arguments or the wrong number of arguments are passed then this 
    message is returned.

    When EMAIL_LIST and GROUP_LIST are defined a string is returned to stdout 
    that summarizes the number of names and groups in the database.
    
    When [GROUPS] is defined the output returned to stdout is a list of email 
    addresses of members belonging to the groups listed in [GROUPS].
    
    Example command and output:
        $  mailgroup members.csv groups.csv (project1&project2)|management
        $  John Doe <j.doe@theinter.net>, Jane Q. Doe <jane.doe@theother.net>, 
        $  James Manager <jims.your@boss.com>
    
    Note that commas are removed from member names stored in EMAIL_LIST, because
    these are interpreted as field separators by most email clients and 
    interfaces.

    If you want to always use mailgroup with the same database, you can use an
    alias, then for a summary you just need enter mailgroup, or for a mailing
    list you only need provide the group expression.

    E.g. in ~/.bashrc:
      alias mailgroup='/usr/bin/mailgroup.py path2MyIndex.csv path2MyGroups.csv'


    Author: Elliot Sefton-Nash (e.sefton-nash@uclmail.net)
             
          """

def error(msg):
    import sys    
    print >> sys.stderr, 'mailgroup: ERROR // '+msg
    sys.exit()

# Reads a csv file and returns one list per column.
def csvgroup2dic(fpath):
    import csv
    
    with open(fpath, mode='r') as f:
        reader = csv.reader(f)
        groups = {rows[0]:rows[1] for rows in reader}

    return groups
    

# Read a 2 column CSV as a dictionary where keys in the first column and values 
# in the second. If there is a header it can be ignored.
def csv2dict(fpath, skipLines):
    import csv
    reader = csv.reader(open(fpath,'Ur'))
    d = {}
    # Skip the header lines
    for _ in range(skipLines):
        reader.next()
    for row in reader:
        key = row[0]
        if key in d:
            # If there is a duplicate key in the dictionary, do not overwrite.
            pass
        else:
            d[key] = row[1:]
    return d


# Read a CSV as a dictionary where headers are the keys and lists are returned 
# as the values. Note that within fields, strings are split by the value passed 
# in fieldDelim. Empty fields are returned as empty lists.
def csv2dictlists(fpath, fieldDelim, skipLines):
    import csv
    reader = csv.DictReader(open(fpath, 'Ur'))
    # Skip the header lines, but the next will be the column headings.
    for _ in range(skipLines):
        reader.next()
    d = {}
    for row in reader:
        for column, value in row.iteritems():
            # Get list of items. First split by delimieter then remove 
            # whitespace.
            v = [x.strip(' ') for x in value.split(fieldDelim)]
            # Append an empty list when all items in the field are empty 
            # strings. This allows us to for loop over items without any convern
            # for considering empty items, because no loops 
            # are executed when the list is empty.
            goFlag=False
            for iv in v:
                if iv: # Non-empty strings evaluate to true,
                    goFlag=True
                    break
                    
            if not goFlag:
                v = []
            
            d.setdefault(column, []).append(v)
    return d    


# Return members as lists
def readMembers(fpath):
             
    # Read index as dictionary.
    skipLines = 0
    fieldDelim = ',' # Commas separate items in fields.
    d = csv2dictlists(fpath, fieldDelim, skipLines)    
    
    # Set all keys lower case for testing
    d = dict((k.lower(), v) for k,v in d.iteritems())
    
    cols = ['last name', 'first name', 'email', 'groups']
    
    newd = {}
    try:
        for col in cols:
            # If this throws an error then required column not present.
            newd[col] = d[col]
    except:
        error(fpath + ' does not have the required columns: '+' '.join(cols))

    return newd

        
# Returns the first line of a file, minus the newlines and whitespace
def getCleanHeader(fpath):
    f = open(fpath,'Ur') # open in universal newline mode
    s = f.readline().rstrip()
    f.close()
    "".join(s.split())
    return s
    

# Return group name/key and descriptions as a dict
def readGroups(fpath):
    
    l = getCleanHeader(fpath).lower().split(',')
    errFlag = False
    groupDict = {}
    try:
        if (len(l) == 2) & l.__contains__('key') & l.__contains__('description'):
            # Read the group file as a dictionary
            skipLines = 1
            groupDict = csv2dict(fpath, skipLines)
            
            # Add the index of the group
            for i, g in enumerate(groupDict):
                groupDict[g].append(i)
            
        else:
            errFlag = True                
    except:
        errFlag = True
    
    if errFlag:
        error(fpath + ' is not in correct format.')
        
    return groupDict
    

# Build boolean arrays for each group, as long as the number of people.
def dbbuild(index, nindex, groups, ngroups):
    
    import numpy as np
    
    # One extra column for the total
    db = np.zeros((nindex, ngroups), dtype=bool)

    # For each person, add thier groups to the index. This is always in order 
    # because even though dicts are unordered, the lists in each value stay in 
    # the same order.
    for im, glist in enumerate(index['groups']):            
        #For each group this person is in.
        for g in glist:
            # Index of group is the last list element in the groups dict value
            db[ im, groups[g][-1] ] = True
            
    return db

                
# Check database contents, report on contents if desired and report any errors.
def dbcheck(index, groups, reportFlag):
    
    import numpy as np
    from sys import stdout
    
    # Assumed innocent until proven guilty, only set to false when there is 
    # something that stops the program producing useful output.
    goFlag = True
    db = False
    
    # Find unique groups.
    uniques = []
    for x in index['groups']:
        # This is not even looped once if groups is empty, i.e. person is in no 
        # groups.
        for group in x:
            if not uniques.__contains__(group):
                uniques.append(group)    
    
    # All lists should be the same length, why not choose email
    nindex = len(index['email'])
    # Note that this is defined with the groups file, there could be many more 
    # groups defined than people are members of. A smarter way would be to have
    # db only be the size of the unique groups present, but link the column 
    # headings of db to the group dict.
    ngroups = len(groups)
    
    # Make sure that all groups present are represented in the groups file, 
    # error if not.
    for u in uniques:
        if not groups.has_key(u):
            goFlag = False
            error(fpathgroups+' does not contain the group refered to: '+u)
    
    if goFlag:
        db = dbbuild(index, nindex, groups, ngroups)
        
        if reportFlag:
            # Number of groups and members in each group
            outstr="""\nDATABASE SUMMARY
            
    Index file:  """+fpathindex+"""
    Group file:  """+fpathgroups+"""
            
    """+str(nindex)+' people and '+str(ngroups)+' groups found.\n\n'
            
            # Report sum of people in each group             
            outstr += '    GROUP\t\tMEMBERS\n'
            for g in groups:
                outstr += '    ' + g + \
                '\t\t' + str(np.sum(db[ :, groups[g][-1]]))+'\n'
        
            ## Check for people with no group
            noGroupFlag = False
            for i,g in enumerate(index['groups']):
                if g == []:
                    if not noGroupFlag:
                        noGroupFlag = True
                        outstr += """
    WARNING: The following people are assigned to no group:\n"""
                    
                    outstr +='    '+ ' '.join(
                    [index['first name'][i][0], index['last name'][i][0]])+'\n'

            ## Check for groups with no people
            noMemberWarnFlag = False
            for g in groups.keys():
                # Search for this group in the index
                noMembers = True
                for ig in index['groups']:
                    if ig.__contains__(g):
                        noMembers = False
                        break
                if noMembers:
                    if not noMemberWarnFlag:
                        noMemberWarnFlag = True
                        outstr += """
    WARNING: The following groups have no assigned people:\n"""
                    outstr +='    '+g+'\n'                                 

            outstr+='\n'
            stdout.write(outstr)
    return db


# For a list, returns either first element or empty string if list is empty.
def listFirstOrEmptyStr(inList):
    if inList:
        return inList[0]
    else:
        return ''


# Query the database and return an ascii stream to stdout that can be pasted
# into an email client.
def dbquery(index, groups, db, inexpr):
   
    import re
    from sys import stdout, stderr
       
    # Replace instances of group names with vectors from the db in arg.
    outexpr = inexpr
    for g in groups.keys():
        
        # Use re, substitute - with word boundary awareness
        outexpr = re.sub(r"\b%s\b" % g , "db[:, groups['"+g+"'][-1]]", outexpr)
        
        # This doesn't work when group names contain shorter group names.
        # outexpr = outexpr.replace(g, "db[:, groups['"+g+"'][-1]]")
        
    # If it doesn't evaluate then the syntax is wrong or the group doesn't exist.
    try:
        exec('thisSet='+outexpr)
    except:
        error('Logical expression invalid. Check that specified group(s) exist: '+inexpr)
    
    # Build output string using boolean vector.
    outstr = ''
    nindex = len(index['email'])
    if any(thisSet):
        for i in range(nindex):

            # Only add to the email string if the email address is present
            if thisSet[i] & (len(index['email'][i]) > 0):
                # Because fields are in lists, we must address the first element
                # But this would produce an error when the list is empty
                # So if the list is empty, substitute it for an empty string.
                # Note that strip() is present to remove unecessary whitespace
                # added by join when both first name and last name are empty.
                outstr += \
                ' '.join( [listFirstOrEmptyStr(index['first name'][i]),\
                           listFirstOrEmptyStr(index['last name'][i]) ]).strip()+\
                ' <'+index['email'][i][0]+'>, '
        # For last one, remove ', '
        outstr=outstr[:-2]+'\n'

        stdout.write(outstr)
    else:
        stderr.write('No members found in the specified set.\n')
    
# Main function - handle cmdline args and call appropriate functions.
if __name__ == '__main__':

    from sys import argv

    # the program name is always the first argument at sys.argv[0].
    argv = argv[1:]

    # Parse the arguments.  
    s=len(argv)
    # If there are too few or too many arguments then display the usage.
    if (s < 2) | (s > 4):
        usage()
    else:
        
        # If we are here user either desires to summarise db contents or make
        # a query. Attempt to load:
        fpathindex = argv[0]
        fpathgroups = argv[1]
    
        index = readMembers(fpathindex)   
        groups = readGroups(fpathgroups) 
        
        # Set flag to summarize contents
        reportFlag = False
        if s == 2:
            reportFlag = True
                  
        db = dbcheck(index, groups, reportFlag)

        if (s == 3) & (db != []):
            # Read the database and return the desired mailing list.
            dbquery(index, groups, db, argv[2])
