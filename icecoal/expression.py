from .const import *

class node:
    parent=None
    
    left=None
    operator=None
    right=None
    result=None
    
    left_type=None
    right_type=None
    
    isvar=None
    
    
    
    def __init__(self,a):
        self.parent=a

def par(exp):
    ops=['%','/','*','+','-','<','>','!','=','&','|'] #in the order of precedence
    # Replace all the negative operands into (0-operand)
    exp_length=len(exp)
    for n in range(0,exp_length):
        if (exp[n]=='-') and ((n==0) or (exp[n-1]=='(') or (exp[n-1]=='=')):
            exp=exp[:n]+'(0'+exp[n:]
            n+=3 #Compensating above added 2 chars + 1
            f=False
            br=0
            for m in range(n,len(exp)):
                if (exp[m]=='('):
                    br+=1
                if (exp[m]==')'):
                    if br>0:
                        br-=1
                    if br==0:
                        exp=exp[:m]+')'+exp[m:]
                        f=True
                        break  
                if (exp[m] in operator) and (br==0):
                    exp=exp[:m]+')'+exp[m:]
                    f=True
                    break
            if not f:
                raise sqlerror(-14,"Incomplete condition in where clause")

    for op in ops:

        i=0
        while i<len(exp):

            if exp[i]==op:
                #Check if ! operator has = next
                if (exp[i]=='!') and (exp[i+1]!='='):
                    raise sqlerror(-8,"Operator ! must be followed by =")
                #Loop back for open bracket
                if (exp[i]=='=') and (exp[i-1] in ['<','>','!']): #Skip 2 char operators
                    #j=i-2
                    break
                else:
                    j=i-1
                    
                bracket=0
                while j>=0:
                    if bracket==0:
                        if exp[j] in ops:
                            exp=exp[:j+1]+'('+exp[j+1:]
                            i+=1
                            break
                        elif exp[j]==')':
                            bracket+=1
                        elif j==0:
                            exp='('+exp
                            i+=1
                            break
                    else:
                        if exp[j]=='(':
                            bracket-=1
                            if bracket==0:
                                exp=exp[:j]+'('+exp[j:]
                                i+=1
                                break
                        elif exp[j]==')':
                            bracket+=1
                        if (j==0)&(bracket!=0):
                            raise sqlerror(-9,"Unbalanced paranthesis on LHS of operator "+op)
                    j-=1
                #Loop forward for close bracket
                j=i+1 #To compensate the additional open bracket added
                bracket=0
                l=len(exp)
                if (exp[j]=='=' ) and (exp[j-1] in ['>','<','!']): #Skip 2 char operators
                    j+=1
                while j<l:
                    if bracket==0:
                        if exp[j] in ops:
                            exp=exp[:j]+')'+exp[j:]
                            break
                        elif exp[j]=='(':
                            bracket+=1
                        elif j==(len(exp)-1):
                            exp=exp+')'
                            
                    else:
                        if exp[j]==')':
                            bracket-=1
                            if bracket==0:
                                exp=exp[:j]+')'+exp[j:]
                                break
                        elif exp[j]=='(':
                            bracket+=1
                        if (j==(len(exp)-1)) & (bracket!=0):
                            raise sqlerror(-10,"Unbalanced paranthesis on RHS of operator "+op)
                    j+=1

            i+=1

    return exp



def calculate(a,op,b,a_type,b_type):
    ops=['%','/','*','+','-','<','<=','>','>=','!=','=','&','|']
    if op not in ops:
        raise sqlerror(-4,"Unsupported operator "+str(op)+" in where clause")
    #Arithmatic and comparison operations
    if op in ['%','/','*','+','-','<','<=','>','>=']:
        #Arithmatic operations allowed only for integer and floats
        #Always returns float
        try:
            a=float(a)
            b=float(b)
        except ValueError:
            raise sqlerror(-5,"Non numeric operand with arithmatic operator "+str(op))
        if op=='%':
            return a%b
        if op=='/':
            return a/b
        if op=='*':
            return a*b
        if op=='+':
            return a+b
        if op=='-':
            return a-b
        if op=='>':
            return a>b
        if op=='>=':
            return a>=b
        if op=='<':
            return a<b
        if op=='<=':
            return a<=b
    #Equality check operators
    if op in ['!=','=']:
        #Arithmatic operations allowed only for integer and floats
        #Always returns float
        if a_type=='str' or b_type=='str': #Handle values surrounded with quotes in query as string only not float
            a=str(a)
            b=str(b)
        else:
            try:
                a_temp=float(a)
                b_temp=float(b) #To conserve initial form of a when there is error in b
                a=a_temp
                b=b_temp
            except ValueError:
                a=str(a)
                b=str(b)


        if op=='!=':
            return a!=b
        if op=='=':

            return a==b
    #Logical operators
    if op in ['&','|']:
        #Convert a
        if str(a)=='True':
            a=True
        elif str(a)=='False':
            a=False
        else:
            raise sqlerror(-6,"Non boolean operand(LHS) with logical operator "+str(op))
        #Convert a
        if str(b)=='True':
            b=True
        elif str(b)=='False':
            b=False
        else:
            raise sqlerror(-7,"Non boolean operand(RHS) with logical operator "+str(op))
        if op=='&':
            return a and b
        if op=='|':
            return a or b
   

def create_exp_tree(exp):
    
    __current_node = None

    
    char_index=0
    state="0"
    isvar=False
    operator_temp=''
    operand_temp=''
    found=False
    passthis=False
    while char_index<len(exp): #For every character in the expression

        for rule in exp_rules: #Search through all the rules
            if ((state==rule[0]) and ((rule[1] in ['any','other']) or (exp[char_index] in rule[1]))): #if the m
                found=True
                state=rule[2]
                if rule[3]=='operatorpush':
                    operator_temp+=exp[char_index]
                if rule[3]=='operandpush':
                    operand_temp+=exp[char_index]
                if rule[3]=='varpush':
                    isvar=True
                    operand_temp+=exp[char_index]
                if rule[3]=='pass':
                    passthis=True
                    
                if rule[4]=='ob':
                    if __current_node==None: #Check if this is the first node
                        __current_node=node(None) #If yes create one and make this current node
                    else: 
                        if (__current_node.left==None): #Check if already an element present in left
                            __current_node.left = node(__current_node) #Create a new node and assign left
                            __current_node = __current_node.left #And make this current node
                        elif (__current_node.right==None):
                            #Assign operator
                            if operator_temp!='':
                                __current_node.operator=operator_temp
                                operator_temp=''
                            __current_node.right = node(__current_node) #Create a new node and assign right
                            __current_node = __current_node.right #And make this current node
                if rule[4]=='cb':
                    if operand_temp!='':
                        __current_node.right=operand_temp
                        if isvar:
                            __current_node.right_type="var"
                            isvar=None
                    if __current_node.parent!=None:
                        __current_node=__current_node.parent
                    operand_temp=''
                if rule[4]=='operator':
                    __current_node.operator=operator_temp
                    operator_temp=''
                if rule[4]=='operand':
                    if operand_temp!='':
                        if __current_node.left==None:
                            __current_node.left=operand_temp
                            if isvar:
                                __current_node.left_type="var"
                                isvar=None
                            operand_temp=''
                        else:
                            __current_node.right=operand_temp
                            if isvar:
                                __current_node.right_type="var"
                                isvar=None
                            operand_temp=''
                if rule[4]=='string':
                    if operand_temp!='':
                        if __current_node.left==None:
                            __current_node.left=operand_temp
                            if isvar:
                                __current_node.left_type="var"
                                isvar=None
                            __current_node.left_type="str"
                            operand_temp=''
                        else:
                            __current_node.right=operand_temp
                            if isvar:
                                __current_node.right_type="var"
                                isvar=None
                            __current_node.right_type="str"
                            operand_temp=''
                if rule[4]=='opandop':
                    if operator_temp!='':
                        __current_node.operator=operator_temp
                        operator_temp=''
                    if operand_temp!='':
                        if __current_node.left==None:
                            __current_node.left=operand_temp
                            if isvar:
                                __current_node.left_type="var"
                                isvar=None
                        else:
                            __current_node.right=operand_temp
                            if isvar:
                                __current_node.right_type="var"
                                isvar=None
                        operand_temp=''
                    
                break
        if not found:
            raise sqlerror(-3,"Unexpected character "+exp[char_index]+" on where clause")
        else:
            found=False
        if passthis:
            passthis=False
        else:
            char_index+=1
    return __current_node
    
def evalthis(__current_node,title,value): ########RECURSIVE########
    if __current_node==None: #No expression present in the query
        return True;
    if isinstance(__current_node.left,node):
        evalthis(__current_node.left,title,value)
        a=__current_node.left.result
    else:
        a=__current_node.left
    op=__current_node.operator
    #Check the extra paranthesis
    if (__current_node.operator==None) and (__current_node.right==None):
        __current_node.result=__current_node.left.result
        return __current_node.result
    else:
        if isinstance(__current_node.right,node):
            evalthis(__current_node.right,title,value)
            b=__current_node.right.result
        else:
            b=__current_node.right
    #Substitute values in variables before calculating
    if __current_node.left_type=="var":
        if str(a) in title:
            __index=title.index(str(a))
            if (__index>=0) and (__index<len(value)):
                a=str(value[__index])
            else:
                raise sqlerror(-12,"Value for variable "+str(a)+" is missing in atleast one row")
        else:
            raise sqlerror(-11,"No field "+str(a)+" found in header")
    if __current_node.right_type=="var":
        if str(b) in title:
            __index=title.index(str(b))
            if (__index>=0) and (__index<len(value)):
                b=str(value[__index])
            else:
                raise sqlerror(-12,"Value for variable "+str(b)+" is missing in atleast one row")
        else:
            raise sqlerror(-11,"No field "+str(b)+" found in header")
    
    __current_node.result=calculate(a,op,b,__current_node.left_type,__current_node.right_type)
    return __current_node.result
