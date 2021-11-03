"""'generator dataframe naar csv"""

import PySimpleGUI as sg

# import pandas as pd


while True:
    sg.change_look_and_feel('DarkGrey5')

    columns = []

    layout = [
        [sg.Text('VDP invul formulier', size=(30, 1), font=('Arial', 14, 'bold'), text_color="orange")],
        [sg.InputText('202012345', key='ordernummer_1'), sg.Text('Ordernummer', font=('Arial', 12))],
        [sg.InputText('4', key='mes'), sg.Text('mes', font=('Arial', 12))],
        [sg.InputText('1', key='vdp_aantal'), sg.Text("VDP's", font=('Arial', 12))],
        [sg.InputText('0', key='afwijkings_waarde'), sg.Text("afwijking_waarde", font=('Arial', 12))],

        [sg.Text()],

        [sg.InputText('10', key='Y_waarde'), sg.Text('Y-waarde')],
        [sg.Text('CSV_file')],
        [sg.Input(), sg.FileBrowse()],

        [sg.Text()],

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
                       layout, default_element_size=(40, 1), grab_anywhere=False)

    while True:
        event, values = window.read()

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
            print('ok')
