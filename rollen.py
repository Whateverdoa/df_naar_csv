import pandas as pd
from calculations import file_to_generator
from summary import *

import itertools

def rol_cq_regel_uitwerker(regel, wikkel, posities_sluitbarcode=8, extra_etiketten =5):
    """maakt een dataframe van de regel met kolommen uit df
     of 3 standaard kolommen
     volgens mij heb ik er een generator van gemaakt en dat is een generator dataframe
     waar ik in kan slicen"""
    aantal = int(regel.aantal)  # overlevering?
    # artnummer = regel.Artnr
    columns = ["beeld", "omschrijving", "Artnr", "sluitbarcode"]

    # print(f'{regel.aantal =}')  # , regel.Artnr, regel.beeld, regel.ColorC

    rol_vulling = pd.DataFrame(
        [(f'{regel.beeld}', "", "",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")
         for x in range(aantal) for i in range(1)], columns=columns)

    sluit = pd.DataFrame([('leeg.pdf',
                           f'{regel.Omschrijving} | {aantal} etiketten'
                           ,f'{aantal} etiketten'
                           ,f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")],
                         columns=columns)

    leeg = pd.DataFrame([('stans.pdf', "", "",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}") for x in range(wikkel) for i in range(1)],
                        columns=columns)

    samenstelling = pd.concat([leeg, sluit, rol_vulling, sluit, leeg])
    #
    # print(samenstelling.head(2))
    # #
    # print(samenstelling.tail(2))
    # samenstelling.to_csv("test.csv")
    return samenstelling, aantal




pdf_sluitetiket = True

def overlevering():
    ...




def rol_beeld_is_pdf_uit_excel(regel,wikkel, overlevering=0):
    """het idee is om de inputlijst completer te maken,
    sluitetiket is een pdf ,wikkel_formule kan worden toegepast op (hoogte x aantal)
    kolomen blijven identiek zodat het backwards compatible blijft
    """
    columns = ["beeld", "omschrijving"]


    aantal = int(regel.aantal) + overlevering

    rol_vulling = pd.DataFrame(
        [(f'{regel.beeld}', "")
         for x in range(aantal) for i in range(1)], columns=columns)

    if pdf_sluitetiket is True:

        sluitetiket =  pd.DataFrame(
            [(f'{regel.sluitbeeld}', "")
             for x in range(1) for i in range(1)], columns=columns)
    else:
        sluitetiket =  pd.DataFrame(
            [("leeg.pdf", f'{regel.omschrijving} |  {regel.aantal} etiketten')
             for x in range(1) for i in range(1)], columns=columns)

    wikkel_om_rol = pd.DataFrame(
        [('stans.pdf', "") for x in range(wikkel) for i in
         range(1)],
        columns=columns)

    rol = pd.concat([wikkel_om_rol,

                     sluitetiket,
                     rol_vulling,
                     sluitetiket,

                    ])

    return rol






rolstandaardtest= file_to_generator(r"C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\rollen\standaard_aanlever_excel.xlsx")
# rolstandaardtest= file_to_generator(r"C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\rollen\202175361 85x35 veelvoud rv1000_verveel_vuldigd_.xlsx")
rolstandaardtest= file_to_generator(r"C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\rollen\202175361 85x35 veelvoud rv2500_verveel_vuldigd_.xlsx")
excel_in_dataframe = rolstandaardtest.itertuples(index=0)
# regel1 = [x for x in itertools.islice(excel_in_dataframe,0,1)]

# baan= []
# for regel in excel_in_dataframe:
#     baan.append(rol_beeld_is_pdf_uit_excel(regel,wikkel=2,overlevering=5))
#     print(rol_beeld_is_pdf_uit_excel(regel,1).head(3))
#     print(regel.aantal)


def rol_summary(regel, num):
    '''draait mee in de splitter2
    mischien zelfs tijn om async te proberen'''
    columns = ["VDP","beeld", "omschrijving","aantal"]

    summary_rol= pd.DataFrame(
        [("",f'{regel.beeld} | rol {num}' , f'{regel.omschrijving}, {regel.aantal} etiketten') for x in range(1)]
    ) #,columns=columns
    return summary_rol


slice = summary_splitter_df_2(rolstandaardtest,8,10)
baangenerator = rolstandaardtest.itertuples(index=0)
kolommen = list(rolstandaardtest.columns)

banen=[]

for slices in slice:
    baangenerator = rolstandaardtest.itertuples(index=0)
    beginslice = slices[0]
    eindslice = slices[1]
    print(slices, beginslice,eindslice)

    baan = [x for x in itertools.islice(baangenerator, beginslice, eindslice)]

    baandf = pd.DataFrame(baan)
    spec_cols=['aantal', 'hoogte', 'Omschrijving', 'sluitbarcode', 'beeld']
    baandf_usespeccols = baandf[spec_cols]

    totaal = baandf.aantal.sum()

    header = pd.DataFrame([[f'{totaal} etiketten in baan', "hoogte", "Omschrijving", "sluitbarcode", "beeld"] for x in range(1)], columns=spec_cols)
    #
    #
    banen.append(header)
    banen.append(baandf_usespeccols)



samen = pd.concat(banen)
samen.to_excel("sum2500.xlsx")




