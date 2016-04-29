## Reads a csv file into a dict, checking to see that the required columns are 
## present and returning a dictionary of only those.
#def readcsv(fpath, cols):
#     # Read as dictionary.
#    skipLines = 0
#    d = csv2dictlists(fpath, skipLines)    
#    
#    # Set all keys lower case for testing
#    d = dict((k.lower(), v) for k,v in d.iteritems())
#    
#    outdict = {}
#    try:
#        for col in cols:
#            # If this throws an error then required column not present.
#            outdict[col] = d[col]
#    except:
#        error(fpath + ' does not have the required columns: '+' '.join(cols))
#    return outdict


## Read a CSV file to a list of lists (lol).
#def csv2lists(fpath, skipLines):
#    import csv    
#    reader = csv.reader(open(fpath,'Ur'))
#    # Skip the header lines
#    for _ in range(skipLines):
#        reader.next()
#
#    first = True
#    for row in reader:
#        if first:
#            # Set up empty lists
#            lol = [[] for _ in range(len(row))]
#            first = False
#            
#        # Go across rows and append each list with new data. Empty cells are
#        # returned as empty strings.        
#        for i,field in enumerate(row):
#            lol[i].append(field)
#            
#    return lol


## Return members as lists
#def readMembers(fpath):
#             
#    l = getCleanHeader(fpath).lower().split(',')
#    errFlag = False
#    
#    cols = ['last name', 'first name', 'email', 'groups']
#    try:
#        # Get indices of columns we need. If 'col' is not in the list then this 
#        # throws an error and the columns we need are not in the csv file. 
#        colsd = {}
#        for col in cols:
#            colsd[col] = l.index(col)   
#        
#        # Read the members csv as a list of lists
#        skipLines = 1
#        lol = csv2lists(fpath, skipLines)
#        
#        # Output lol
#        outlol = [[] for _ in range(len(cols))]
#        
#        # Process the lol to fill only the columns we need.
#        for i,col in enumerate(cols):
#            outlol[i].append(lol[colsd[col]])   
#                              
#    except:
#        errFlag = True    
#        
#    if errFlag:
#        error(fpath + ' is not in correct format.')
#
#    return (outlol, cols)


## Returns the first line of a file, minus the newlines and whitespace
#def getCleanHeader(fpath):
#    f = open(fpath,'Ur') # open in universal newline mode
#    s = f.readline().rstrip()
#    f.close()
#    "".join(s.split())
#    return s