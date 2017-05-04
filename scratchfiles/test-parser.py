import myconf
    
myconf.inty = 5

def sqr(inp):
    _i = int(inp)
    return (_i * _i)

def parse(com, inp):
    if (com == 'v'):
        # view
        myconf.inty = int(inp)
        return 'INTY SET TO ' + str(inp)

    elif (com == 's'):
        #square
        return parse('v',str(sqr(inp)))

    elif (com == 'i'):
        return parse('v',(inp))

    elif (com == 'l'):
        return 'STRING LENGTH: ' + str(len(inp))

    elif (com == 'r'):
        return 'INTY VAL IS ' + str(myconf.inty)

    elif (com == 'b'):
        comps = {'m': (0, 'EQ'), 'g': (-1, 'GT'), 'l': (1, 'LT')}

        comp_type = inp[0]
        comp_targ = int(inp[1])
        true_com  = inp[2:4]
        false_com = inp[4:6]

        feedback = 'COMPARE (' + comps[comp_type][1] + ' ' + str(comp_targ) + ')'
        feedback = feedback + 'True >> ' + true_com + ' ' + 'False >> ' + false_com
        
        if (myconf.inty.__cmp__(comp_targ) == comps[comp_type][0]):
            parse(true_com[0], true_com[1])
        else:
            parse(false_com[0], false_com[1])
        return feedback
           

inty = 0
commands = 'r i5 l7 r bg5v2v8 r v12 r s4 r v3 lANC'
for com in commands.split():
    print com + '\t' + str(parse(com[0], com[1:]))

