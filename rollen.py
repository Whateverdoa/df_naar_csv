import pandas as pd

from summary import *

import itertools

def file_to_generator(file_in):
    """Builds from a workable csv or excel file a Dataframe
     on which to Generate with itertuples or ...."""

    if Path(file_in).suffix == ".csv":
        # extra arg = ";"or ","

        file_to_generate_on = pd.read_csv(file_in, ";")
        return file_to_generate_on

    elif Path(file_in).suffix == ".xlsx":
        # print(Path(file_in).suffix)
        file_to_generate_on = pd.read_excel(file_in, engine='openpyxl')
        return file_to_generate_on

    elif Path(file_in).suffix == ".xls":
        # print(Path(file_in).suffix)
        file_to_generate_on = pd.read_excel(file_in)
        return file_to_generate_on

def rol_cq_regel_uitwerker(regel, wikkel, posities_sluitbarcode=8, extra_etiketten =5):
    """maakt een dataframe van de regel met kolommen uit df
     of 3 standaard kolommen
     volgens mij heb ik er een generator van gemaakt en dat is een generator dataframe
     waar ik in kan slicen"""
    aantal = int(regel.aantal)  # overlevering?
    # artnummer = regel.Artnr
    columns = ["pdf", "omschrijving", "Artnr", "sluitbarcode"]

    # print(f'{regel.aantal =}')  # , regel.Artnr, regel.beeld, regel.ColorC

    rol_vulling = pd.DataFrame(
        [(f'{regel.beeld}', "", f"{regel.Artnr}", f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")
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





def overlevering():
    ...




def rol_beeld_is_pdf_uit_excel(regel,wikkel, posities_sluitbarcode=8, pdf_sluitetiket=True,extra_etiketten =5 ):

    """het idee is om de inputlijst completer te maken,
    sluitetiket is een pdf (DAN GEEN SLUITBARCODE NODIG IN LIJST)
    ,wikkel_formule kan worden toegepast op (hoogte x aantal)
    kolommen blijven identiek zodat het backwards compatible blijft
    """
    # columns = ["beeld", "omschrijving"]
    columns = ["pdf", "omschrijving", "Artnr", "sluitbarcode"]
    # print(f'{pdf_sluitetiket=}')

    aantal = int(regel.aantal) + extra_etiketten

    rol_vulling = pd.DataFrame(
        [(f'{regel.beeld}', "",f"{regel.Artnr}",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")
         for x in range(aantal) for i in range(1)], columns=columns)

    if pdf_sluitetiket is True:

        sluitetiket =  pd.DataFrame(
            [(f'{regel.sluitbeeld}', "","",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")
             for x in range(1) for i in range(1)], columns=columns)
    else:
        sluitetiket =  pd.DataFrame(
            [("leeg.pdf", f'{regel.Omschrijving} |  {regel.aantal} etiketten',"",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")
             for x in range(1) for i in range(1)], columns=columns)

    wikkel_om_rol = pd.DataFrame(
        [('stans.pdf', "","",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}") for x in range(wikkel) for i in
         range(1)],
        columns=columns)

    rol = pd.concat([wikkel_om_rol,

                     sluitetiket,
                     rol_vulling,
                     sluitetiket,

                    ])

    return rol, regel.aantal


def dummy_rol_is_baan(regel,gemiddelde_aantal,pdf_sluitetiket=True):
    columns = ["pdf", "omschrijving", "Artnr", "sluitbarcode"]

    aantal = gemiddelde_aantal

    if pdf_sluitetiket != True:

        rol_vulling = pd.DataFrame(
            [(f'{regel.beeld}', "dummy_Baan", "", 0)
             for x in range(aantal) for i in range(1)], columns=columns)
        return 0

    else:
        rol_vulling = pd.DataFrame(
            [(f'{regel.beeld}', "dummy_BAAN", "", 0)
             for x in range(aantal) for i in range(1)], columns=columns)
        return 0



# rolstandaardtest= file_to_generator(r"C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\rollen\standaard_aanlever_excel.xlsx")
# # rolstandaardtest= file_to_generator(r"C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\rollen\202175361 85x35 veelvoud rv1000_verveel_vuldigd_.xlsx")
# # rolstandaardtest= file_to_generator(r"C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\rollen\202175361 85x35 veelvoud rv2500_verveel_vuldigd_.xlsx")
# excel_in_dataframe = rolstandaardtest.itertuples(index=0)
# regel1 = [x for x in itertools.islice(excel_in_dataframe,0,1)]

# baan= []
# for regel in excel_in_dataframe:
#     baan.append(rol_beeld_is_pdf_uit_excel(regel,wikkel=2,overlevering=5))
#     print(rol_beeld_is_pdf_uit_excel(regel,1).head(3))
#     print(regel.aantal)


def rol_summary(regel, num):
    '''draait mee in de splitter2
    mischien zelfs tijn om async te proberen'''
    columns = ["VDP","pdf", "omschrijving","aantal"]

    summary_rol= pd.DataFrame(
        [("",f'{regel.beeld} | rol {num}' , f'{regel.omschrijving}, {regel.aantal} etiketten') for x in range(1)]
    ) #,columns=columns
    return summary_rol


# slice = summary_splitter_df_2(rolstandaardtest,8,10)
# baangenerator = rolstandaardtest.itertuples(index=0)
# kolommen = list(rolstandaardtest.columns)







