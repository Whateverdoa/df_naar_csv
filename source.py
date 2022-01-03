"""'generator dataframe naar csv"""

import PySimpleGUI as sg
from pathlib import Path
from icecream import ic
import pandas as pd
from calculations import *
from summary import (summary_splitter_df_2,
                     html_sum_form_writer,
                     df_sum_met_slice)


while True:
    sg.change_look_and_feel('DefaultNoMoreNagging')

    columns = []
    font = ('Arial', 10)
    layout = [
        [sg.Text("Excel naar VDP's ombouw", size=(30, 1), font=('Arial', 14, 'bold'), text_color="darkblue")],
        [sg.InputText('202012345', key='ordernummer_1'), sg.Text('Ordernummer', font=font)],
        [sg.InputText('4', key='mes'), sg.Text('mes', font=font)],
        [sg.InputText('7 ', key='vdp_aantal'), sg.Text("VDP's", font=font)],
        [sg.InputText('01409468', key='sluitbarcode_uitvul_waarde'), sg.Text("uitvul sluitbarcode", font=font)],
        [sg.InputText('8', key='posities_sluitbarcode_uitvul_waarde'), sg.Text("Posities voor sluitbarcode", font=font)],
        [sg.InputText('0', key='afwijkings_waarde'), sg.Text("afwijking_waarde", font=font)],
        [sg.InputText('76', key='kern'), sg.Text("kern", font=font)],
        [sg.InputText('80', key='formaat breedte'), sg.Text("breedte", font=font)],
        [sg.InputText('80', key='formaat hoogte'), sg.Text("hoogte", font=font)],


        [sg.Text()],

        [sg.InputText('10', key='Y_waarde'), sg.Text('Y-waarde')],
        [sg.Text('Excel file')],
        [sg.Text('verplichte headers zijn: aantal, Omschrijving, sluitbarcode, Artnr')],
        [sg.Input(), sg.FileBrowse()],

        [sg.Text()],
        [
            sg.Frame(
                layout=[
                    # [
                    #     sg.Checkbox(
                    #         "gebruik template bij sscc, 1 extra '?' toevoegen voor de cd",
                    #         key="gebruik_template",
                    #         default=False,
                    #     )
                    # ],
                    # [
                    #     sg.Text("template", size=(15, 1)),
                    #     sg.Input("??????????????", key="template"),
                    # ],
                    # [
                    #     sg.Checkbox(
                    #         "gebruik slice rechts",
                    #         key="slice_rechts_check",
                    #         default=False,
                    #     )
                    # ],
                    # [
                    #     sg.Text("slice rechts", size=(15, 1)),
                    #     sg.Input(3, key="slice_rechts"),
                    # ],
                    # [
                    #     sg.Checkbox(
                    #         "gebruik slice links",
                    #         key="slice_links_check",
                    #         default=False,
                    #     )
                    # ],
                    # [
                    #     sg.Text("slice links", size=(15, 1)),
                    #     sg.Input(3, key="slice_links"),
                    # ],
                    [
                        sg.Checkbox(
                            "Wikkel handmatig",
                            key="wikkel_handmatig",
                            default=False,
                        )
                    ],
                    [
                        sg.Text("Wikkel", size=(5, 1)),
                        sg.Input(1, key="wikkel_handmatige_invoer"),
                    ],
                    [sg.Text()],
                    # [
                    #     sg.Checkbox(
                    #         "SSCC18", key="sscc18", default=False, size=(10, 1)
                    #     ),
                    #     sg.Checkbox("null", key="null", default=False),
                    # ],
                    [
                        sg.Radio(
                            "NL",
                            "RADIO1",
                            key="radio",
                            default=True,
                            size=(5, 1),
                        ),
                        sg.Radio("Duits", "RADIO1"),
                    ],
                ],
                title="Options",
                title_color="red",
                relief=sg.RELIEF_SUNKEN,
                tooltip="taal voor sluitetiket",
            )
        ],

        [sg.InputText('1', key='overlevering_pct'), sg.Text('overlevering %')],
        [sg.InputText('10', key='ee'), sg.Text('extra etiketten')],
        [sg.InputText('10', key='wikkel'), sg.Text('Wikkel')],
        [sg.InputText('opmerkingen', key='opmerkingen'), sg.Text('Opmerkingen')],





        [sg.Button("Ok"), sg.Cancel()],
        # run button]

        # this saves the input information
        [sg.Text('_' * 40)],
        [sg.Text('SAVE of LOAD inputform', size=(35, 1))],
        # [sg.Text('Your Folder', size=(15, 1), justification='right'),
        #  sg.InputText('Default Folder', key='folder'), sg.FolderBrowse()],
        [sg.Button('Exit'),
         sg.Text(' ' * 40), sg.Button('SaveSettings'), sg.Button('LoadSettings')]

    ]
    window = sg.Window('VDP formulier 2021 for use with DFgen',
                       layout, default_element_size=(30, 1), grab_anywhere=False)

    while True:
        event, values = window.read()

        #todo make OS proof with try except

        if event in ('Exit', None):

            exit(0)

        elif event == 'SaveSettings':
            filename = sg.popup_get_file('Save Settings', save_as=True, no_window=False)
            # False in macOS otherwise it will crash
            window.SaveToDisk(filename)

            # save(values)
        elif event == 'LoadSettings':
            filename = sg.popup_get_file('Load Settings', no_window=False)
            # False in macOS otherwise it will crash
            window.LoadFromDisk(filename)
            # load(form)

        elif event == "Cancel":

            exit(0)

        elif event == "Ok":

            ordernummer = values['ordernummer_1']

            mes = int(values['mes'])
            aantal_vdps = int(values['vdp_aantal'])
            etiket_y = int(values['Y_waarde'])
            name_file_in = Path(values['Browse'])
            pad = name_file_in.parent

            afwijkings_waarde = int(values['afwijkings_waarde'])

            sluitbarcode_uitvul_waarde= int(values['sluitbarcode_uitvul_waarde'])
            sluitbarcode_posities = int(values['posities_sluitbarcode_uitvul_waarde'])
            sluitbarcode_uitvul_waarde_getal = f"{sluitbarcode_uitvul_waarde:>{0}{sluitbarcode_posities}}"

            overlevering_pct = float(values['overlevering_pct'])
            extra_etiketten = int(values['ee'])
            hoogte = int(values['formaat hoogte'])
            kern = int(values['kern'])

            opmerkingen = str(values['opmerkingen'])
            # wikkel = int(values['wikkel'])

            # todo try except
            # atribute error als er geen excel gekozen is na load e
            print(f'name_file_in.parent ={name_file_in.parent.is_dir()}')

            wikkel_handmatig = values["wikkel_handmatig"]
            if wikkel_handmatig:
                wikkel = int(values["wikkel_handmatige_invoer"])  # handmatige wikkel
            else:
                #todo max rol waarde halen uit dataframe
                # aantal_per_rol = de max aantalperrol in de lijst
                aantal_per_rol=10
                wikkel = de_uitgerekenende_wikkel(aantal_per_rol, hoogte, kern)

            print(mes,
                  aantal_vdps,
                  etiket_y,
                  name_file_in,
                  overlevering_pct,
                  extra_etiketten,
                  wikkel)

            # stap 1 maak een dataframe van de file
            de_te_verwerken_dataframe = file_to_generator(name_file_in)
            ic(de_te_verwerken_dataframe.head(2))
            ic(de_te_verwerken_dataframe.tail(2))

            aantalbanen = aantal_vdps * mes
            totaal_aantal = int(de_te_verwerken_dataframe.aantal.sum())
            gemiddelde = (totaal_aantal // (mes * aantal_vdps)) - afwijkings_waarde

            de_gemaakte_df_uit_excel = splitter_df_2(de_te_verwerken_dataframe,
                                                     mes=mes,
                                                     aantalvdps=aantal_vdps,
                                                     sluitbarcode_posities=sluitbarcode_posities,
                                                     afwijking_waarde=afwijkings_waarde,
                                                     wikkel=wikkel,
                                                     gemiddelde=None
                                                     )


            #stap 2 verdeel de lijst over een x(vdps * mes) aantal banen
            banen_gemaakt_uit_eerste_df = [pd.concat(de_gemaakte_df_uit_excel[x]).reset_index(drop=True)
                                           for x in range(len(de_gemaakte_df_uit_excel))]


            banen_gemaakt = len(banen_gemaakt_uit_eerste_df)

            ##### dummybanen maken
            dummybanen_bool, aantal_dummy_banen =banen_in_vdp_check(aantalbanen, banen_gemaakt)
            if dummybanen_bool != True:
                dummy_banen_zijn = []
                #break
            elif dummybanen_bool == True:
                de_te_verwerken_naar_dummydataframe = file_to_generator(name_file_in)

                dummy_banen_zijn = maak_een_dummy_baan(de_te_verwerken_naar_dummydataframe,
                                                       gemiddelde,
                                                       aantal_dummy_banen)
                print("dummybanen maken")

            if aantal_vdps == 1:
                wdir= name_file_in
                vdp_naam_csv =  pad.joinpath(f'{ordernummer}_VDP_1.csv')

                banen_met_reset_index = pd.concat(banen_gemaakt_uit_eerste_df, axis=1)
                kolomnamen = headers_for_totaal_kolommen(banen_gemaakt_uit_eerste_df[0], mes)
                banen_met_reset_index.columns = kolomnamen

                vervang_beeld_stans = filna_dict("beeld", "stans.pdf", mes)
                vervang_sluitean_ = filna_dict("sluitbarcode", sluitbarcode_uitvul_waarde_getal, mes)

                vervang_sluitean_.update(vervang_beeld_stans)

                nieuwe_df = banen_met_reset_index.fillna(value=vervang_sluitean_)

                inloop_uitloop_stans(nieuwe_df, aantal_vdps, etiket_y,
                                     list(vervang_beeld_stans.keys())).to_csv(
                    vdp_naam_csv, index=0)


            else:

                maak_meerdere_vdps(banen_gemaakt_uit_eerste_df,
                                  mes,
                                  aantal_vdps,
                                  ordernummer,
                                  pad,
                                  sluitbarcode_uitvul_waarde_getal,
                                  etiket_y)

                # maak een lijst van lijsten
                # lijst_van_vdps_in_lijsten = lijst_opbreker(banen_gemaakt_uit_eerste_df,mes,aantal_vdps)
                # # banen_met_reset_index.columns = kolomnamen
                #
                # for count, de_te_maken_vdp in enumerate(lijst_van_vdps_in_lijsten):
                #     vdp_naam_csv = pad.joinpath(f"{ordernummer} VDP {count + 1}.csv")
                #     print(vdp_naam_csv)
                #
                #     banen_met_reset_index = pd.concat(de_te_maken_vdp, axis=1)
                #     kolomnamen = headers_for_totaal_kolommen(de_te_maken_vdp[0], mes)
                #     banen_met_reset_index.columns = kolomnamen
                #
                #
                #     vervang_beeld_stans = filna_dict("beeld", "stans.pdf", mes)
                #     vervang_sluitean_ = filna_dict("sluitbarcode", sluitbarcode_uitvul_waarde_getal, mes)
                #     vervang_sluitean_.update(vervang_beeld_stans)
                #     ic(sluitbarcode_uitvul_waarde_getal)
                #     nieuwe_df = banen_met_reset_index.fillna(value=vervang_sluitean_)
                #
                #     inloop_uitloop_stans(nieuwe_df, aantal_vdps, etiket_y,
                #                          list(vervang_beeld_stans.keys())).to_csv(
                #         vdp_naam_csv, index=0)


            #################SUMMARY ########################

            summary_file_uit_excel = summary_splitter_df_2(de_te_verwerken_dataframe,
                                                     mes=mes,
                                                     aantalvdps=aantal_vdps,
                                                     sluitbarcode_posities=sluitbarcode_posities,
                                                     afwijking_waarde=afwijkings_waarde,
                                                     wikkel=wikkel,
                                                     gemiddelde=None)

            lengte_summary_df = len(summary_file_uit_excel)
            lijst_van_sumary_lijsten = lijst_opbreker(summary_file_uit_excel,mes,aantal_vdps)

            # if vdp==1:
            #     summary_vdp1 =df_sum_met_slice(de_te_verwerken_dataframe, summary_file_uit_excel, 1)
            #     summary_vdp1.to_excel(pad.joinpath(f'{name_file_in.stem}_summary_VDP_1.xlsx'))
            #
            # elif vdp > 1:
            #     for count,lijst in enumerate(lijst_van_sumary_lijsten,1):
            #         df_sum_met_slice(de_te_verwerken_dataframe,lijst,count)









            aantal_rollen, kolommen = de_te_verwerken_dataframe.shape

            keywordargs = {
                "Ordernummer: ": ordernummer,
                "Aantal VDP's": aantal_vdps,
                # "vdp meters: ": f'{meterlijst} m',

                "Totaal aantal ": str(f"{totaal_aantal:,} etiketten").replace(",", "."),
                # "begin_nummer": f"{prefix}{begin_nummer:>{0}{posities}}{postfix}",
                # "eind_nummer": f"{prefix}{begin_nummer + totaal_aantal - 1:>{0}{posities}}{postfix}",
                "Aantal Rollen": f"{aantal_rollen} rollen",
                # "Rol_nummers": f'Rol_{begin_rolnummer + 1} t/m Rol_{begin_rolnummer + aantal_rollen}',
                "Mes ": mes,
                # 'Mes x combinaties ': f'{mes} van {combinaties} banen',
                "Wikkel": f"{wikkel + 3} etiketten inclusief sluitetiket",
                "Inloop en uitloop": f"{etiket_y} x 10 sheets.",
                # 'De files staan hier': naar_folder_pad,
                "Opmerkingen": opmerkingen,

                # " datafr": 0}
            }

            html_sum_form_writer(pad, ordernummer, **keywordargs)



            print('ok')
