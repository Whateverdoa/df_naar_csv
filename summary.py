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


def vdp_meters_uit_df_shape(df, formaat_hoogte):
    totaal, kolommen = df.shape
    meters = totaal * (formaat_hoogte + 3) / 1000
    return meters


def summary_splitter_df_2(df_in, mes, aantalvdps=1, sluitbarcode_posities=8, afwijking_waarde=0, wikkel=1, gemiddelde=None,
                  extra_etiketten=5):
    """Deze splitter functie is een copie van de splitter functie
    om een tuple lijst genereren [(0,50),50,100)]....
    die de gebruikte excel opsplitst in een summary"""

    kolomnamen = list(df_in.columns)
    baan_teller = 1
    start = 0

    aantal_rollen, kolommen = df_in.shape
    totaal_aantal = int(df_in.aantal.sum())
    gemiddelde = (totaal_aantal // (mes * aantalvdps)) + afwijking_waarde

    # if gemiddelde is None:
    #     gemiddelde = (totaal_aantal // (mes * aantalvdps)) - afwijking_waarde
    # else:
    #     gemiddelde = gemiddelde - afwijking_waarde
    # # gemiddelde = df_in.aantal.median()
    print(f'{gemiddelde = } met {afwijking_waarde}', f'{ aantal_rollen =}')#aantal_rollen

    summary_lijst = []
    slice_lijst = []
    aantal_lijst = []

    for num, regel in enumerate(df_in.itertuples(index=0), 1):

        df_regel, df_regel_aantal = rol_summary(df_in, regel, num)

        aantal_lijst.append((df_regel_aantal))
        summary_lijst.append(df_regel)

        som = sum(aantal_lijst)

        if som >= gemiddelde or aantal_rollen == num:
            beginslice = start
            eindslice = num
            start = num
            print(beginslice,eindslice)
            slice_lijst.append((beginslice,eindslice))
            aantal_lijst = []
            continue
    return slice_lijst


def df_sum_met_slice(de_te_gebruiken_dataframe, functie_splitter_tuple_lijst_maker, numvdp=1):
    ''''voorals nog moet aanwezig zijn: aantal', 'hoogte', 'Omschrijving', 'sluitbarcode', 'beeld'''
    """#todo gebruik gewoon dataframe slices"""
    slice = functie_splitter_tuple_lijst_maker
    banen = []
    kolommen = list(de_te_gebruiken_dataframe.columns)

    for slices in slice:
        baangenerator = de_te_gebruiken_dataframe.itertuples(index=0)
        beginslice = slices[0]
        eindslice = slices[1]
        print(slices, beginslice,eindslice)

        baan = [x for x in itertools.islice(baangenerator, beginslice, eindslice)]

        baandf = pd.DataFrame(baan)
        spec_cols=['aantal', 'Omschrijving', 'sluitbarcode', 'beeld'] #, 'hoogte'
        baandf_usespeccols = baandf[spec_cols]

        totaal = baandf.aantal.sum()
        #todo baan nummers
        header = pd.DataFrame([[f'{totaal} etiketten in baan', "Omschrijving",f"VDP_{numvdp}", "beeld", ] for x in range(1)], columns=spec_cols) #, "hoogte"
        #
        #
        banen.append(header)
        banen.append(baandf_usespeccols)



    samen = pd.concat(banen)
    #todo  maak de html_sum form writer zo dat ie een df maakt net de 4 noodzakelijke headers
    # samen.to_excel("sum2500.xlsx")
    return samen


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


def df_sum_form_writer(**kwargs):

    """user_designated_file_path, titel="summary",
     "build a df file for summary purposes with  *kwargv
     """
    for key, value in kwargs.items():
        print(key, value)

    # sum_dik = {key: value in kwargs.items()}
    sum_dik = {key: [key,value] for (key, value) in kwargs.items()}
    df_summary = pd.DataFrame.from_dict(sum_dik, orient="index")


    # naam_html_file = f"{user_designated_file_path}/{titel}.html"

    # with open(naam_html_file, "w") as f_html:
    #
    #     #         for key, value in kwargs.items():
    #     #             print(key, value)
    #
    #     print("<!DOCTYPE html>\n", file=f_html)
    #     print('<html lang = "en">\n', file=f_html)
    #     print("     <head>\n", file=f_html)
    #     print("<meta charset='UTF-8>'\n", file=f_html)
    #     # print(f"<title>{titel.capitalize()}</title>\n", file=f_html)
    #     print("     </head>", file=f_html)
    #     print("         <body>", file=f_html)
    #     for key, value in kwargs.items():
    #         print(f" <p><b>{key}</b> : {value}<p/>", file=f_html)
    #
    #     print("         </body>", file=f_html)
    #     print(" </html>", file=f_html)
    return df_summary
