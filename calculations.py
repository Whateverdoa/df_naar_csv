import itertools
import math
from pathlib import Path
import pandas as pd
# from rollen import dummy_rol_is_baan
from rollen import rol_beeld_is_pdf_uit_excel,rol_cq_regel_uitwerker


import logging

from openpyxl import load_workbook
import xlrd
import xlwt

logger = logging.getLogger(__name__)


def bereken_vdp_aantal(total_labels, mes, max_meters_per_vdp, formaat_hoogte):
    """Bereken het aantal VDP's op basis van max meters per rol.

    Meters = rollengte (fysieke lengte, banen lopen parallel).
    labels_per_baan_max = max_meters * 1000 / (formaat_hoogte + 3)
    vdp_aantal = ceil(total_labels / (mes * labels_per_baan_max))
    """
    if max_meters_per_vdp <= 0:
        raise ValueError("max_meters_per_vdp must be greater than 0")
    labels_per_baan_max = max_meters_per_vdp * 1000 / (formaat_hoogte + 3)
    vdp_aantal = math.ceil(total_labels / (mes * labels_per_baan_max))
    return max(1, vdp_aantal)


def vdp_meters_uit_df_shape(df, formaat_hoogte):
    totaal, kolommen = df.shape
    meters = totaal * (formaat_hoogte + 3) / 1000
    return meters


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
    suffix = Path(file_in).suffix.lower()

    try:
        if suffix == ".csv":
            return pd.read_csv(file_in, sep=";")
        elif suffix == ".xlsx":
            return pd.read_excel(file_in, engine='openpyxl')
        elif suffix == ".xls":
            return pd.read_excel(file_in)
        else:
            logger.warning("Unsupported file format: %s", suffix)
            return None
    except FileNotFoundError:
        logger.error("File not found: %s", file_in)
        return None
    except Exception as e:
        logger.error("Failed to read file %s: %s", file_in, e)
        return None


# testdf = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\test_excel\202124565 Geisha standaard.xlsx')
# testdf7 = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\test_excel\202124565 Geisha per 7 art.xlsx')
# test_mouthaan = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\test_excel\202170964 verzameld v proef als geisha.xlsx')
# test_engelvaartwibra = file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\test_excel\202177773.xlsx')
# standaardtestfile =  file_to_generator(r'C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\rollen\standaard_aanlever_excel.xlsx')


def rol_cq_regel_uitwerker(regel, wikkel, posities_sluitbarcode=8, extra_etiketten =5):
    """maakt een dataframe van de regel met kolommen uit df
     of 3 standaard kolommen
     volgens mij heb ik er een generator van gemaakt en dat is een generator dataframe
     waar ik in kan slicen"""
    aantal = int(regel.aantal)  # + int (extra_etiketten)
    artnummer = regel.Artnr
    columns = ["pdf", "omschrijving", "Artnr", "sluitbarcode"]

    # print(f'{regel.aantal =}')  # , regel.Artnr, regel.beeld, regel.ColorC

    rol_vulling = pd.DataFrame(
        [(f'{regel.beeld}', "", "",f"{regel.sluitbarcode:>{0}{posities_sluitbarcode}}")
         for x in range(aantal + int (extra_etiketten)) for i in range(1)], columns=columns)

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
        logger.debug("splitter_df: num=%d", num)
        som = sum(aantal_lijst)
        if som >= 1000:
            logger.debug("splitter_df: som=%d STOP", som)

    logger.debug("splitter_df: aantal_lijst=%s", aantal_lijst)

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


def splitter_df_2(df_in,
                  mes,
                  aantalvdps=1,
                  sluitbarcode_posities=8,
                  afwijking_waarde=0,
                  wikkel=1,
                  gemiddelde=None,
                  extra_etiketten=5,
                  pdf_sluitetiket=False):
    """Deze splitter functie neemt een x aantal argumenten en maakt daar een x aantal banen voor benodigd
    voor het maken van de vdp.
    er moet een functie komen die check over teveel of te weining
    banen zijn en daarop kan reageren met overnieuw funktie toepassen of lege dummy baan toetevoegen"""

    kolomnamen = list(df_in.columns)

    aantal_rollen, kolommen = df_in.shape
    totaal_aantal = int(df_in.aantal.sum())
    gemiddelde = (totaal_aantal // (mes * aantalvdps)) + afwijking_waarde

    logger.debug("splitter_df_2: gemiddelde=%d afwijking=%d rollen=%d", gemiddelde, afwijking_waarde, aantal_rollen)

    dataframes_gesplitst = []
    dataframe_lijst = []
    aantal_lijst = []

    for num, regel in enumerate(df_in.itertuples(index=0), 1):

        # df_regel, df_regel_aantal = rol_cq_regel_uitwerker(regel, wikkel, sluitbarcode_posities, extra_etiketten)
        df_regel, df_regel_aantal = rol_beeld_is_pdf_uit_excel(regel, wikkel,  sluitbarcode_posities, pdf_sluitetiket, extra_etiketten=extra_etiketten)

        dataframe_lijst.append(df_regel)
        aantal_lijst.append((df_regel_aantal))


        som = sum(aantal_lijst)
        # eerste gedeelte wijst zichzelf is een itertuples() loop door de lijst.
        # het gelijk stellen van de teller aan de laatste rol
        # laadt hem in de dataframe_lijst.

        if som >= gemiddelde or aantal_rollen == num:

            logger.debug("Lane split: gemiddelde=%d som=%d verschil=%d rollen=%d", gemiddelde, som, som - gemiddelde, num)
            dataframes_gesplitst.append(pd.concat(dataframe_lijst, ignore_index=True))
            dataframe_lijst=[]

            aantal_lijst = []

            continue

    return dataframes_gesplitst




def banen_in_vdp_check(aantalbanen, daadwerkelijk_gemaakte_banen, aantal_vdps=1,mes_waarde=1):
    # # try except for value error ValueError: Length mismatch:

    #todo dummy dfbaan maken in splitter?
    if aantalbanen == daadwerkelijk_gemaakte_banen:
        logger.debug("banen_in_vdp_check: exact match, doorgaan")
        return True, 0, aantal_vdps
    elif aantalbanen > daadwerkelijk_gemaakte_banen:
        dummybanen = aantalbanen - daadwerkelijk_gemaakte_banen
        logger.info("banen_in_vdp_check: %d te weinig, maak %d dummybanen", dummybanen, dummybanen)
        return False, dummybanen, aantal_vdps
    else:
        logger.info("banen_in_vdp_check: meer VDPs nodig")
        aantal_vdps += 1
        dummybanen = (aantal_vdps * mes_waarde) - daadwerkelijk_gemaakte_banen
        return False, dummybanen, aantal_vdps


def dummy_rol_is_baan(regel,gemiddelde_aantal,pdf_sluitetiket=True):
    columns = ["beeld", "omschrijving", "Artnr", "sluitbarcode"]

    aantal = gemiddelde_aantal

    if pdf_sluitetiket != True:

        rol_vulling = pd.DataFrame(
            [(f'{regel.beeld}', "dummy_Baan", "", 0)
             for x in range(aantal) for i in range(1)], columns=columns)
        return rol_vulling

    else:
        rol_vulling = pd.DataFrame(
            [(f'{regel.beeld}', "dummy_BAAN", "", 0)
             for x in range(aantal) for i in range(1)], columns=columns)
        return rol_vulling


def maak_een_dummy_baan(dummy_baan_generator, gemiddelde, aantal_dummy_banen):
    """#todo maak een of meerdere baan(banen) waarin hel beeld stans.pdf is
    of maak van de hele invoer lijst banen met
    beeldd door stans vervangen en haal de benodigde banen  hieruit, te omslachtig
     gebruik generator zodat je de juiste headers hebt en gemiddelde
     voor de juiste waarden
         """
    kolomnamen = list(dummy_baan_generator.columns)
    logger.debug("dummy baan kolomnamen: %s", kolomnamen)
    # vervang beeld waarde voor stans.pdf of leeg.pdf
    dummy_baan_generator['beeld'] ="stans.pdf"
    dummy_baan_generator['sluitbeeld'] ="leeg.pdf"

    def bouwertje(generator,x):
        nieuwe_df=[]
        for rows in generator:
            for i in range(2):
                nieuwe_df.append([rows])

    # stap1 haal uit Dataframe  de regels voor de dummys # stap2 maak een nieuwe itertuples() hiermee
    db = dummy_baan_generator[0:aantal_dummy_banen].itertuples()
    logger.debug("maak_een_dummy_baan: %d dummy banen", aantal_dummy_banen)

    # verwerkte_file_in = pd.DataFrame(nieuwe_df)
    dummy_lijst_voor_baan=[dummy_rol_is_baan(regel,gemiddelde,pdf_sluitetiket=True) for regel in db]
    logger.debug("dummy baan columns: %s", dummy_lijst_voor_baan[0].columns)


    return  dummy_lijst_voor_baan, len(dummy_lijst_voor_baan)





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
    """"werkt. maar probeer een dict comprehension"""

    key = [f'{kolomnaam}_{count+1}'for count in range(mes)]
    value = [f'{vulling}'for count in range(mes)]
    filna_tobe_inserted = dict(zip(key,value))
    return filna_tobe_inserted


def inloop_uitloop_stans(df, wikkel, etiket_y, kolomnaam_vervang_waarde):
    # apr? laatstesluit? opbouw bewerken 3 sheets in en uit.
    # kan je 1 regel maken met generator en dat vermenigvuldigen met inloop waarde

    loop = (etiket_y * 10) - (wikkel +(3 * etiket_y))
    generator = df.itertuples(index=0)

    einde_df = len(df)
    data_df = []
    nieuwe_df = []

    sluitetiket = pd.DataFrame(
        [x for x in itertools.islice(generator, 1, 3)] # if wikkel =1 else???/
    )
    # sluitetiket2= pd.DataFrame(
    #     [x for x in itertools.islice(generator, 2, 3)],

    generator = df.itertuples(index=0)

    for seq in itertools.islice(generator, 0, 4):
        data_df.append(seq)

    data_df1 = pd.DataFrame(data_df)

    pdf_data_inloop_enuitloop_uit_iterslice = pd.DataFrame(
        [x for x in itertools.islice(generator, wikkel, wikkel + (3*etiket_y))]
    )
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


def maak_meerdere_vdps(banen_gemaakt_uit_eerste_df, mes, aantal_vdps, ordernummer, pad, sluitbarcode_uitvul_waarde_getal, etiket_y,dummylijst=[]):
    """bouwt vdps #todo  voeg de dummylijst hier meteen aan het einde van de lijst toe zodat we uitkomen"""
    # maak een lijst van lijsten
    #todo check of dit ook voor 1 vdp werkt


    # banen_met_reset_index.columns = kolomnamen
    te_gebruiken_lijst = banen_gemaakt_uit_eerste_df + dummylijst

    lijst_van_vdps_in_lijsten = lijst_opbreker(te_gebruiken_lijst, mes, aantal_vdps)

    for count, de_te_maken_vdp in enumerate(lijst_van_vdps_in_lijsten):
        vdp_naam_csv = pad.joinpath(f"{ordernummer} VDP {count + 1}.csv")
        logger.info("Writing VDP CSV: %s", vdp_naam_csv)

        banen_met_reset_index = pd.concat(de_te_maken_vdp, axis=1)

        kolomnamen = headers_for_totaal_kolommen(de_te_maken_vdp[0], mes)
        banen_met_reset_index.columns = kolomnamen


        vervang_beeld_stans = filna_dict("pdf", "stans.pdf", mes)
        vervang_sluitean_ = filna_dict("sluitbarcode", sluitbarcode_uitvul_waarde_getal, mes)
        vervang_sluitean_.update(vervang_beeld_stans)
        nieuwe_df = banen_met_reset_index.fillna(value=vervang_sluitean_)

        inloop_uitloop_stans(nieuwe_df, aantal_vdps, etiket_y,
                             list(vervang_beeld_stans.keys())).to_csv(vdp_naam_csv, index=0)


    return 0


