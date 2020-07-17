import string

#GLOBAL CONSTANTS
__DEFAULT_DB_PATH__=''    #Default path where all database is stored. if nothing provided, its current directory
__IGNORED_CHARS__=string.whitespace #Allowed white spaces withing query. Add any character here if you want to ignore that. remember to check if any other specific cases present for that character already
DELIMITER=","


# CONSTANTS RELATED TO RULE EXECUTION
alphabet=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
number=['0','1','2','3','4','5','6','7','8','9']
dot=['.']
operator=['%','/','*','+','-','<','>','!','=','&','|']
a_operator=['%','/','*','+','-']
gt_lt=['<','>']
logical=['&','|']
quote=['"',"'"]
singlequote=["'"]
doublequote=['"']
underscore=['_']

class sqlerror(Exception):
    sqlcode=0
    message=''
    def __init__(self,code,msg):
        self.sqlcode = code
        self.message = msg
# Important to note that rule for 'any' should be mentioned at last after specific rules
# RULES FOR EXPRESSION
exp_rules=[
        ["0","(","1",'','ob'],
        ["1","(","1",'','ob'],
        ["1",alphabet+underscore,"2",'varpush',''],
        ["1",number,"3",'operandpush',''],
        ["1",singlequote,"5",'',''],
        ["1",doublequote,"5.1",'',''],
        
        ["2",alphabet+underscore,"2",'operandpush',''],
        ["2",a_operator,"1",'operatorpush','opandop'],
        ["2",gt_lt,"4",'operatorpush','operand'],
        ["2",'!',"9",'operatorpush','operand'],
        ["2",logical,"1",'operatorpush','opandop'],
        ["2",'=',"1",'operatorpush','opandop'],
        ["2",')',"2",'','cb'],
        ["2",'#',"",'','end'],
        
        ["3",number,"3",'operandpush',''],
        ["3",dot,"7",'operandpush',''],
        ["3",')',"3",'','cb'],
        ["3",'#',"",'','end'],
        ["3",'other',"2",'pass','operand'],
        ["4",'=',"1",'operatorpush','opandop'],
        ["4",'other',"1",'pass','operator'],
        ["5",singlequote,"6",'','string'],
        ["5",'any',"5",'operandpush',''],
        ["5.1",doublequote,"6",'','string'],
        ["5.1",'any',"5.1",'operandpush',''],
        ["6",'=',"1",'operatorpush','operator'],
        ["6",'!',"8",'operatorpush',''],
        ["6",')',"6",'','cb'],
        ["6",logical,"1",'operatorpush','opandop'],
        ["6",'#',"",'','end'],
        ["7",number,"7",'operandpush',''],
        ["7",'other',"2",'pass','operand'],
        ["8",'=',"1",'operatorpush','operand'],
        ["9",'=',"1",'operatorpush','operator'],
    ]
    
rule=[

    #NAME RESOLVER
    #state -1 is dedicated to resolve queries that start with same characters
    ['-1',['r','R'],"201",'',''], #To resolve between (D)ROP and (D)ELETE redirect to DROP
    ['-1',['e','E'],"402",'',''], #To resolve between (D)ROP and (D)ELETE redirect to DELETE

    # SELECT
    ["0",string.whitespace,"0",'',''], #Allowind possible extra whitespace
    ['0',['s','S'],"1",'',''],
    ['1',['e','E'],"2",'',''],
    ['2',['l','L'],"3",'',''],
    ['3',['e','E'],"4",'',''],
    ['4',['c','C'],"5",'',''],
    ['5',['t','T'],"6",'',''],
    # Fields to be fetched
    ['6',string.whitespace,"7",'',''],
    ['7',string.whitespace,"7",'',''],
    ['7',['*'],"8",'push',''],
    ['7',alphabet+underscore,"15",'push',''],
    ['8',string.whitespace,"9",'','req'],
    # FROM
    ['9',string.whitespace,"9",'',''],
    ['9',['f','F'],"10",'',''],
    ['10',['r','R'],"11",'',''],
    ['11',['o','O'],"12",'',''],
    ['12',['m','M'],"13",'',''],
    # Table name
    ['13',string.whitespace,"14",'',''],
    ['14',string.whitespace,"14",'',''],
    ['14',alphabet+underscore+['\\','/','.'],"17",'push',''],
    #Required fields
    ['15',string.whitespace,"15.1",'','req'],
    ['15',[','],"15.2",'','req'],
    ['15',alphabet+underscore+number,"15",'push',''],
    ['15.1',string.whitespace,"15.1",'',''],     #
    ['15.1',['f','F'],"10",'',''],               # Ignore white spaces before comma
    ['15.1',',',"15.2",'',''],                   #
    ['15.2',string.whitespace,"15.2",'',''],     #-Ignore white spaces after comma
    ['15.2',alphabet+underscore,"15",'push',''], #-
    # Table name
    ['17',[','],"17.2",'','csv'],
    ['17',string.whitespace,"17.1",'','csv'],
    ['17',['#'],"end",'','csv_select'], #Query without header file
    ['17',['_','.','/','\\',':']+alphabet+number,"17",'push',''],
    
    ['17.1',string.whitespace,"17.1",'',''],
    ['17.1',['#'],"end",'','csv_select'], #Query without header file
    ['17.1',[','],"17.2",'',''],
    ['17.1',['w','W'],"20",'',''],
    ['17.2',string.whitespace,"17.2",'',''],
    ['17.2',alphabet+underscore+['\\','/','.'],"18.1",'push',''],
    # Header file
    #['18',alphabet+underscore,"18.1",'push',''],
    ['18.1',['_','.','/','\\',':']+alphabet+number,"18.1",'push',''],
    ['18.1',['#'],'end','','head_select'],
    ['18.1',string.whitespace,"19",'','head'],
    # WHERE
    ['19',string.whitespace,"19",'',''],
    ['19',['#'],'end','','head_select'],
    ['19',['w','W'],"20",'',''],
    ['20',['h','H'],"21",'',''],
    ['21',['e','E'],"22",'',''],
    ['22',['r','R'],"23",'',''],
    ['23',['e','E'],"24",'',''],
    # Condition to be met
    ['24',string.whitespace,"24",'',''],
    #open bracket
    ['24','(',"24",'push',''],
    ['24',')',"24",'push',''],
    #variable
    ['24',alphabet+underscore,"24.1",'push',''],
        ['24.1',alphabet+underscore+number,"24.1",'push',''],
        ['24.1','any',"24",'pass',''],
    #number
    ['24',number+['.'],"24.2",'push',''],
        ['24.2',number+['.'],"24.2",'push',''],
        ['24.2','any',"24",'pass',''],
    ['24',singlequote,"24.3",'push',''],
        ['24.3',singlequote,"24",'push',''],
        ['24.3','any',"24.3",'push',''],
    ['24',doublequote,"24.4",'push',''],
        ['24.4',doublequote,"24",'push',''],
        ['24.4','any',"24.4",'push',''],
    
    ['24',operator,"24",'push',''],
    ['24',['#'],'end','','exp_select'],
    
    #CREATE
    ['0',['c','C'],"101",'',''],
    ['101',['r','R'],"102",'',''],
    ['102',['e','E'],"103",'',''],
    ['103',['a','A'],"104",'',''],
    ['104',['t','T'],"105",'',''],
    ['105',['e','E'],"106",'',''],
    ['106',string.whitespace,"107",'',''],
    # DATABASE
    ['107',string.whitespace,"107",'',''],
    ['107',['d','D'],"108",'',''],
    ['108',['a','A'],"109",'',''],
    ['109',['t','T'],"110",'',''],
    ['110',['a','A'],"111",'',''],
    ['111',['b','B'],"112",'',''],
    ['112',['a','A'],"113",'',''],
    ['113',['s','S'],"114",'',''],
    ['114',['e','E'],"115",'',''],
    ['115',string.whitespace,"115.1",'',''],
    ['115.1',string.whitespace,"115.1",'',''],
    ['115.1','any',"116",'pass',''],
    # Database name
    ['116',alphabet+number+underscore+['/','\\',':','.'],"116",'dbpush',''], #Push the characters of db name in temp variable
    ['116',string.whitespace,'116.1','',''],
    ['116',['#'],"end",'','mkdb'],
    ['116.1',string.whitespace,'116.1','',''],
    ['116.1',['#'],'end','','mkdb'],
    # TABLE
    ['107',['t','T'],"151",'',''],
    ['151',['a','A'],"152",'',''],
    ['152',['b','B'],"153",'',''],
    ['153',['l','L'],"154",'',''],
    ['154',['e','E'],"155",'',''],
    
    ['155',string.whitespace,"155.1",'',''],
    ['155.1',string.whitespace,"155.1",'',''],
    ['155.1','any',"156",'pass',''],
    
    # Table name
    ['156',alphabet+number+underscore+['/','\\',':','.'],"156",'tablepush',''],
    
    ['156',string.whitespace,"156.1",'',''],
    ['156.1',string.whitespace,"156.1",'',''],
    ['156.1',['('],"156.2",'','tablename'],
    
    ['156',['('],"156.2",'','tablename'],
    
    ['156.2',string.whitespace,"156.2",'',''],
    ['156.2',string.whitespace,"156.2",'',''],
    ['156.2','any',"157",'pass',''],
    
    # Field names
    ['157',alphabet+underscore,"158",'headerpush',''], #To ensure field names can start only with alphabet and underscore
    ['158',alphabet+number+underscore,"158",'headerpush',''],
    
    ['158',string.whitespace,"158.1",'',''],
    ['158.1',string.whitespace,"158.1",'',''],
    ['158.1',[','],"156.2",'headerpush',''],
    ['158.1',[')'],"159",'','header'],
    
    ['158',[','],"156.2",'headerpush',''],
    ['158',[')'],"159",'','header'],
    ['159',['#'],"end",'','mktable'],
    
    ['159',string.whitespace,"159.1",'',''],
    ['159.1',string.whitespace,"159.1",'',''],
    ['159.1',['#'],"end",'','mktable'],
    
    # DROP
    ['0',['d','D'],"-1",'',''], #Redirecting to -1 to resolve between (D)elete
    ['201',['o','O'],"202",'',''],
    ['202',['p','P'],"203",'',''],
    
    ['203',string.whitespace,"203.1",'',''],
    ['203.1',string.whitespace,"203.1",'',''],
    ['203.1',['d','D'],"205",'',''],
    
    ['205',['a','A'],"206",'',''],
    ['206',['t','T'],"207",'',''],
    ['207',['a','A'],"208",'',''],
    ['208',['b','B'],"209",'',''],
    ['209',['a','A'],"210",'',''],
    ['210',['s','S'],"211",'',''],
    ['211',['e','E'],"212",'',''],
    
    ['212',string.whitespace,"212.1",'',''],
    ['212.1',string.whitespace,"212.1",'',''],
    ['212.1','any',"213",'pass',''],
    
    # Database name
    ['213',alphabet+number+underscore+['/','\\',':','.'],"213",'dbpush',''], #Push the characters of db name in temp variable
    
    ['213',string.whitespace,"213.1",'',''],
    ['213.1',string.whitespace,"213.1",'',''],
    ['213.1',['#'],"end",'','drdb'],
    
    ['213',['#'],"end",'','drdb'],
    # TABLE
    ['203.1',['t','T'],"221",'',''],
    ['221',['a','A'],"222",'',''],
    ['222',['b','B'],"223",'',''],
    ['223',['l','L'],"224",'',''],
    ['224',['e','E'],"225",'',''],
    
    ['225',string.whitespace,"225.1",'',''],
    ['225.1',string.whitespace,"225.1",'',''],
    ['225.1','any',"226",'pass',''],
    
    # Table name
    ['226',alphabet+number+underscore+['/','\\',':','.'],"226",'tablepush',''],
    
    ['226',string.whitespace,"226.1",'',''],
    ['226.1',string.whitespace,"226.1",'',''],
    ['226.1',['#'],"end",'','drtb'],
    
    ['226',['#'],"end",'','drtb'],
    
    
    # TRUNCATE
    ['0',['t','T'],"250",'',''],
    ['250',['r','R'],"251",'',''],
    ['251',['u','U'],"252",'',''],
    ['252',['n','N'],"253",'',''],
    ['253',['c','C'],"254",'',''],
    ['254',['a','A'],"255",'',''],
    ['255',['t','T'],"256",'',''],
    ['256',['e','E'],"257",'',''],
    ['257',string.whitespace,"258",'',''],
    # TABLE
    ['258',string.whitespace,"258",'',''],
    ['258',['t','T'],"259",'',''],
    ['259',['a','A'],"260",'',''],
    ['260',['b','B'],"261",'',''],
    ['261',['l','L'],"262",'',''],
    ['262',['e','E'],"263",'',''],
    #['263',[' '],"264",'',''],
    
    ['263',string.whitespace,"263.1",'',''],
    ['263.1',string.whitespace,"263.1",'',''],
    ['263.1','any',"264",'pass',''],
    
    # Table name
    ['264',alphabet+number+underscore+['/','\\',':','.'],"264",'tablepush',''],
    ['264',['#'],"end",'','trtb'],
    
    ['264',string.whitespace,"264.1",'',''],
    ['264.1',string.whitespace,"264.1",'',''],
    ['264.1',['#'],"end",'','trtb'],
    
    # INSERT INTO
    ['0',['i','I'],"300",'',''],
    ['300',['n','N'],"301",'',''],
    ['301',['s','S'],"302",'',''],
    ['302',['e','E'],"303",'',''],
    ['303',['r','R'],"304",'',''],
    ['304',['t','T'],"305",'',''],
    ['305',string.whitespace,"306",'',''],
    ['306',string.whitespace,"306",'',''],
    ['306',['i','I'],"307",'',''],
    ['307',['n','N'],"308",'',''],
    ['308',['t','T'],"309",'',''],
    ['309',['o','O'],"310",'',''],
    #['310',[' '],"311",'',''],
    
    ['310',string.whitespace,"310.1",'',''],
    ['310.1',string.whitespace,"310.1",'',''],
    ['310.1','any',"311",'pass',''],
    
    # Table name
    ['311',alphabet+number+underscore+['/','\\',':','.'],"311",'tablepush',''],
    
    ['311',string.whitespace,"311.1",'',''],
    ['311.1',string.whitespace,"311.1",'',''],
    ['311.1',['('],"312",'','tablename'],
    
    ['311',['('],"312",'','tablename'],
   
    
    ['312',[')'],"313",'','row'],
    ['312',string.whitespace,"312",'',''],
    ['312',[','],"312",'listpush',''],
    
    ['312',singlequote,"312.1",'',''],
    ['312.1',singlequote,"312",'',''],
    ['312.1','any',"312.1",'valuepush',''],

    ['312',doublequote,"312.4",'',''],
    ['312.4',doublequote,"312",'',''],
    ['312.4','any',"312.4",'valuepush',''],
    
    ['312',"any","312.2",'valuepush',''],
    ['312.2',string.whitespace,"312.3",'',''],
    ['312.2',[','],"312",'listpush',''],
    ['312.2',[')'],"313",'','row'],
    ['312.2',"any","312.2",'valuepush',''],
    ['312.3',string.whitespace,"312.3",'',''],
    ['312.3',[','],"312",'listpush',''],
    ['312.3',[')'],"313",'','row'],
    
    ['313',string.whitespace,"313",'',''],
    ['313',['#'],"end",'','insert'],
    
    # UPDATE
    ['0',['u','U'],"350",'',''],
    ['350',['p','P'],"351",'',''],
    ['351',['d','D'],"352",'',''],
    ['352',['a','A'],"353",'',''],
    ['353',['t','T'],"354",'',''],
    ['354',['e','E'],"355",'',''],
    
    ['355',string.whitespace,"355.1",'',''],
    ['355.1',string.whitespace,"355.1",'',''],
    ['355.1','any',"356",'pass',''],
    
    # Table name
    ['356',alphabet+number+underscore+['/','\\',':','.'],"356",'tablepush',''],
    ['356',[','],"356.2",'','csv'],
    ['356',string.whitespace,"356.1",'','csv'],
    ['356.1',string.whitespace,"356.1",'',''],
    ['356.1',[','],"356.2",'',''],
    ['356.1',['s','S'],"357.2",'',''],
    ['356.2',string.whitespace,"356.2",'',''],
    ['356.2','any',"357",'pass',''],
    ['357',alphabet+number+underscore+['/','\\',':','.'],"357",'headpush',''],
    ['357',string.whitespace,"357.1",'','head'],
    # Var val pairs
    ['357.1',string.whitespace,"357.1",'',''],
    ['357.1',['s','S'],"357.2",'',''],
    ['357.2',['e','E'],"357.3",'',''],
    ['357.3',['t','T'],"357.4",'',''],
    ['357.4',string.whitespace,"357.5",'',''],
    ['357.5',string.whitespace,"357.5",'',''],
    ['357.5','any',"358",'pass',''],
    ['358',alphabet+underscore,"359",'keypush',''], #To ensure field names can start only with alphabet and underscore
    ['359',alphabet+number+underscore,"359",'keypush',''],
    ['359',string.whitespace,"359.1",'',''],
    ['359',['='],"359.2",'','key'],
    ['359.1',string.whitespace,"359.1",'',''],
    ['359.1',['='],"359.2",'','key'],
    ['359.2',string.whitespace,"359.2",'',''],
    ['359.2','any',"359.3",'pass',''],
    ['359.3',singlequote,"359.4",'',''],
        ['359.4',singlequote,"359.3",'','value'],
        ['359.4','any',"359.4",'valpush',''],   
    ['359.3',doublequote,"359.41",'',''],
        ['359.41',doublequote,"359.3",'','value'],
        ['359.41','any',"359.41",'valpush',''],   
    ['359.3',[','],"357.5",'','value'],
    ['359.3',string.whitespace,"359.5",'',''],
        ['359.5',string.whitespace,"359.5",'',''],
        ['359.5',[','],"357.5",'',''],
        ['359.5',['w','W'],"363",'','value'],
        ['359.5',['#'],"end",'','updateall'],
    ['359.3','any',"359.3",'valpush',''],
    
    ['359.3',['#'],"end",'','updateall'],
    
    ['362',['w','W'],'363','',''],
    ['363',['h','H'],'364','',''],
    ['364',['e','E'],'365','',''],
    ['365',['r','R'],'366','',''],
    ['366',['e','E'],'367','',''],

    
    # Condition to be met
    ['367',string.whitespace,"367",'',''],
    #open bracket
    ['367','(',"367",'push',''],
    ['367',')',"367",'push',''],
    #variable
    ['367',alphabet+underscore,"367.1",'push',''],
        ['367.1',alphabet+underscore+number,"367.1",'push',''],
        ['367.1','any',"367",'pass',''],
    #number
    ['367',number+['.'],"367.2",'push',''],
        ['367.2',number+['.'],"367.2",'push',''],
        ['367.2','any',"367",'pass',''],
    ['367',singlequote,"367.3",'push',''],
        ['367.3',singlequote,"367",'push',''],
        ['367.3','any',"367.3",'push',''],
    ['367',doublequote,"367.31",'push',''],
        ['367.31',doublequote,"367",'push',''],
        ['367.31','any',"367.31",'push',''],
    
    ['367',operator,"367",'push',''],
    ['367',['#'],'end','','exp_update'],

    
    
    # DELETE
    ['0',['d','D'],"-1",'',''], # Redirecting to -1 to resolve with (D)ROP
    ['402',['l','L'],"403",'',''],
    ['403',['e','E'],"404",'',''],
    ['404',['t','T'],"405",'',''],
    ['405',['e','E'],"408",'',''],
    ['408',string.whitespace,"409",'',''],
    # FROM
    ['409',string.whitespace,"409",'',''],
    ['409',['f','F'],"410",'',''],
    ['410',['r','R'],"411",'',''],
    ['411',['o','O'],"412",'',''],
    ['412',['m','M'],"413",'',''],
    
    # Table name
    ['413',string.whitespace,"414",'',''],
    ['414',string.whitespace,"414",'',''],
    ['414',alphabet+underscore+['\\','/','.'],"417",'push',''],
    # Table name
    ['417',[','],"417.2",'','csv'],
    ['417',string.whitespace,"417.1",'','csv'],
    ['417',['_','.','/','\\',':']+alphabet+number,"417",'push',''],
    
    ['417.1',string.whitespace,"417.1",'',''],
    ['417.1',[','],"417.2",'',''],
    ['417.1',['w','W'],"420",'',''],
    ['417.2',string.whitespace,"417.2",'',''],
    ['417.2',alphabet+underscore+['\\','/','.'],"418.1",'push',''],
    # Header file
    ['418.1',['_','.','/','\\',':']+alphabet+number,"418.1",'push',''],
    ['418.1',string.whitespace,"419",'','head'],
    # WHERE
    ['419',string.whitespace,"419",'',''],
    ['419',['w','W'],"420",'',''],
    ['420',['h','H'],"421",'',''],
    ['421',['e','E'],"422",'',''],
    ['422',['r','R'],"423",'',''],
    ['423',['e','E'],"424",'',''],
    # Condition to be met
    ['424',string.whitespace,"424",'',''],
    #open bracket
    ['424','(',"424",'push',''],
    ['424',')',"424",'push',''],
    #variable
    ['424',alphabet+underscore,"424.1",'push',''],
        ['424.1',alphabet+underscore+number,"424.1",'push',''],
        ['424.1','any',"424",'pass',''],
    #number
    ['424',number+['.'],"424.2",'push',''],
        ['424.2',number+['.'],"424.2",'push',''],
        ['424.2','any',"424",'pass',''],
    ['424',singlequote,"424.3",'push',''],
        ['424.3',singlequote,"424",'push',''],
        ['424.3','any',"424.3",'push',''],
    ['424',doublequote,"424.31",'push',''],
        ['424.31',doublequote,"424",'push',''],
        ['424.31','any',"424.31",'push',''],
    
    ['424',operator,"424",'push',''],
    ['424',['#'],'end','','delete']

    
    
    ]