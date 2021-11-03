from pathlib import Path
import pandas as pd


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


testdf = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\202124565 Geisha.xlsx')
testdf7 = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\202124565 Geisha per 7 art.xlsx')


def regel_uitwerker(regel, wikkel):
    """maakt een dataframe van de regel met kolommen uit df
     of 3 standaard kolommen
     volgens mij heb ik er een generator van gemaakt en dat is een generator dataframe
     waar ik in kan slicen"""
    aantal = int(regel.Aantal)  # overlevering?
    artnummer = regel.Artnr

    print(f'{regel.Aantal=}')  # , regel.Artnr, regel.beeld, regel.ColorC

    a = pd.DataFrame(
        [(f'{regel.beeld}', "", f'{regel.Artnr}||{regel.ColorN}||{regel.Size}')
         for x in range(aantal) for i in range(1)], columns=["beeld", "omschrijving", "Artnr"])

    sluit = pd.DataFrame([('sluit.pdf', f'{aantal} etiketten van {artnummer}||{regel.ColorN}||{regel.Size}', "")],
                         columns=["beeld", "omschrijving", "Artnr"])

    leeg = pd.DataFrame([('stans.pdf', "", "") for x in range(wikkel) for i in range(1)],
                        columns=["beeld", "omschrijving", "Artnr"])

    samenstelling = pd.concat([leeg, sluit, a, sluit, leeg])

    print(samenstelling.head(5))

    print(samenstelling.tail(5))
    # samenstelling.to_csv("test.csv")

    return samenstelling


def splitter_df(df_in, mes, aantalvdps=1):
    kolomnamen = list(df_in.columns)

    aantal_rollen, kolommen = df_in.shape
    totaal = int(df_in.Aantal.sum())
    gemiddelde = totaal // (mes * aantalvdps)

    dataframe_lijst = []

    for num, regel in enumerate(df_in.itertuples(), 1):
        dataframe_lijst.append(regel_uitwerker(regel, 1))
        print(num)

    return aantal_rollen, totaal, gemiddelde, kolomnamen
    # return dataframe_lijst


def dfbouwer(dfgenerator):
    nieuwe_df = []

    for rows in dfgenerator.itertuples():

        for i in range(int(rows.Aantal)):
            # todo if else logic on rolnummer to build wikkel etc..
            nieuwe_df.append(rows)

    verwerkte_file_in = pd.DataFrame(nieuwe_df, dtype='string')

    return verwerkte_file_in


