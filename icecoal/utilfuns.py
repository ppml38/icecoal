import os
import shutil
from .expression import evalthis
from .const import *

def setdel(deli):
    global DELIMITER
    DELIMITER=deli
    return None
def getdel():
    global DELIMITER
    return DELIMITER

def __select(required_fields,csvfile,headfile,etree):
    '''Function that returns rows that match the condition given
    @param: requiired_fields-list of fields that need to be returned or *
    @param: csvfile-String of table name
    @param: headfile-String of header file name or empty
    @param: etree-Instance of Node. Root node of the expression tree created with given condition
    @return: 0 with result set or empty set if the query successfull
    @return: -1 if the table does not exist
    @return: -2 if given csvfile is not a name of a table
    @return: -3 if header file does not exist
    @return: -4 if header file is not name of a file
    @return: -5 field mentioned in select not found in table
    '''
    global DELIMITER
    print(DELIMITER.encode())
    #Initiate result set to empty
    result=[]
    count=0
    #Open table if exist
    if os.path.exists(csvfile):
        if os.path.isfile(csvfile):
            __csv_file=open(csvfile,'r')
        else:
            return -2
    else:
        return -1

    #open headfile if exist
    if headfile=='': # If no header file provided, first line of csvfile is the header line
        head=__csv_file.readline().strip('\n').split(DELIMITER)
    else:
        if os.path.exists(headfile):
            if os.path.isfile(headfile):
                hf=open(headfile,"r")
                head=hf.readline().strip('\n').split(DELIMITER)
                hf.close()
            else:
                return -4
        else:
            return -3
    line=__csv_file.readline()
    while(len(line)!=0): #Until end of file
        if len(line.strip('\n'))!=0: #If the line is empty line
            row=line.strip('\n').split(DELIMITER)
            exec_result=evalthis(etree,head,row)
            if(exec_result==True):
                if required_fields[0]=='*':
                    result.append(row)
                else:
                    temp_result=[]
                    for i in range(0,len(required_fields)):
                        found=False
                        for j in range(0,len(head)):
                            if head[j]==required_fields[i]:
                                found=True
                                if j<len(row):
                                    temp_result.append(row[j])
                                else:
                                    raise sqlerror(-12,"Value for variable "+head[j]+" is missing in atleast one row")
                                break
                        if not found:
                            raise sqlerror(-11,"No field "+required_fields[i]+" found in header")
                    result.append(temp_result)
            elif exec_result==False:
                pass
            else:
                raise sqlerror(-13,"Where clause condition returns non-boolean result")
        else:
            pass #Empty line, ignore it silently
        line=__csv_file.readline()
    __csv_file.close()
    count=len(result)
    if count==0:
        return [1,'0 rows selected',result]
    else:
        return [0,str(count)+' rows selected',result]

def __update(fields,values,csvfile,headfile,etree):
    '''Ipdates the table with given values
    @param: fields, list of fields that need to be changed
    @param: values, list of corresponding values of above given fields
    @param: csvfile-String of data file name
    @param: headfile-String of header file name or empty
    @param: etree-Instance of Node. Root node of the expression tree created with given condition
    @return: 0 if the update was successful
    @return: -1 if the table does not exist
    @return: -2 if given csvfile is not a name of a table
    @return: -3 if header file does not exist
    @return: -4 if header file is not name of a file
    @Throws: Exceptopm if any other error occured
    '''
    __csv_file=None
    __res_csv_file=None
    count=0
    try: #Execute the update process inside try, in case of any exception, Updates will be rolled back
        #Rename the table file to .bak
        #Open table if exist
        if os.path.exists(csvfile):
            if os.path.isfile(csvfile):
                os.rename(csvfile,csvfile+".bak")
                __csv_file=open(csvfile+".bak",'r')
            else:
                return -2
        else:
            return -1

        #open headfile if exist
        if headfile=='': # If no header file provided, first line of csvfile is the header line
            head=__csv_file.readline().strip('\n').split(DELIMITER)
        else:
            if os.path.exists(headfile):
                if os.path.isfile(headfile):
                    hf=open(headfile,"r")
                    head=hf.readline().strip('\n').split(DELIMITER)
                    hf.close()
                else:
                    return -4
            else:
                return -3
                
        #Open the resultant file with .bak2 extension. this will then be renamed to original csvfile once all updates performed
        __res_csv_file=open(csvfile+".bak2","w") #Note this may overwrite unfinished operation performed earlier
        #Write the header inside the file
        firstline=True
        if headfile=='':
            __res_csv_file.write(DELIMITER.join(head))
            firstline=False
        
        line=__csv_file.readline()
        while(len(line)!=0): #Until end of file
            if len(line.strip('\n'))!=0: #If the line is empty line
                row=line.strip('\n').split(DELIMITER)
                exec_result=evalthis(etree,head,row)
                if(exec_result==True): #Means this row should be updated before written in result file.
                    count+=1
                    for i in range(0,len(fields)):
                        field_found=False #To check if the field provided is part of table
                        for j in range(0,len(head)):
                            if head[j]==fields[i]:
                                field_found=True
                                if j<len(row): #check if the row contains value for given field
                                    row[j]=values[i]
                                else:
                                    raise sqlerror(-12,"Value for variable "+head[j]+" is missing in atleast one row")
                                break
                        if not field_found:
                            raise sqlerror(-11,"No field "+fields[i]+" found in header")
                    if firstline:
                        __res_csv_file.write(DELIMITER.join(row)) #without prepending new line
                        firstline=False
                    else:
                        __res_csv_file.write("\n"+(DELIMITER.join(row))) #with prepending new line
                elif exec_result==False:
                    if firstline:
                        __res_csv_file.write(line.strip('\n')) #Writing the read line back with no change. Note here while reading \n was at end of line but while writing its in front
                        firstline=False
                    else:
                        __res_csv_file.write("\n"+line.strip('\n')) #Writing the read line back with no change. Note here while reading \n was at end of line but while writing its in front
                        
                else:
                    raise sqlerror(-13,"Where clause condition returns non-boolean result")
            else:
                pass #Empty line, ignore it silently
            line=__csv_file.readline()
        __csv_file.close()
        __res_csv_file.close()
        os.remove(csvfile+".bak")
        os.rename(csvfile+".bak2",csvfile)
        if count==0:
            return [3,'0 rows updated',[]]
        else:
            return [0,str(count)+' row(s) updated',[]]
    except:
        raise #Every exception will be thrown back to inform users
    finally: #Check table health and Rollback if necessary
        if __csv_file!=None:
            if not __csv_file.closed:
                __csv_file.close()
        if __res_csv_file!=None:
            if not __res_csv_file.closed:
                __res_csv_file.close()
        if os.path.isfile(csvfile):
            pass #Table is healthy
        elif os.path.isfile(csvfile+".bak"): #Error occured before deleting backup file, hence restore backup
            os.rename(csvfile+".bak",csvfile)
        elif os.path.isfile(csvfile+".bak2"): #Error occured before renaming result file. hence proceed with rename
            os.rename(csvfile+".bak2",csvfile)
        #Exceptions in finally clause is unhandled to inform user

def __delete(csvfile,headfile,etree):
    '''Deletes the row that matching condition
    @param: csvfile-String of data file name
    @param: headfile-String of header file name or empty
    @param: etree-Instance of Node. Root node of the expression tree created with given condition
    @return: 0 if the delete was successful
    @return: -1 if the table does not exist
    @return: -2 if given csvfile is not a name of a table
    @return: -3 if header file does not exist
    @return: -4 if header file is not name of a file
    @Throws: Exceptopm if any other error occured
    '''
    __csv_file=None
    __res_csv_file=None
    count=0
    try: #Execute the update process inside try, in case of any exception, Updates will be rolled back
        #Rename the table file to .bak
        #Open table if exist
        if os.path.exists(csvfile):
            if os.path.isfile(csvfile):
                os.rename(csvfile,csvfile+".bak")
                __csv_file=open(csvfile+".bak",'r')
            else:
                return -2
        else:
            return -1

        #open headfile if exist
        if headfile=='': # If no header file provided, first line of csvfile is the header line
            head=__csv_file.readline().strip('\n').split(DELIMITER)
        else:
            if os.path.exists(headfile):
                if os.path.isfile(headfile):
                    hf=open(headfile,"r")
                    head=hf.readline().strip('\n').split(DELIMITER)
                    hf.close()
                else:
                    return -4
            else:
                return -3
                
        #Open the resultant file with .bak2 extension. this will then be renamed to original csvfile once all updates performed
        __res_csv_file=open(csvfile+".bak2","w") #Note this may overwrite unfinished operation performed earlier
        #Write the header inside the file
        firstline=True
        if headfile=='':
            __res_csv_file.write(DELIMITER.join(head))
            firstline=False
        
        line=__csv_file.readline()
        while(len(line)!=0): #Until end of file
            if len(line.strip('\n'))!=0: #If the line is empty line
                row=line.strip('\n').split(DELIMITER)
                exec_result=evalthis(etree,head,row)
                if(exec_result==True): #Means this row should be updated before written in result file.
                    count+=1
                    pass #This line will not be written in the result file. Hence deleted
                elif exec_result==False:
                    if firstline:
                        __res_csv_file.write(line.strip('\n')) #Writing the read line back with no change. Note here while reading \n was at end of line but while writing its in front
                        firstline=False
                    else:
                        __res_csv_file.write("\n"+line.strip('\n')) #Writing the read line back with no change. Note here while reading \n was at end of line but while writing its in front
                        
                else:
                    raise sqlerror(-13,"Where clause condition returns non-boolean result")
            else:
                pass #Empty line, ignore it silently
            line=__csv_file.readline()
        __csv_file.close()
        __res_csv_file.close()
        os.remove(csvfile+".bak")
        os.rename(csvfile+".bak2",csvfile)
        if count==0:
            return [2,'0 rows deleted',[]]
        else:
            return [0,str(count)+' row(s) deleted',[]]
    except:
        raise #Every exception will be thrown back to inform users
    finally: #Check table health and Rollback if necessary
        if __csv_file!=None:
            if not __csv_file.closed:
                __csv_file.close()
        if __res_csv_file!=None:
            if not __res_csv_file.closed:
                __res_csv_file.close()
        if os.path.isfile(csvfile):
            pass #Table is healthy
        elif os.path.isfile(csvfile+".bak"): #Error occured before deleting backup file, hence restore backup
            os.rename(csvfile+".bak",csvfile)
        elif os.path.isfile(csvfile+".bak2"): #Error occured before renaming result file. hence proceed with rename
            os.rename(csvfile+".bak2",csvfile)
        #Exceptions in finally clause is unhandled to inform user


def __mkdb(dbname):
    '''Private function that creates a new database with given [path]name
    If dbname given with no path, it will be created in current directory
    @param: dbname - String Database name to be created
    @return: 0 if the database created
    @return: -1 if database already exists
    @throws: Exception if database could not be created due to environment or permission issues.
    '''
    if dbname !='':
        #If there is no such folder create one
        if not os.path.exists(dbname):
            os.makedirs(dbname)
            return 0
        #If directory already exists do nothing
        else:
            return -1
    #If the dbname is empty, do nothing
    else:
        pass

def __mktable(tablename,header): #Optionally with path
    '''Creates a table with given path and header content
    If table name given with no path, it will be created in current directory
    @param: tablename - String name of table to be created
    @param: header - String header of the csv file
    @return: 0 if table creation successful
    @return: -1 if the table already exists
    @return: -2 if database does not exists
    @return: -3 Database name is blank
    @throws: Exception if the table could not be created due to environment issues or permission issues
    '''
    if ((tablename!='')&(header!='')):
        #If there is no such table create one
        if os.path.dirname(tablename)=='':
            return -3
        if (os.path.dirname(tablename)!='') and not os.path.exists(os.path.dirname(tablename)):
            return -2
        if not os.path.exists(tablename):
            newfile=open(tablename,'w')
            newfile.write((DELIMITER.join(header.split(","))))
            newfile.close()
            return 0
        #If table already exists do nothing return error code
        else:
            return -1
    #If empty table or header name passed, do nothing
    else:
        pass

def __insertrow(tablename,row):
    '''Inserts given row in given table as a last row
    This inserts a new lineseparator specific to current os at every line end
    @param: tablename, string with dbname/tablename.csv format
    @param: row, string of comma separated values to be inserted in the table
    @return: 0 if the row inserted successfully
    @return: -1 if the table does not exist
    @return: -2 if given is not a table name
    @return: -3 if provided values count does not match with field count
    @throws: Exception if the operation could not be carried out due to other reasons
    '''
    givenfile=None
    try:
        if os.path.exists(tablename):
            if os.path.isfile(tablename):
                givenfile=open(tablename,'a+')
                
                #Check if provided field count matches with table's field count
                givenfile.seek(0)
                if (len(givenfile.readline().strip('\n').split(DELIMITER))) == (len(row.split(","))): #row will still be delimited by comma coming from query, we have to change to current DELIMITER when writing on file.
                
                    #It is important NOT TO use os.linesep here instead of \n. Because, by default, while 'writing' python will replace all \n chars
                    #to os.linesep. so if we use os.linesep instead of \n, that will translate into \r\n in windows and further \n will be replaced with
                    #os.linesep(i.e.,\r\n). So atlast you will get \r\r\n written in storage, which will then be read as empty line and a line separator in windows.
                    givenfile.write("\n"+(DELIMITER.join(row.split(",")))) #As we are adding \n here python will replace this with os.linesep(\r\n). which is important to avoid
                                            #appending new lines with existing last line instead of next line
                else:
                    givenfile.close()
                    return -3
                
                givenfile.close()
                return 0
            else:
                return -2
        else:
            return -1
    except:
        raise
    finally:
        if givenfile!=None:
            if not givenfile.closed:
                givenfile.close()
        

def __dropdb(dbname):
    '''Drops a database with all of its tables
    @param: dbname - String, name of the database to be deleted.
    @return: -1 if the database doesnt exist
    @return: -2 if the given dbname is not a directory name
    '''
    if os.path.exists(dbname):
        if os.path.isdir(dbname):
            shutil.rmtree(dbname)
            return 0
        else:
            return -2
    else:
        return -1
        
def __droptable(tablename):
    '''Drops a table
    @param: table - String, name of the table to be deleted with its database name
    @return: -1 if the table does not exist
    @return: -2 if the given table name is not a table
    '''
    if os.path.exists(tablename):
        if os.path.isfile(tablename):
            os.remove(tablename)
            return 0
        else:
            return -2
    else:
        return -1
        
def __truntable(tablename):
    '''Truncates the table
    @param: table - String, name of the table to be truncated with the database name
    @return: -1 if the table does not exist
    @return: -2 if the given table name is not a table
    @return: Return codes of __mktable function
    '''
    f=None
    try:
        if os.path.exists(tablename):
            if os.path.isfile(tablename):
                f = open(tablename,'r')
                header=f.readline().strip('\n')
                f.close()
                
                f= open(tablename,'w')
                f.write(header)
                f.close()
                return 0
            else:
                return -2
        else:
            return -1
    except:
        raise
    finally:
        if f!=None:
            if not f.closed:
                f.close()
    