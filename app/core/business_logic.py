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
import logging

logger = logging.getLogger(__name__)


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
    columns = ["pdf", "omschrijving", "Artnr", "sluitbarcode"]

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

    logger.debug("splitter_df_2: gemiddelde=%d afwijking=%d rollen=%d", gemiddelde, afwijking_waarde, aantal_rollen)

    dataframes_gesplitst = []
    dataframe_lijst = []
    aantal_lijst = []

    for num, regel in enumerate(df_in.itertuples(index=0), 1):

        df_regel, df_regel_aantal = rol_beeld_is_pdf_uit_excel(regel, wikkel, sluitbarcode_posities, pdf_sluitetiket, extra_etiketten=extra_etiketten)

        dataframe_lijst.append(df_regel)
        aantal_lijst.append((df_regel_aantal))

        som = sum(aantal_lijst)

        if som >= gemiddelde or aantal_rollen == num:

            logger.debug("Lane split: gemiddelde=%d som=%d verschil=%d rollen=%d", gemiddelde, som, som - gemiddelde, num)
            dataframes_gesplitst.append(pd.concat(dataframe_lijst, ignore_index=True))
            dataframe_lijst=[]

            aantal_lijst = []

            continue

    return dataframes_gesplitst


def banen_in_vdp_check(aantalbanen, daadwerkelijk_gemaakte_banen, aantal_vdps=1, mes_waarde=1):
    """Check if we need dummy lanes"""
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
    logger.debug("dummy baan kolomnamen: %s", kolomnamen)
    
    # Replace image value for stans.pdf or leeg.pdf
    dummy_baan_generator['beeld'] = "stans.pdf"
    if 'sluitbeeld' in dummy_baan_generator.columns:
        dummy_baan_generator['sluitbeeld'] = "leeg.pdf"

    # Get rules for dummies
    db = dummy_baan_generator[0:aantal_dummy_banen].itertuples()
    logger.debug("maak_een_dummy_baan: %d dummy banen", aantal_dummy_banen)

    def dummy_rol_is_baan(regel, gemiddelde_aantal, pdf_sluitetiket=True):
        columns = ["pdf", "omschrijving", "Artnr", "sluitbarcode"]
        aantal = gemiddelde_aantal

        rol_vulling = pd.DataFrame(
            [(f'{regel.beeld}', "dummy_BAAN", "", 0)
             for x in range(aantal) for i in range(1)], columns=columns)
        return rol_vulling

    dummy_lijst_voor_baan = [dummy_rol_is_baan(regel, gemiddelde, pdf_sluitetiket=True) for regel in db]
    logger.debug("dummy baan columns: %s", dummy_lijst_voor_baan[0].columns if dummy_lijst_voor_baan else "No dummy lanes created")

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

    logger.debug("summary_splitter_df_2: gemiddelde=%d afwijking=%d rollen=%d", gemiddelde, afwijking_waarde, aantal_rollen)

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
            logger.debug("summary_splitter_df_2: slice=(%d, %d)", beginslice, eindslice)
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
        logger.debug("df_sum_met_slice: slice=(%d, %d)", beginslice, eindslice)

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
        logger.debug("df_sum_form_writer: %s=%s", key, value)

    sum_dik = {key: [key,value] for (key, value) in kwargs.items()}
    df_summary = pd.DataFrame.from_dict(sum_dik, orient="index")

    return df_summary


def pdf_sum_form_writer(output_dir, titel, banen_data, **kwargs):
    """Write a PDF summary file alongside the existing HTML/Excel summaries.

    Parameters
    ----------
    output_dir : str or Path
        Directory where the PDF will be written.
    titel : str
        Used as the filename stem (e.g. "summary" → "summary.pdf").
    banen_data : dict
        Must contain ``meters_per_baan`` (list[float]) and
        ``banen_summary`` (list[dict]) keys.
    **kwargs
        Remaining job parameters forwarded to ``generate_pdf_summary``.
    """
    from pdf_summary import generate_pdf_summary

    output_path = Path(output_dir) / f"{titel}.pdf"

    generate_pdf_summary(
        output_path=output_path,
        meters_per_baan=banen_data.get("meters_per_baan", []),
        banen_summary=banen_data.get("banen_summary", []),
        **kwargs,
    )
    return output_path
