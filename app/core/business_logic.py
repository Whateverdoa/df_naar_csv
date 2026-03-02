"""
Business logic wrapper that imports only what's needed for the API
This avoids importing PySimpleGUI and other GUI dependencies
"""
import itertools
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
import xlrd
import xlwt
from icecream import ic


def file_to_generator(file_in):
    """Builds from a workable csv or excel file a Dataframe
     on which to Generate with itertuples or ...."""

    if Path(file_in).suffix == ".csv":
        # extra arg = ";"or ","
        file_to_generate_on = pd.read_csv(file_in, sep=";")
        return file_to_generate_on

    elif Path(file_in).suffix == ".xlsx":
        # print(Path(file_in).suffix)
        file_to_generate_on = pd.read_excel(file_in, engine='openpyxl')
        return file_to_generate_on

    elif Path(file_in).suffix == ".xls":
        # print(Path(file_in).suffix)
        file_to_generate_on = pd.read_excel(file_in)
        return file_to_generate_on


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


# Create the wikkel calculator instance
de_uitgerekenende_wikkel = wikkel_formule()


def begin_eind_dataframe(df_rol):
    """geeft begin van file, eind van file en aantal van file in tuple format"""

    begin = df_rol.iat[0, 0]
    beg = df_rol.iloc[0, 0]
    einde, kolommen = df_rol.shape
    eind_positie_rol = einde - 1
    eind = df_rol.iat[eind_positie_rol, 0]

    return (begin, eind, einde)


def rol_beeld_is_pdf_uit_excel(regel, wikkel, posities_sluitbarcode=8, pdf_sluitetiket=True, extra_etiketten=5):
    """Build a single-roll DataFrame with wikkel wrapping and sluitetiket rows."""
    aantal = int(regel.aantal)
    columns = ["beeld", "omschrijving", "Artnr", "sluitbarcode"]

    rol_vulling = pd.DataFrame(
        [(f'{regel.beeld}', "", regel.Artnr, f"{regel.sluitbarcode:0>{posities_sluitbarcode}}")
         for _ in range(aantal + extra_etiketten)], columns=columns)

    if pdf_sluitetiket and hasattr(regel, 'sluitbeeld'):
        sluitetiket = pd.DataFrame(
            [(f'{regel.sluitbeeld}', "", "", f"{regel.sluitbarcode:0>{posities_sluitbarcode}}")],
            columns=columns)
    else:
        sluitetiket = pd.DataFrame(
            [("leeg.pdf", f'{regel.Omschrijving} | {aantal} etiketten', "",
              f"{regel.sluitbarcode:0>{posities_sluitbarcode}}")],
            columns=columns)

    wikkel_om_rol = pd.DataFrame(
        [('stans.pdf', "", "", f"{regel.sluitbarcode:0>{posities_sluitbarcode}}")
         for _ in range(wikkel)], columns=columns)

    rol = pd.concat([wikkel_om_rol, sluitetiket, rol_vulling, sluitetiket], ignore_index=True)
    return rol, aantal


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

    print(f'{gemiddelde = } met {afwijking_waarde}', f'{ aantal_rollen = }')

    dataframes_gesplitst = []
    dataframe_lijst = []
    aantal_lijst = []

    for num, regel in enumerate(df_in.itertuples(index=0), 1):

        df_regel, df_regel_aantal = rol_beeld_is_pdf_uit_excel(regel, wikkel, sluitbarcode_posities, pdf_sluitetiket, extra_etiketten=extra_etiketten)

        dataframe_lijst.append(df_regel)
        aantal_lijst.append((df_regel_aantal))

        som = sum(aantal_lijst)
        ic(som)

        if som >= gemiddelde or aantal_rollen == num:

            print(f'gemiddelde ={gemiddelde} som = {som} verschil = {som-gemiddelde}, STOP * {num} rollen in  file in dataframes_gesplitst__')
            dataframes_gesplitst.append(dataframe_lijst)
            dataframe_lijst=[]

            aantal_lijst = []

            continue

    return dataframes_gesplitst


def banen_in_vdp_check(aantalbanen, daadwerkelijk_gemaakte_banen, aantal_vdps=1, mes_waarde=1):
    """Check if we need dummy lanes"""
    if aantalbanen == daadwerkelijk_gemaakte_banen:
        print(" doorgaan ")
        return True, 0, aantal_vdps
    else:
        if aantalbanen > daadwerkelijk_gemaakte_banen:
            dummybanen = aantalbanen - daadwerkelijk_gemaakte_banen
            print(f'{aantalbanen-daadwerkelijk_gemaakte_banen} te weinig dus opnieuw berekenen')
            print(f'maak {dummybanen} lege dummybanen')
            return False, dummybanen, aantal_vdps
        elif aantalbanen < daadwerkelijk_gemaakte_banen:
            print("meer vdp's nodig")
            aantal_vdps += 1
            dummybanen = (aantal_vdps * mes_waarde) - daadwerkelijk_gemaakte_banen
            return False, dummybanen, aantal_vdps,
        else:
            dummybanen = daadwerkelijk_gemaakte_banen - aantalbanen
            print(f'{daadwerkelijk_gemaakte_banen-aantalbanen} te veel?weinig? voeg lege baan(banen) toe')
            print(f'maak {dummybanen} lege dummybanen')
            return False, dummybanen, aantal_vdps


def lijst_opbreker(lijst_in, mes_waarde, combi):
    """Break list into combinations"""
    start = 0
    end = mes_waarde
    combinatie_binnen_mes = []

    for combinatie in range(combi):
        combinatie_binnen_mes.append(lijst_in[start:end])
        start += mes_waarde
        end += mes_waarde

    return combinatie_binnen_mes


def maak_een_dummy_baan(dummy_baan_generator, gemiddelde, aantal_dummy_banen):
    """Create dummy lanes"""
    kolomnamen = list(dummy_baan_generator.columns)
    ic(kolomnamen)
    
    # Replace image value for stans.pdf or leeg.pdf
    dummy_baan_generator['beeld'] = "stans.pdf"
    if 'sluitbeeld' in dummy_baan_generator.columns:
        dummy_baan_generator['sluitbeeld'] = "leeg.pdf"

    ic(dummy_baan_generator)

    # Get rules for dummies
    db = dummy_baan_generator[0:aantal_dummy_banen].itertuples()
    print(f'{db=}')

    def dummy_rol_is_baan(regel, gemiddelde_aantal, pdf_sluitetiket=True):
        columns = ["beeld", "omschrijving", "Artnr", "sluitbarcode"]
        aantal = gemiddelde_aantal

        rol_vulling = pd.DataFrame(
            [(f'{regel.beeld}', "dummy_BAAN", "", 0)
             for x in range(aantal) for i in range(1)], columns=columns)
        return rol_vulling

    dummy_lijst_voor_baan = [dummy_rol_is_baan(regel, gemiddelde, pdf_sluitetiket=True) for regel in db]
    ic(dummy_lijst_voor_baan[0].columns if dummy_lijst_voor_baan else "No dummy lanes created")

    return dummy_lijst_voor_baan, len(dummy_lijst_voor_baan)


# Summary functions
def rol_summary(df_in, regel, num, extra_etiketten):
    '''draait mee in de splitter2
    mischien zelfs tijn om async te proberen'''
    columns = ["beeld", "omschrijving","aantal"]

    aantal = regel.aantal + extra_etiketten

    summary_rol= pd.DataFrame(
        [(f'{regel.beeld} | rol {num}' , f'{regel.Omschrijving}', f'{regel.aantal} etiketten') for x in range(1)]
     ,columns=columns)
    return summary_rol, regel.aantal


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

    print(f'{gemiddelde = } met {afwijking_waarde}', f'{ aantal_rollen =}')

    summary_lijst = []
    slice_lijst = []
    aantal_lijst = []

    for num, regel in enumerate(df_in.itertuples(index=0), 1):

        df_regel, df_regel_aantal = rol_summary(df_in, regel, num, extra_etiketten)

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
        spec_cols=['aantal', 'Omschrijving', 'sluitbarcode', 'beeld']
        baandf_usespeccols = baandf[spec_cols]

        totaal = baandf.aantal.sum()
        header = pd.DataFrame([[f'{totaal} etiketten in baan', "Omschrijving",f"VDP_{numvdp}", "beeld", ] for x in range(1)], columns=spec_cols)

        banen.append(header)
        banen.append(baandf_usespeccols)

    samen = pd.concat(banen)
    return samen


def df_sum_form_writer(**kwargs):
    """build a df file for summary purposes with  *kwargv"""
    for key, value in kwargs.items():
        print(key, value)

    sum_dik = {key: [key,value] for (key, value) in kwargs.items()}
    df_summary = pd.DataFrame.from_dict(sum_dik, orient="index")

    return df_summary
