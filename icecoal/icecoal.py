""" Light weight SQL database
Usage::
    >>> from icecoal import icecoal
    >>> result=icecoal.query("select name from input.csv,heads.csv where native='usa'")
"""

from .utilfuns import __dropdb, __mkdb, __mktable, __select, __droptable, __truntable, __insertrow, __update, __delete
from .expression import par
from .expression import create_exp_tree
from .const import *

def execute_query(q):
    q+="#"
    state='0'
    temp=""
    templist=[]
    
    exp=''
    etree=None
    required_fields=[]
    csvfile,headfile='',''
    keyword=''
    keys=[]
    values=[]
    
    #For each character in a query
    end= False
    found=False
    i=0
    while i < len(q):
        #for every rule in rule table
        passthis=False
        if not end:
            for j in range(0,len(rule)):
                #if state is equal to current state and it allows current char
                if (rule[j][0]==state) and ((rule[j][1]=='any') or(q[i] in rule[j][1])):
                    #Execute required and stop rule search
                    found=True
                    state=rule[j][2]
                    if rule[j][3]=="pass":
                        passthis=True
                    elif rule[j][3]=='listpush':
                        templist.append(temp)
                        temp=''
                    elif rule[j][3]!='': #push #valuepush
                        temp+=q[i]
                        
                    if rule[j][4]=="req": #clean
                        required_fields.append(temp)
                        temp=''
                    elif rule[j][4]=="csv":
                        csvfile=temp
                        temp=''
                    elif rule[j][4]=="csv_select":
                        if csvfile=='' and temp!='':
                            csvfile=temp
                        keyword='select'
                        temp=''
                    elif rule[j][4]=="head":
                        if headfile=='' and temp!='':
                            headfile=temp
                        temp=''
                    elif rule[j][4]=="head_select":
                        headfile=temp
                        temp=''
                        keyword='select'
                    elif rule[j][4]=="exp_select":
                        exp=temp
                        temp=''
                        #Apply BODMAS Rule with proper paranthesis
                        exp=par(exp)
                        #Create tree
                        etree=create_exp_tree(exp)
                        keyword='select'
                    elif rule[j][4]=="delete":
                        exp=temp
                        temp=''
                        #Apply BODMAS Rule with proper paranthesis
                        exp=par(exp)
                        #Create tree
                        etree=create_exp_tree(exp)
                        keyword='delete'
                    elif rule[j][4]=="mkdb":
                        dbname=temp
                        keyword='mkdb'
                        temp=''
                    elif rule[j][4]=="drdb":
                        dbname=temp
                        keyword='drdb'
                        temp=''
                    elif rule[j][4]=="tablename":
                        tablename=temp
                        temp=''
                    elif rule[j][4]=="header":
                        header=temp
                        temp=''
                    elif rule[j][4]=="row":
                        templist.append(temp)
                        row=templist
                        temp=''
                        templist=[]
                    elif rule[j][4]=="mktable":
                        keyword="mktable"
                    elif rule[j][4]=="drtb":
                        tablename=temp
                        keyword='drtb'
                        temp=''
                    elif rule[j][4]=="trtb":
                        tablename=temp
                        keyword='trtb'
                        temp=''
                    elif rule[j][4]=="insert":
                        keyword='insert'
                        temp=''
                    elif rule[j][4]=="key":
                        keys.append(temp)
                        temp=''
                    elif rule[j][4]=="value":
                        values.append(temp)
                        temp=''
                    elif rule[j][4]=="exp_update":
                        exp=temp
                        temp=''
                        #Apply BODMAS Rule with proper paranthesis
                        exp=par(exp)
                        #Create tree
                        etree=create_exp_tree(exp)
                        keyword='update'
                    elif rule[j][4]=="updateall":
                        if temp!='':
                            values.append(temp)
                        keyword='update'
                        temp=''
                    if state=='end':
                        end=True
                    break
            if not found:
                raise sqlerror(-2,"Unexpected character "+q[i]+" at position "+str(i+1))
            else:
                found=False
        if passthis==True:
            pass
        else:
            i+=1
    # Execute the corresponding function inferred from the query
    if keyword=='select':
        rt=__select(required_fields,csvfile,headfile,etree)
        if rt==-1:
            return [-20,'Table does not exist',[]]
        elif rt==-2:
            return [-21,'Not a table name',[]]
        elif rt==-3:
            return [-22,'Header file does not exist',[]]
        elif rt==-4:
            return [-23,'Provided header is not a file',[]]
        else:
            return rt
    elif keyword=='mkdb':
        if __mkdb(dbname)==0:
            return [0,'Success',[]]
        else:
            return [-15,'Database already exists',[]]
    elif keyword=='mktable':
        rt=__mktable(tablename,header)
        if rt==0:
            return [0,'Success',[]]
        elif rt==-1:
            return [-16,'Table already exists',[]]
        elif rt==-2:
            return [-17,'Database does not exist',[]]
        elif rt==-3:
            return [-18,'Database name is blank',[]]
    elif keyword=='drdb':
        rt=__dropdb(dbname)
        if rt==0:
            return [0,'Success',[]]
        elif rt==-1:
            return [-17,'Database does not exist',[]]
        elif rt==-2:
            return [-19,'Not a database name',[]]
    elif keyword=='drtb':
        rt=__droptable(tablename)
        if rt==0:
            return [0,'Success',[]]
        elif rt==-1:
            return [-20,'Table does not exist',[]]
        elif rt==-2:
            return [-21,'Not a table name',[]]
    elif keyword=='trtb':
        rt=__truntable(tablename)
        if rt==0:
            return [0,'Success',[]]
        elif rt==-1:
            return [-20,'Table does not exist',[]]
        elif rt==-2:
            return [-21,'Not a table name',[]]
    elif keyword=='insert':
        rt=__insertrow(tablename,row)
        if rt==0:
            return [0,'Success',[]]
        elif rt==-1:
            return [-20,'Table does not exist',[]]
        elif rt==-2:
            return [-21,'Not a table name',[]]
        elif rt==-3:
            return [-24,'Values count does not match table fields count',[]]
    elif keyword=='update':
        rt=__update(keys,values,csvfile,headfile,etree)
        if rt==-1:
            return [-20,'Table does not exist',[]]
        elif rt==-2:
            return [-21,'Not a table name',[]]
        elif rt==-3:
            return [-22,'Header file does not exist',[]]
        elif rt==-4:
            return [-23,'Provided header is not a file',[]]
        else:
            return rt
    elif keyword=='delete':
        rt=__delete(csvfile,headfile,etree)
        if rt==-1:
            return [-20,'Table does not exist',[]]
        elif rt==-2:
            return [-21,'Not a table name',[]]
        elif rt==-3:
            return [-22,'Header file does not exist',[]]
        elif rt==-4:
            return [-23,'Provided header is not a file',[]]
        else:
            return rt
    else: #Keyword possibly blank
        return [-1,'Query incomplete',[]]

def query(q):
    """Parse and execute the query
    :param: Query string with mandatory input and header files.
    :return: Matching list of rows
    :return: -1 if error
    :return: Empty list if no rows match
    """
    try:
        return execute_query(q)
    except sqlerror as e:
        return [e.sqlcode,e.message,[]]
