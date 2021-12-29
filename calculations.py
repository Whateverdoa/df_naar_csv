import itertools
from pathlib import Path
import pandas as pd


from openpyxl import load_workbook
import xlrd
import xlwt

# oplossing voor uitgevulde nummers met voorloop nul is
# f"{getal:>{0}{posities}}"

from icecream import ic



def wikkel_formule():
    def wikkel(Aantalperrol, formaat_hoogte, kern=76):
        """importing in a function?"""
        import math

        pi = math.pi
        # kern = 76  # global andere is 40
        materiaal = 145  # global var
        var_1 = int(
            math.sqrt(
                (4 / pi) * ((Aantalperrol * formaat_hoogte) / 1000) * materiaal
                + pow(kern, 2)
            )
        )
        wikkel = int(2 * pi * (var_1 / 2) / formaat_hoogte + 2)
        return wikkel

    return wikkel


de_uitgerekenende_wikkel = wikkel_formule()


def begin_eind_dataframe(df_rol):
    """geeft begin van file, eind van file en aantal van file in tuple format"""

    begin = df_rol.iat[0, 0]
    beg = df_rol.iloc[0, 0]
    einde, kolommen = df_rol.shape
    eind_positie_rol = einde - 1
    eind = df_rol.iat[eind_positie_rol, 0]

    return (begin, eind, einde)


def taal_sluitetiket():
    # rolnummer komt uit enumarate
    # nummer omzetten in string
    def taal(dataframe_rol, taal, rolnummer, posities):
        # posities if  len(lijst)>= 10 dan 2 100 = 3 etc zie plb2020 of num generator

        rol_nummer = f"{rolnummer + 1:>{0}{posities}}"
        begin, eind, aantal = begin_eind_dataframe(dataframe_rol)

        if taal == "nl":
            sluitetiket = (
                f"Rol {rol_nummer} | {begin} - {eind} | {aantal} etiketten"
            )
            return sluitetiket
        if taal == "de":
            sluitetiket = (
                f"Rolle {rol_nummer} | {begin} - {eind} | {aantal} stück"
            )
            return sluitetiket

    return taal


language = taal_sluitetiket()

def headers_for_totaal_kolommen(dataframe_rol, mes):
    df_rol_kolommen_lijst = dataframe_rol.columns.to_list()
    count = 1
    kolom_naam_lijst_naar_mes = []
    for _ in range(mes):
        for kolomnaam in df_rol_kolommen_lijst:
            # print(kolomnaam, count)
            header = f"{kolomnaam}_{count}"
            kolom_naam_lijst_naar_mes.append(header)
        count += 1

    return kolom_naam_lijst_naar_mes


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


testdf = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\test_excel\202124565 Geisha standaard.xlsx')
testdf7 = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\test_excel\202124565 Geisha per 7 art.xlsx')
test_mouthaan = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\test_excel\202170964 verzameld v proef als geisha.xlsx')
test_engelvaartwibra = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\test_excel\202177773.xlsx')


def rol_cq_regel_uitwerker(regel, wikkel, posities_sluitbarcode=8, extra_etiketten =5):
    """maakt een dataframe van de regel met kolommen uit df
     of 3 standaard kolommen
     volgens mij heb ik er een generator van gemaakt en dat is een generator dataframe
     waar ik in kan slicen"""
    aantal = int(regel.aantal)  + int (extra_etiketten)
    artnummer = regel.Artnr
    columns = ["beeld", "omschrijving", "Artnr", "sluitbarcode"]

    # print(f'{regel.aantal =}')  # , regel.Artnr, regel.beeld, regel.ColorC

    rol_vulling = pd.DataFrame(
        [(f'{regel.beeld}', "", "",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")
         for x in range(aantal ) for i in range(1)], columns=columns)

    sluit = pd.DataFrame([('leeg.pdf',
                           f'{regel.Omschrijving} | {aantal} etiketten'
                           ,f'{aantal} etiketten'
                           ,f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")],
                         columns=columns)

    leeg = pd.DataFrame([('stans.pdf', "", "",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}") for x in range(wikkel) for i in range(1)],
                        columns=columns)

    samenstelling = pd.concat([leeg, sluit, rol_vulling, sluit, leeg])

    return samenstelling, aantal




def splitter_df(df_in, mes, aantalvdps=1 , extra_etiketten=5):
    kolomnamen = list(df_in.columns)

    aantal_rollen, kolommen = df_in.shape
    totaal = int(df_in.Aantal.sum())
    gemiddelde = totaal // (mes * aantalvdps)

    dataframe_lijst = []
    aantal_lijst = []
    for num, regel in enumerate(df_in.itertuples(), 1):

        dataframe_lijst.append(rol_cq_regel_uitwerker(regel, 1, extra_etiketten))
        aantal_lijst.append(rol_cq_regel_uitwerker(regel, 1)[1])
        print(num)
        som = sum(aantal_lijst)
        if som >= 1000:
            print(som,"STOP "*20)

    print(f'{aantal_lijst=}')

    return aantal_rollen, totaal, gemiddelde, kolomnamen
    # return dataframe_lijst


def dfbouwer(dfgenerator):
    nieuwe_df = []

    for rows in dfgenerator.itertuples():

        for i in range(int(rows.aantal)):
            # todo if else logic on rolnummer to build wikkel etc..
            nieuwe_df.append(rows)

    verwerkte_file_in = pd.DataFrame(nieuwe_df, dtype='string')

    return verwerkte_file_in


def splitter_df_2(df_in, mes, aantalvdps=1, sluitbarcode_posities=8, afwijking_waarde=0, wikkel=1, gemiddelde=None, extra_etiketten=5):
    """Deze splitter functie neemt een x aantal argumenten en maakt daar een x aantal banen voor benodigd
    voor het maken van de vdp.
    er moet een functie komen die check over teveel of te weining
    banen zijn en daarop kan reageren met overnieuw funktie toepassen of lege dummy baan toetevoegen"""

    kolomnamen = list(df_in.columns)

    aantal_rollen, kolommen = df_in.shape
    totaal = int(df_in.aantal.sum())
    if gemiddelde is None:
        gemiddelde = (totaal // (mes * aantalvdps)) - afwijking_waarde
    else:
        gemiddelde = gemiddelde - afwijking_waarde
    # gemiddelde = df_in.aantal.median()
    print(f'{gemiddelde = } met {afwijking_waarde}',f'{ aantal_rollen =}')

    dataframes_gesplitst=[]
    dataframe_lijst = []
    aantal_lijst = []

    for num, regel in enumerate(df_in.itertuples(index=0), 1):

        df_regel, df_regel_aantal = rol_cq_regel_uitwerker(regel, wikkel, sluitbarcode_posities, extra_etiketten)

        dataframe_lijst.append(df_regel)
        aantal_lijst.append((df_regel_aantal))


        som = sum(aantal_lijst)
        # eerste gedeelte wijst zichzelf is een itertuples() loop door de lijst.
        # het gelijk stellen van de teller aan de laatste rol
        # laadt hem in de dataframe_lijst.
        if som >= gemiddelde + afwijking_waarde or aantal_rollen == num:

            print(f'gemiddelde ={gemiddelde} som = {som} verschil = {som-gemiddelde}, STOP * {num} rollen in  file in dataframes_gesplitst__')
            dataframes_gesplitst.append(dataframe_lijst)
            dataframe_lijst=[]

            aantal_lijst = []

            continue

    return dataframes_gesplitst




def banen_in_vdp_check(aantalbanen, daadwerkelijk_gemaakte_banen):
    #todo dummy dfbaan maken
    if aantalbanen == daadwerkelijk_gemaakte_banen:
        print(" gaan ")
    else:
        if aantalbanen> daadwerkelijk_gemaakte_banen:
            print(f'{aantalbanen-daadwerkelijk_gemaakte_banen} te veel dus opnieuw berekenen')
        else:
            print(f'{daadwerkelijk_gemaakte_banen-aantalbanen} te weinig voeg lege baa(banen) toe')


def lijst_opbreker(lijst_in, mes_waarde, combi):
    start = 0
    end = mes_waarde
    combinatie_binnen_mes = []

    for combinatie in range(combi):
        # print(combinatie)
        combinatie_binnen_mes.append(lijst_in[start:end])
        start += mes_waarde
        end += mes_waarde

    return combinatie_binnen_mes




def headers_for_totaal_kolommen(dataframe_rol, mes):
    df_rol_kolommen_lijst = dataframe_rol.columns.to_list()
    count = 1
    kolom_naam_lijst_naar_mes = []
    for _ in range(mes):
        for kolomnaam in df_rol_kolommen_lijst:
            # print(kolomnaam, count)
            header = f"{kolomnaam}_{count}"
            kolom_naam_lijst_naar_mes.append(header)
        count += 1

    return kolom_naam_lijst_naar_mes


def filter_kolommen_pdf(mes, de_kolomnaam):
    # defenitie gekopieerd van
    # headers_for_totaal_kolommen()
    df_rol_kolommen_lijst = [de_kolomnaam]
    count = 1
    kolomnaam_vervang_waarde = []
    for _ in range(mes):
        for kolomnaam in df_rol_kolommen_lijst:
            # print(kolomnaam, count)
            header = f"{kolomnaam}_{count}"
            kolomnaam_vervang_waarde.append(header)
        count += 1
    return kolomnaam_vervang_waarde


def filna_dict(kolomnaam,vulling, mes):
    """"werkt. maar ga een dict comprehension proberen."""

    key = [f'{kolomnaam}_{count+1}'for count in range(mes)]
    value = [f'{vulling}'for count in range(mes)]
    filna_tobe_inserted = dict(zip(key,value))
    return filna_tobe_inserted


def inloop_uitloop_stans(df, wikkel, etiket_y, kolomnaam_vervang_waarde):
    # apr? laatstesluit? opbouw bewerken 3 sheets in en uit.
    # kan je 1 regel maken met generator en dat vermenigvuldigen met inloop waarde

    loop = (etiket_y * 10) - (wikkel +(3 * etiket_y))
    ic(wikkel)
    ic(loop)
    generator = df.itertuples(index=0)

    einde_df = len(df)
    ic(einde_df)
    data_df = []
    nieuwe_df = []

    sluitetiket = pd.DataFrame(
        [x for x in itertools.islice(generator, 2, 3)]
    )
    ic(sluitetiket)

    generator = df.itertuples(index=0)

    for seq in itertools.islice(generator, 0, 4):
        data_df.append(seq)

    data_df1 = pd.DataFrame(data_df)
    ic(data_df1)

    pdf_data_inloop_enuitloop_uit_iterslice = pd.DataFrame(
        [x for x in itertools.islice(generator, wikkel, wikkel + (3*etiket_y))]
    )
    ic(pdf_data_inloop_enuitloop_uit_iterslice.head())

    generator = df.itertuples(index=0)
    for seq in itertools.islice(generator, 3, loop):
        nieuwe_df.append(seq)
    inloopDF = pd.DataFrame(nieuwe_df)
    inloopDF[kolomnaam_vervang_waarde] = "stans.pdf"


    indat = pd.concat(
        [
            sluitetiket,
            pdf_data_inloop_enuitloop_uit_iterslice,
            # data_df1,

            inloopDF,
            df,
            inloopDF,
            # data_df1,

            pdf_data_inloop_enuitloop_uit_iterslice,
            sluitetiket,
        ]
    )
    indat.reset_index()
    return indat



