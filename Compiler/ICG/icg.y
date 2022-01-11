%{
  #include <stdio.h>
  #include <stdlib.h>
  #include <string.h>
  #include <ctype.h>
  int top=-1;
  void yyerror(char *);
  extern FILE *yyin;

%}

%start S
%token ID NUM T_lt T_gt T_lteq T_gteq T_neq T_noteq T_eqeq T_and T_or T_incr T_decr T_not T_eq WHILE INT CHAR FLOAT VOID H MAINTOK INCLUDE BREAK CONTINUE IF ELSE COUT STRING FOR ENDL T_ques T_colon DO

%token T_pl T_min T_mul T_div
%left T_lt T_gt
%left T_pl T_min
%left T_mul T_div

%%
S
      : START {printf("Input accepted.\n");}
      ;

START
      : INCLUDE T_lt H T_gt MAIN
      | INCLUDE "\"" H "\"" MAIN
      ;

MAIN
      : VOID MAINTOK BODY
      | INT MAINTOK BODY
      ;

BODY
      : '{' C '}'
      ;

C
      : C statement ';'
      | C LOOPS
      | statement ';'
      | LOOPS
      ;

LOOPS
      : WHILE {while1();} '(' COND ')'{while2();} '{' C '}' {while3();}
      | IF '(' COND ')' {if1();} '{' C '}' {if3();}
	| DO '{' C '}' WHILE '(' COND ')' ';' {do_while(); do_while2();} 
;



/*
LOOPBODY
  	  : '{' LOOPC '}'
  	  | ';'
  	  | statement ';'
  	  ;

LOOPC
      : LOOPC statement ';'
      | LOOPC LOOPS
      | statement ';'
      | LOOPS
      ;
*/
statement
      : ASSIGN_EXPR
      | EXP
      | PRINT statement
      ;





COND  : B {assign_4();}
      | B T_and{assign_4();} COND
      | B {assign_4();}T_or COND
      | T_not B{assign_4();}
      ;

B : V T_eq{push();}T_eq{push();} LIT
  | V T_gt{push();}F
  | V T_lt{push();}F
  | V T_not{push();} T_eq{push();} LIT
  |'(' B ')'
  | V {pushab();}
  ;

F :T_eq{push();}LIT
 |LIT
  ;

V : ID{push();};

ASSIGN_EXPR
      : LIT  T_eq {push();} EXP {codegen_assign();}
      | TYPE LIT  T_eq {push();} EXP {codegen_assign();}
      ;

EXP
	  : ADDSUB
	  | EXP T_lt {push();} ADDSUB {codegen();}
	  | EXP T_gt {push();} ADDSUB {codegen();}
	  ;
ADDSUB
      : TERM
      | ADDSUB T_pl {push();} TERM {codegen();}
      | ADDSUB T_min {push();} TERM {codegen();}
      ;

TERM
	  : FACTOR
      | TERM T_mul {push();} FACTOR {codegen();}
      | TERM T_div {push();} FACTOR {codegen();}
      ;

FACTOR
	  : LIT
	  | '(' EXP ')'
  	;

PRINT
      : COUT T_lt T_lt STRING ';'
      ;
LIT
      : ID {push();}
      | NUM {push();}
      ;
TYPE
      : INT
      | CHAR
      | FLOAT
      ;

%%

#include "lex.yy.c"
#include<ctype.h>
char st[100][100];

char i_[2]="0";
int temp_i=0;
char tmp_i[3];
char temp[2]="t";
int label[20];
int lnum=0;
int l_dwhile=0;
int ltop=0;
int abcd=0;
int l_while=0;
int l_for=0;
int flag_set = 1;

int main(int argc,char *argv[])
{

  yyin = fopen("input.cpp","r");
  if(!yyparse()) 
  {
    printf("Parsing Complete\n");
 
  }
  else
  {
    printf("Parsing failed\n");
  }

  fclose(yyin);
  return 0;
}

void yyerror(char *s)
{
  printf("Error :%s at %d \n",yytext,yylineno);
}

push()
{
strcpy(st[++top],yytext);
}
pusha()
{
strcpy(st[++top],"  ");
}

pushab()
{
strcpy(st[++top],"  ");
strcpy(st[++top],"  ");
strcpy(st[++top],"  ");
}
codegen()
{
	//for(int i=top; i>=0; i--)
	//	printf("GENCHECKK!! %s \n", st[i]);
    strcpy(temp,"T");
    sprintf(tmp_i, "%d", temp_i);
    strcat(temp,tmp_i);
    printf("%s = %s %s %s\n",temp,st[top-2],st[top-1],st[top]);
    top-=2;
    strcpy(st[top],temp);
    temp_i++;
}

assign_4()
{
//	for(int i=top; i>=0; i--)
//		printf("OTOPCHEKC!! %s \n", st[i]);
	strcpy(temp,"T");
	sprintf(tmp_i, "%d", temp_i);
	strcat(temp,tmp_i);
	printf("%s = %s %s %s\n",temp,st[top-2],st[top-1],st[top]);
	top-=4;
	temp_i++;
	strcpy(st[top],temp);
}

codegen_assign()
{
	//for(int i=top; i>=0; i--)
	//	printf("assssss!! %s \n", st[i]);

    printf("%s = %s\n",st[top-2],st[top]);
    top-=2;
}

if1()
{
 //lnum++;
 strcpy(temp,"T");
 sprintf(tmp_i, "%d", temp_i);
 strcat(temp,tmp_i);
 printf("%s = not %s\n",temp,st[top]);
 printf("if %s goto L%d\n",temp,lnum);

 temp_i++;
 label[++ltop]=lnum;
}

if3()
{
    int y;
    y=label[ltop--];
    printf("L%d: \n",y);
}


while1()
{

    l_while = lnum;
    printf("L%d: \n",lnum++);

}

while2()
{
//for( int i=top; i>=0; i--)
//	printf("randsss %s \n", st[i]);
 strcpy(temp,"T");
 sprintf(tmp_i, "%d", temp_i);
 strcat(temp,tmp_i);
 printf("%s = not %s\n",temp,st[top]);
    printf("if %s goto L%d\n",temp,lnum);
 temp_i++;
 }
while3()
{
//lnum+=1;
	printf("goto L%d \n",l_while);
    printf("L%d: \n",lnum++);
}
do_while()
{
l_dwhile=lnum;
lnum++;
 strcpy(temp,"T");
temp_i+=1;
 sprintf(tmp_i, "%d", temp_i);
 strcat(temp,tmp_i);
 printf("%s = not %s\n",temp,st[top]);
    printf("if %s goto L%d\n",temp,lnum);
 temp_i++;
 }

do_while2()
{
	printf("goto L%d \n",l_dwhile);
    printf("L%d: \n",lnum);
}


