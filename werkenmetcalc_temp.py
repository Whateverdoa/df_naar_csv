from calculations import *



##################################################
mes = 5
wikkel=2
etiket_y=25
apr =10
aantal_vdps=1
sluitbarcode_posities=8
####################################################

aantalbanen= aantal_vdps * mes


de_gemaakte_df_uit_excel = splitter_df_2(test_engelvaartwibra, mes, 1,8,0)

banen_gemaakt_uit_eerste_df = [pd.concat(de_gemaakte_df_uit_excel[x]).reset_index(drop=True) for x in range(len(de_gemaakte_df_uit_excel))]

if aantal_vdps >= 1:
    #todo hoe bereken ik hier wanneer de combinatie niet uitkomt (bij ongelijke ) en hoe tackel ik dat
    nvdp=lijst_opbreker(banen_gemaakt_uit_eerste_df, mes, aantal_vdps)
    print(len(nvdp))



banen_met_reset_index = pd.concat(banen_gemaakt_uit_eerste_df, axis=1)
kolomnamen=headers_for_totaal_kolommen(banen_gemaakt_uit_eerste_df[0], aantalbanen)
# eerst deze banen uitvullen met stans.pdf voor je verder gaat gebruik een veelvoud van een regel
# ipv van een hele slice

kolomnamen=headers_for_totaal_kolommen(banen_gemaakt_uit_eerste_df[0], aantalbanen)
banen_met_reset_index.columns=kolomnamen

vervang_beeld_stans = filna_dict("beeld","stans.pdf",aantalbanen)
#  3 soorten in laten vullen door gebruiker.
sluitean = 8710000000000
ean8=1412178

posities=8
sluitbarcode_uitvul_waarde= 1412178 # nummer met voorloopgetal 0
sluitbarcode_uitvul_waarde_getal = f"{sluitbarcode_uitvul_waarde:>{0}{posities}}"

ean = 0
# hier zit een keuze van 3 soorten in
vervang_sluitean_ = filna_dict("sluitbarcode", sluitbarcode_uitvul_waarde_getal, aantalbanen)

vervang_sluitean_.update(vervang_beeld_stans)

nieuwe_df = banen_met_reset_index.fillna(value=vervang_sluitean_)

inloop_uitloop_stans(nieuwe_df, aantal_vdps, etiket_y, list(vervang_beeld_stans.keys())).to_excel("202177773_5_banen.xlsx", index=0)
inloop_uitloop_stans(nieuwe_df, aantal_vdps, etiket_y, list(vervang_beeld_stans.keys())).to_csv("202177773_5_banen.csv", index=0)

nieuwevdpdf = inloop_uitloop_stans(nieuwe_df, aantal_vdps, etiket_y, list(vervang_beeld_stans.keys()))