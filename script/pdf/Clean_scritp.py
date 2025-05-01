

def clean_scritp(txt_split):


    for i in range(len(txt_split)):
        try:
            if (txt_split[i][0]=='"') and (txt_split[i][-1]=='"'):

                txt_split[i] = txt_split[i][1:-1]
        except:
            pass

        try:
            if (txt_split[i][0]=='"') :

                txt_split[i] = txt_split[i][1:]
        except:
            pass

        try:
            if (txt_split[i][-2]=='"'):

                txt_split[i] = txt_split[i][:-2]
        except:
            pass

        try:
            if (txt_split[i][-1]==' '):

                txt_split[i] = txt_split[i][:-1]
        except:
            pass

        try:
            if (txt_split[i][2]=='o'):

                txt_split[i] = txt_split[i].replace('o  	','•  ')

        except:
            pass

        try:
            if (txt_split[i][4]=='.'):

                txt_split[i] = txt_split[i].replace('    .  ','  •  ')
        except:
            pass

        try:
            if (txt_split[i][2]=='•'):

                txt_split[i] = txt_split[i].replace('•  	','•  ')
        except:
            pass

        try:
            if (txt_split[i][0]=='•') and  (txt_split[i][1]!=' '):

                txt_split[i] = txt_split[i].replace('•','• ')
        except:
            pass

        try:
            if (txt_split[i][0]=='•'):

                txt_split[i] = txt_split[i].replace('•  	','•    ')
        except:
            pass

        try:
            if (txt_split[i][9]=='o'):

                txt_split[i] = txt_split[i].replace('         o ','         ○ ')
        except:
            pass

        try:
            if (txt_split[i][0]=='o'):

                txt_split[i] = txt_split[i].replace('o ','•')
        except:
            pass

        try:
            if (txt_split[i][0]=='-'):

                txt_split[i] = txt_split[i].replace('- ','•')
        except:
            pass

        try:
            if (txt_split[i][10]=='o'):

                txt_split[i] = txt_split[i].replace('         o	 ','        ○  ')
        except:
            pass

        try:
            if (txt_split[i][9]=='o'):

                txt_split[i] = txt_split[i].replace('        o	 ','        ○  ')
        except:
            pass

        try:
            if (txt_split[i][0]=='-'):
                txt_split[i] = txt_split[i].replace('-         ','►         ')
        except:
            pass

        try:
            if (txt_split[i][0]=='·'):
                txt_split[i] = txt_split[i].replace('·        ','►        ')
        except:
            pass

        try:
            if (txt_split[i][0]=='ü'):

                txt_split[i] = txt_split[i].replace('ü','✓')
        except:
            pass

    return txt_split

