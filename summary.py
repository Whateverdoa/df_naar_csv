import itertools
from pathlib import Path
import pandas as pd
from icecream import ic


columns = ["beeld", "omschrijving","aantal"]

def rol_summary(df_in, regel, num):
    '''draait mee in de splitter2
    mischien zelfs tijn om async te proberen'''
    columns = ["beeld", "omschrijving","aantal"]
    # columns = list(df_in.columns)

    aantal = regel.aantal

    summary_rol= pd.DataFrame(
        [(f'{regel.beeld} | rol {num}' , f'{regel.Omschrijving}', f'{regel.aantal} etiketten') for x in range(1)]
     ,columns=columns)
    # summary_rol= regel
    return summary_rol, aantal


def summary_splitter_df_2(df_in, mes, aantalvdps=1, sluitbarcode_posities=8, afwijking_waarde=0, wikkel=1, gemiddelde=None,
                  extra_etiketten=5):
    """Deze splitter functie neemt een x aantal argumenten en maakt daar een x aantal banen voor benodigd
    voor het maken van de vdp.
    er moet een functie komen die check over teveel of te weining
    banen zijn en daarop kan reageren met overnieuw funktie toepassen of lege dummy baan toetevoegen"""

    kolomnamen = list(df_in.columns)
    baan_teller = 1
    start = 0

    aantal_rollen, kolommen = df_in.shape
    totaal = int(df_in.aantal.sum())
    if gemiddelde is None:
        gemiddelde = (totaal // (mes * aantalvdps)) - afwijking_waarde
    else:
        gemiddelde = gemiddelde - afwijking_waarde
    # gemiddelde = df_in.aantal.median()
    print(f'{gemiddelde = } met {afwijking_waarde}', f'{ aantal_rollen =}')

    dataframes_gesplitst = []
    dataframe_lijst = []
    slice_lijst = []
    # summarylijst
    summary_lijst_gesplitst = []
    summary_lijst = []
    slice_lijst = []
    aantal_lijst = []

    for num, regel in enumerate(df_in.itertuples(index=0), 1):

        df_regel, df_regel_aantal = rol_summary(df_in, regel, num)


        aantal_lijst.append((df_regel_aantal))
        summary_lijst.append(df_regel)

        som = sum(aantal_lijst)
        # eerste gedeelte wijst zichzelf is een itertuples() loop door de lijst.
        # het gelijk stellen van de teller aan de laatste rol
        # laadt hem in de dataframe_lijst.

        if som >= gemiddelde + afwijking_waarde or aantal_rollen == num:
            # print(
            #     f'gemiddelde ={gemiddelde} som = {som} verschil = {som - gemiddelde}, STOP * {num} rollen in  file in dataframes_gesplitst__')
            # header = pd.DataFrame([(f'Baan_{baan_teller}',f'gemiddelde ={gemiddelde} som = {som} verschil = {som - gemiddelde}',f'totaal {som}') for x in range(1)], columns = columns)
            # # summary_lijst_gesplitst.append([header])
            # # summary_lijst_gesplitst.append(summary_lijst)
            # summary_lijst_gesplitst.append([header]+summary_lijst)
            # summary_lijst = []

            beginslice = start
            eindslice = num
            start = num
            print(beginslice,eindslice)
            slice_lijst.append((beginslice,eindslice))

            # baangenerator = df_in.itertuples(index=0)
            #
            # baan= [x for x in itertools.islice(baangenerator,beginslice,eindslice)]
            #
            # ic(baan[0])
            #
            # banen=[]
            # samen=[]
            # for regel in baan:
            #     print(regel.aantal,regel.Omschrijving,regel.beeld)
            #
            #     rol = pd.DataFrame([(f'{regel.aantal}', regel.Omschrijving, regel.beeld) for x in range(1)],
            #                      columns=["aantal", "omschrijving", "beeld"])
                # ic(type(rol))

            aantal_lijst = []
            continue



    return slice_lijst




def html_sum_form_writer(user_designated_file_path, titel="summary", **kwargs):
    """ "build a html file for summary purposes with  *kwargv
    search jinja and flask
    css link toevoegen
    """
    for key, value in kwargs.items():
        print(key, value)

    naam_html_file = f"{user_designated_file_path}/{titel}.html"
    with open(naam_html_file, "w") as f_html:

        #         for key, value in kwargs.items():
        #             print(key, value)

        print("<!DOCTYPE html>\n", file=f_html)
        print('<html lang = "en">\n', file=f_html)
        print("     <head>\n", file=f_html)
        print("<meta charset='UTF-8>'\n", file=f_html)
        # print(f"<title>{titel.capitalize()}</title>\n", file=f_html)
        print("     </head>", file=f_html)
        print("         <body>", file=f_html)
        for key, value in kwargs.items():
            print(f" <p><b>{key}</b> : {value}<p/>", file=f_html)

        print("         </body>", file=f_html)
        print(" </html>", file=f_html)
