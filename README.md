![](art/logo.png)
# Icecoal
Icecoal is a light weight SQL database

Targets are,
- Apps that require SQL DB or external DB server
- Apps that need lightweight replacement for oracle, MySQL etc.., which they use just to store and retrieve data
- Those who want to add a database in their app without worrying about JDBC, ODBC, connection driver etc. and other technical jargons
- Those who want to conveniently process CSV files with SQL.

### Features:
- Written purely in python
- Light weight (Just 57 Kb in total)
- No external dependencies
- Easy to add in your app/system (Just import!)

### In action
#### Create a Database
![](art/demo/create_db.PNG)
#### Create a table
![](art/demo/create_tb.png)
#### Insert a row in a table
![](art/demo/insert.png)
#### Update a row in a table
![](art/demo/update.png)
#### Delete a row in a table
![](art/demo/delete.png)
#### Select rows from a table
![](art/demo/select.png)
#### Truncate a table
![](art/demo/truncate.png)
#### Drop a table
![](art/demo/drop_tb.png)
#### Drop a database
![](art/demo/drop_db.png)

#### Processing csv files with SQL
![](art/dataflow.png)

![](art/demo/csv.png)

### How to install
```
pip install icecoal
```

### Usage
#### General database oprations
```python
from icecoal import query
query("select name,age from travel_db/passengers where native='USA'")
```
#### Processing your csv data files
```python
from icecoal import query
query("select * from path/to/passengers.csv where native='USA'")
```
Here icecoal expects first line of csv file to be header line.    
if it is not, you can either add headers in first line    
or create a new file just with headers delimited with comma and add it along with data file name in the query as below    
```python
from icecoal import query
query("select * from path/to/passengers.csv, path/to/header.csv where native='USA'")
```

### Return format
```
[sqlcode,'<message>',[result list]]
```
### SQL return codes
| SQL Code | Description |
| --- | --- |
| 2 | 0 row\(s) deleted |
| 3 | 0 row\(s) updated |
| 1 | 0 row\(s) selected |
| 0 | **Success** |
| -1 | Query incomplete |
| -2 |  Unexpected character on position \<index\> |
| -3 |  Unexpected character on where clause position \<index\> |
| -4 |  Unsupported operator in where clause |
| -5 |  Non numeric operand with arithmatic operator \<operator\> |
| -6 | Non boolean operand(LHS) with logical operator \<operator\> |
| -7 | Non boolean operand(RHS) with logical operator \<operator\> |
| -8 | Operator ! must be followed by = |
| -9 | Unbalanced paranthesis on LHS of operator \<operator\> |
| -10 | Unbalanced paranthesis on RHS of operator \<operator\> |
| -11 |  No field \<fieldname\> found in header file |
| -12 | Value for variable \<variablename\> is missing in atleast one row |
| -13 | Where clause condition returns non-boolean result |
| -14 | Incomplete condition in where clause |
| -15 | Database already exist |
| -16 | Table already exist |
| -17 | Database does not exist |
| -18 | Database name is blank |
| -19 | Not a database name |
| -20 | Table does not exist |
| -21 | Not a table name |
| -22 | Header file does not exist |
| -23 | Provided header is not a file |
| -24 | Values count does not match table fields count |
### Reserved words
| Keywords |
| --- |
| SELECT |
| FROM |
| WHERE |
| CREATE |
| DATABASE |
| TABLE |
| INSERT |
| UPDATE |
| SET |
| INTO |
| TRUNCATE |
| DROP |
| DELETE |

### Supported SQL operations and its syntax
* SELECT *column_list* FROM \[*path/to/*]*databasename/tablename*\[*.csv*] \[WHERE *condition*]
* CREATE DATABASE \[*path/to/*]*databasename*
* CREATE TABLE \[*path/to/*]*databasename/tablename*\[*.csv*](*colum1,column2..*)
* DROP DATABASE \[*path/to/*]*databasename*
* DROP TABLE \[*path/to/*]*databasename/tablename*\[*.csv*]
* TRUNCATE TABLE \[*path/to/*]*databasename/tablename*\[*.csv*]
* INSERT INTO \[*path/to/*]*databasename/tablename*\[*.csv*](*value1,value2,..*)
* UPDATE \[*path/to/*]*databasename/tablename*\[*.csv*] SET *field1=value1,field2=value..* \[WHERE *condition*]
* DELETE FROM \[*path/to/*]*databasename/tablename*\[*.csv*] WHERE *condition*

### Operators supported
| Operator type | Operators |
| --- | --- |
| Arithmatic operators | +, -, *, /, % |
| Comparison operators | >, <, >=, <=, =, != |
| Logical operators | &, \| |
| End of query statement | \# (Used internally) |

### Operator precedence (in order from high to low)

**NOTE :** Expression evaluation will use BODMAS as you studied in school. i.e., It has individual operator precedence unlike python or java.   
**Example :** '9-7+1' will result '1'(That's how we were taught in school), where python eval() will return 3 as it treats + and - with equal precedence from left to right

*You can use paranthesis to re-order precedence*

| Operator precedence |
| :---: |
| \% |
| \/ |
| \* |
| + |
| \- |
| <,<= |
| \>,>= |
| != |
| = |
| & |
| \| |

### File formats supported
Comma seperated value(.csv) files.

### Instructions
* Tables are referred with '/' character from database like 'db/table'
* String values should be within '<string>'
* Comparison operator '=' is used instead of '=='
* Database,table names can contain only alphabet, number and underscore
* Field names can contain only alphabets,number and underscore
* All the exceptions are thrown to be handled by users
* By default icecoal stores all its databases in current directory unless you prefix path with tablename
 
### Licence
MIT Licence. Please raise a pull request to contribute.
