from fpdf import FPDF
from script.pdf.Clean_scritp import clean_scritp


class PDF(FPDF):
    def header(self):
        # Logo
        self.image("/data/copie_windows/version Windows alix02/Desktop/ALIX_APP/script/pdf/image/dq-legaltech-logo.png", 10, 8, 33)
        self.image("/data/copie_windows/version Windows alix02/Desktop/ALIX_APP/script/pdf/image/Iparme-logo.png", 185, 8, 20)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):

        # Position at 1.5 cm from bottom
        self.set_y(-19)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        self.set_text_color(r=0, g= 0, b = 0)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 1, 'C')
        self.cell(0, 10, 'Mise à jour en novembre 2021', 0, 0, 'L')
        self.cell(0, 10, '@ DROITS QUOTIDIENS LEGAL TECH', 0, 0, 'R')

def chapter_body(pdf,txt_split,context):


    # Read text file
    array_Space =['"Vous pouvez peut-être dès maintenant :','"Vous pouvez aussi organiser votre protection juridique future :','La loi vous offre d’autres possibilités :','Vous pouvez prendre dès maintenant l’initiative de mettre en place une mesure de protection juridique :']
    pdf.add_font('DejaVu', '', "/data/copie_windows/version Windows alix02/Desktop/ALIX_APP/script/pdf/DejaVuSansCondensed.ttf", uni=True)
    # Output justified text

    txt_split=clean_scritp(txt_split)

    for i in range(len(txt_split)):

        try:
            if i == 0:
                pdf.set_font('DejaVu', '', 11)
                pdf.cell(0, 5, txt_split[i][:-1], align='C')
                pdf.ln()
            elif i == 1:
                pdf.set_font('DejaVu', '', 11)
                pdf.set_text_color(r = 233, g= 18, b = 194)
                pdf.cell(0, 5, txt_split[i][:-1], align='C')
                pdf.ln()

            elif  txt_split[i][0:7] == 'seule +':
                print(context)
                txt=str(context)
                txt = txt.replace('[','')
                txt = txt.replace(']','')
                txt = txt.replace("'","")
                pdf.set_font('DejaVu', '', 8)
                pdf.set_text_color(r=0, g= 0, b = 0)
                pdf.multi_cell(0, 5,txt )

            elif txt_split[i][0:12] == 'Informations':
                pdf.set_font('DejaVu', '', 16)
                pdf.set_text_color(r = 0, g= 0, b = 0)
                pdf.multi_cell(0, 5, '__________________________________________________________________________')

                pdf.set_font('DejaVu', '', 10)
                pdf.set_text_color(r = 233, g= 18, b = 194)
                pdf.ln()
                pdf.cell(0, 5, txt_split[i][:-1], align='C')
                pdf.ln()
                pdf.ln()

            elif txt_split[i][0:7] == 'Comment':
                pdf.set_font('DejaVu', '', 10)
                pdf.set_text_color(r = 233, g= 18, b = 194)
                pdf.ln()
                pdf.cell(0, 5, txt_split[i][:-1], align='C')
                pdf.ln()
                pdf.ln()

            elif txt_split[i][0:8] == 'Pourquoi':
                pdf.set_font('DejaVu', '', 10)
                pdf.set_text_color(r = 233, g= 18, b = 194)
                pdf.ln()
                pdf.cell(0, 5, txt_split[i][:-1], align='C')
                pdf.ln()
                pdf.ln()


            elif  (txt_split[i][0:9] == 'Attention'):
                pdf.set_font('DejaVu', '', 6)
                pdf.set_text_color(r = 233, g= 18, b = 194)
                pdf.cell(0, 5, txt_split[i], align='C')
                pdf.ln()
                pdf.set_font('DejaVu', '', 16)
                pdf.set_text_color(r = 0, g= 0, b = 0)
                pdf.multi_cell(0, 5, '__________________________________________________________________________')
                pdf.ln()

            else:

                pdf.set_font('DejaVu', '', 8)
                pdf.set_text_color(r=0, g= 0, b = 0)

                try:
                    if txt_split[i] in array_Space:

                        pdf.ln()
                except:
                    pass

                pdf.multi_cell(0, 5, txt_split[i])

                try:
                    if (txt_split[i][0]=='•') and (txt_split[i+1][0]!='•') :
                        if (txt_split[i+1][9]!='○'):
                            pdf.ln()
                except:
                    pass

        except:
            pass



    return pdf



def Make_pdf(File_name,context):

    '''
    Cette fonction appellera les autres fonctions et créera un pdf à partir du fichier txt enregistré localement.

    '''

    with open(File_name, 'rb') as fh:
        txt = fh.read().decode('utf-8')
    # Times 12
    txt_split = txt.split("\n")
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    pdf = chapter_body(pdf,txt_split,context)

    return pdf
