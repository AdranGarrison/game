__author__ = 'Alan'

import random



MNames_order1={}
MNames_order2={}
FNames_order1={}
FNames_order2={}


def load(table,file,order):
    lines=file.readlines()
    for string in lines:
        string=string.replace('\n','')
        for i in range(len(string)-order):
            if i+order<len(string):
                table.setdefault(string[i:i+order],[])
                table[string[i:i+order]]+=string[i+order]



def generate_first_name(table_order2,table_order1,startletter=None,maxlength=12):
    if startletter is None:
        name=random.choice(list(table_order2.keys()))
        while name.capitalize()!=name:
            name=random.choice(list(table_order2.keys()))
    else:
        name=startletter
    for i in range(0,maxlength):
        try:
            name+=random.choice(table_order2[name[-2:]])
        except KeyError:
            try:
                name+=random.choice(table_order1[name[-1:]])
            except KeyError:
                pass
    name=name.replace(',','')
    if len(name)<3:
        name=generate_first_name(table_order2,table_order1,startletter=startletter,maxlength=maxlength)
    return name

    pass


file=open('./Data/MaleNames.txt')
load(MNames_order2,file,2)
load(MNames_order1,file,1)
file.close()
file=open('./Data/FemaleNames.txt')
load(FNames_order2,file,2)
load(FNames_order1,file,1)
file.close()

def loadlastnames():
    '''
    All words in the files will be tagged in the files as follows:

    + for positive attribute (generally for names given by allies)
    - for negative attribute (generally for names given by enemies)
    ^ for adjectives which can be used in the syntax 'the ^adjective^'
    # for nouns which can be used in the syntax of 'the #noun#'
    % for words which can be used in the syntax of 'the #noun# of (the) %word%(s)'

    '''
    dict={}
    LastNamesPost=[]
    LastNamesPre=[]
    Descriptors=[]
    file=open('./Data/Adjectives.txt')
    Pre=file.readlines()
    file.close()

    file=open('./Data/Nouns.txt')
    Post=file.readlines()
    Pre.extend(Post)
    file.close()

    file=open('./Data/NameSuffix.txt')
    Post.extend(file.readlines())
    file.close()

    for i in Pre:
        new=i.replace('\n','')
        if '^' in new:
            new=new.replace('^','')
            Descriptors.append(new)
        LastNamesPre.append(new)

    for i in Post:
        LastNamesPost.append(i.replace('\n',''))

    dict['first']=LastNamesPre
    dict['last']=LastNamesPost
    dict['descriptors']=Descriptors

    return dict

namedict=loadlastnames()




def generate_last_name(LastNamesPre,LastNamesPost):
    sep=''
    first=random.choice(LastNamesPre)
    last=random.choice(LastNamesPost)
    while first in last or last in first:
        print('whoops!')
        first=random.choice(LastNamesPre)
        last=random.choice(LastNamesPost)
    name=sep.join([first,last])
    name=name.capitalize()
    return name



def namegen(nametype,title=False):
    if nametype=='m':
        firstname=generate_first_name(MNames_order2,MNames_order1)
    elif nametype=='f':
        firstname=generate_first_name(FNames_order2,FNames_order1)
    lastname=generate_last_name(namedict['first'],namedict['last'])
    sep=''
    name=sep.join([firstname,' ',lastname])
    if title==True:
        name=sep.join([name,' the ',random.choice(namedict['descriptors'])])
    return name



for i in range(0,100):
    print(namegen('f',title=True))

