import re

def dec_hex(num):
    return "0x"+'{:04x}'.format(int(num))

#remove LRU register and replace with new
def cache_entry(cache,var):
    if var in cache:
        cache.remove(var)
    cache.append(var)

def stor_reg(register,temp_var,var,reg_num,cache,tc,offset,current):
    if (reg_num==7):
        while cache[0] not in register:
            cache.pop(0)
        if current in var:
            if cache[0] in var: #store it into memory and load it so that it can be used 
                tc.append("SW $"+register[cache[0]]+" , "+offset[cache[0]]+"(0)")
            register[current]=register[cache[0]]
            tc.append("LW $"+register[current]+" , "+offset[current]+"(0)")
        else: 
            if cache[0] in var:
                tc.append("SW $"+register[cache[0]]+" , "+offset[cache[0]]+"(0)")
            register[current]=register[cache[0]]
        register.pop(cache[0])
        cache.pop(0)
    else:
        reg_num = reg_num + 1
        register[current]="t"+str(reg_num)
        if current in var:
            tc.append("LW $"+register[current]+" , "+offset[current]+"(0)")
    return reg_num

fin = open("input_tar.txt",'r')
data = fin.readlines()
intermediate = [x.strip('\n').split(' ') for x in data]
notnum = []
temp_var=set()
labels = set()
for line in intermediate:
    for word in line:
        match = re.search("^(?!T|L|[0-9])[a-zA-Z]+[0-9]*$",str(word))
        temp = re.search("[T][0-9]+",str(word))
        lab = re.search("[L][0-9]+(?<!:)$",str(word))
        if match is not None:
            notnum.append(word)
        elif temp is not None:
            temp_var.add(word)
        elif lab is not None:
            labels.add(word)


variables = set(filter((lambda x: x!='if' and x!='not' and x!='goto' and x!='Input' and x!='Accepted'),notnum))
register = dict()
offset = dict()
cache = []
reg_num = 0
print(".data")
addr = 0
for var in variables:
    print(dec_hex(addr)+" "+var)
    addr = addr+32
print("\n.text")
tc = []
i = 0
for var in variables:
    if var not in offset:
        offset[var]=str(4*i)
        i = i + 1
        #reg_num = reg_num + 1
    #tc.append("LW $"+register[var]+","+offset[var]+"(0)")

for command in intermediate:
    #print("#"+" ".join(x for x in command))
    if len(command)==1:
        tc.append(command[0])
    elif len(command)==2:
        if command[0]=="goto":
            tc.append("J "+command[1])
        elif command[1]=="Accepted":
            tc.append("$END")
    elif len(command)==3: #assignments 
        #print(command) #register: reg {'a': 't1', 'b': 't2', 'T3': 't3'}
        if command[0] not in register:
            reg_num = stor_reg(register,temp_var,variables,reg_num,cache,tc,offset,command[0])
        if command[2].isnumeric(): #IN CASE ONE of the operands is a number , then you assign it to the temp b
            #by adding to zero and then you store in memory
            tc.append("ADDI $"+register[command[0]]+" , $zero , "+dec_hex(int(command[2])))
            tc.append("SW $"+register[command[0]]+" , "+offset[command[0]]+"(0)")
            cache_entry(cache,command[0]) 
        else: #else if both registers it adds the value of the register to the main register 
            tc.append("ADDI $"+register[command[0]]+" , $zero , $"+register[command[2]])
            tc.append("SW $"+register[command[0]]+" , "+offset[command[0]]+"(0)")
            cache_entry(command[2])
            cache_entry(cache,command[0])
    elif len(command)==4:
        #for if-goto statements and NOT statements
        #['T4', '=', 'not', 'T3']
        #['if', 'T4', 'goto', 'L1']
        # Example of cond : ['>',dest, op1, op2]
        if 'if' in command and 'goto' in command: #if both are numeric, assign register to them, add zero 
            if cond[2].isnumeric() and cond[3].isnumeric():
                register["temp1"]="t"+str(reg_num)
                reg_num = reg_num+1
                tc.append("ADDI $"+register["temp1"]+" , $zero , "+dec_hex(cond[2]))
                cond[2]="temp1" # replace the operands with the name temp
                register["temp2"]="t"+str(reg_num)
                tc.append("ADDI $"+register["temp2"]+" , $zero , "+dec_hex(cond[3]))
                cond[3]="temp2"
            elif cond[3].isnumeric(): #if one of the operands is numeric
                register["temp2"]="t"+str(reg_num)
                tc.append("ADDI $"+register["temp2"]+" , $zero , "+dec_hex(cond[3]))
                cond[3]="temp2"
                cache_entry(cache,cond[2])
            elif cond[2].isnumeric():
                register["temp1"]="t"+str(reg_num)
                tc.append("ADDI $"+register["temp1"]+" , $zero , "+dec_hex(cond[2]))
                cond[2]="temp1"
                cache_entry(cache,cond[3])
            else: 
                cache_entry(cache,cond[2])
                cache_entry(cache,cond[3])
            if (cond[0]=='>') or (cond[0]=='<' and 'not' in cond):
                tc.append("SLT $"+register[cond[1]]+" , $"+register[cond[2]]+" , $"+register[cond[3]])
                tc.append("BGTZ $"+register[cond[1]]+" , "+command[3])
            elif (cond[0]=='<') or (cond[0]=='>' and 'not' in cond):
                tc.append("SLT $"+register[cond[1]]+" , $"+register[cond[3]]+" , $"+register[cond[2]])
                tc.append("BGTZ $"+register[cond[1]]+" , "+command[3])
            elif (cond[0]=='==') or (cond[0]=='!=' and 'not' in cond):
                tc.append("BEQ $"+register[cond[2]]+" , $"+register[cond[3]]+" , "+command[3])
            elif (cond[0]=='!=') or (cond[0]=='==' and 'not' in cond):
                tc.append("BNE $"+register[cond[2]]+" , $"+register[cond[3]]+" , "+command[3])
            cache_entry(cache,cond[1])
            if "temp1" in register and "temp2" in register:
                reg_num = reg_num - 1 #why reduce by 1?????
            if "temp1" in register: #remove the temps from the register 
                register.pop("temp1") 
            if "temp2" in register:
                register.pop("temp2")    
        elif 'not' in command:
            cond.append('not')
    elif len(command)==5:
        '''
        ['T3', '=', 'a', '>', 'b']
        ['T7', '=', 'x', '>', '20']
        ['T11', '=', 'a', '>', 'b']
        ''' 
        if command[0] not in register: #if a register has not been assigned to the first element then store
            reg_num = stor_reg(register,temp_var,variables,reg_num,cache,tc,offset,command[0])
        if command[3] in ['+','-','*','/']: #for all arithmatic operations
            #first we check that these variables are present in the variable list 
            if (command[2] in variables or command[2] in temp_var) and (command[4] in variables or command[4] in temp_var):
                if command[3]=='+': #then write the MIPS command 
                    tc.append("ADD $"+register[command[0]]+" , $"+register[command[2]]+" , $"+register[command[4]])
                elif command[3]=='-':
                    tc.append("SUB $"+register[command[0]]+" , $"+register[command[2]]+" , $"+register[command[4]])
                elif command[3]=='*':
                    tc.append("MUL $"+register[command[0]]+" , $"+register[command[2]]+" , $"+register[command[4]])
                elif command[3]=='/':
                    tc.append("DIV $"+register[command[0]]+" , $"+register[command[2]]+" , $"+register[command[4]])
                cache_entry(cache,command[2])
                cache_entry(cache,command[4])
                cache_entry(cache,command[0])
                
            else:
                if command[2].isnumeric():
                    if command[3]=='+':
                        tc.append("ADDI $"+register[command[0]]+" , $"+register[command[4]]+" , "+dec_hex(command[2]))
                    elif command[3]=='-':
                        tc.append("SUBI $"+register[command[0]]+" , $"+register[command[4]]+" , "+dec_hex(command[2]))
                    elif command[3]=='*':
                        tc.append("ADDI $t"+str(reg_num)+" , $zero , "+dec_hex(command[2]))
                        tc.append("MUL $"+register[command[0]]+" , $t"+str(reg_num)+" , $"+register[command[4]])
                    elif command[3]=='/':
                        tc.append("ADDI $t"+str(reg_num)+" , $zero , "+dec_hex(command[2]))
                        tc.append("DIV $"+register[command[0]]+" , $t"+str(reg_num)+" , $"+register[command[4]])
                    cache_entry(cache,command[4])
                    cache_entry(cache,command[0])
                else:
                    if command[3]=='+':
                        tc.append("ADDI $"+register[command[0]]+" , $"+register[command[2]]+" , "+dec_hex(command[4]))
                    elif command[3]=='-':
                        tc.append("SUBI $"+register[command[0]]+" , $"+register[command[2]]+" , "+dec_hex(command[4]))
                    elif command[3]=='*':
                        tc.append("ADDI $t"+str(reg_num)+" , $zero , "+dec_hex(command[4]))
                        tc.append("MUL $"+register[command[0]]+" , $t"+str(reg_num)+" , $"+register[command[2]])
                    elif command[3]=='/':
                        tc.append("ADDI $t"+str(reg_num)+" , $zero , "+dec_hex(command[2]))
                        tc.append("DIV $"+register[command[0]]+" , $t"+str(reg_num)+" , $"+register[command[2]])
                    cache_entry(cache,command[2])
                    cache_entry(cache,command[0])
        #if it is a conditional operator then append to a list the condiiton, dest, operand1, operand2
        elif command[3]=='>':
            cond = ['>',command[0],command[2],command[4]]
        elif command[3]=='<':
            cond = ['<',command[0],command[2],command[4]]
        elif command[3]=='==':
            cond = ['==',command[0],command[2],command[4]]
        elif command[3]=='!=':
            cond = ['!=',command[0],command[2],command[4]]
        if command[0] in variables: #update the new value of the destination in memory
            tc.append("SW $"+register[command[0]]+" , "+offset[command[0]]+"(0)")

#reduces the number of stores 
stores = []
loads = []
print(tc[::-1])
for command in tc[::-1]:
    parts = command.split()
    if parts[0]=="SW":
        if command not in stores:
            stores.append(command) #unless loaded from memory, you dont need to keep storing the same variable into memory bc hasnt changed 
        elif command in stores and parts[1] in loads:
            stores.append(command)
            loads.remove(parts[1])
    elif parts[0]=="LW": #appends all the registers used 
        loads.append(parts[1])
        stores.append(command)
    else: 
        stores.append(command)
for command in stores[::-1]:
    if len(command.split())>1 or command.split()[0]=="$END":
        print(command)
    else:
        print(command,end=' ')
            




                
                



