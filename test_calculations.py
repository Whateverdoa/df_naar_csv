from calculations import (maak_een_dummy_baan,
                          splitter_df,
                          splitter_df_2,
                          dfbouwer,
                          testdf,
                          testdf7,
                          lijst_opbreker,
                          banen_in_vdp_check,
                          standaardtestfile,
                          maak_meerdere_vdps,
                          )

import pandas as pd


def test_splitter_df():
    # test2 = splitter_df(testdf, 3, 2)
    test3 = splitter_df(testdf, 4, 3)

    # assert test2 == (483,125935, 20989)
    assert test3 == (472, 125935, 10494,
                     ['tel_1_7', 'Artnr', 'ColorC', 'ColorN', 'Size',
                      'Price', 'Barcode', 'Aantal', 'beeld'])


def test_dfbouwer():
    test = dfbouwer(testdf7)
    print(test)
    assert False


def test_splitter_df_2():
    test3 = splitter_df_2(testdf, 4)
    # test3 = splitter_df_2(test_mouthaan, 4, 6)

    assert type(test3) == list


testlijst1 = [1, 2, 3, 4, 5, 6]


def test_lijst_opbreker():
    testinglijstbrekeer = lijst_opbreker(testlijst1, 3, 2)

    assert testinglijstbrekeer == [[1, 2, 3], [4, 5, 6]]


def test_banen_in_vdp_check():
    minder = banen_in_vdp_check(4, 3)  # assert False
    meer = banen_in_vdp_check(4, 5)  # assert False
    gelijk = banen_in_vdp_check(4, 4)

    assert gelijk == 0


def test_maak_meerder_vdps():
    banen_gemaakt_uit_eerste_df = [pd.concat(standaardtestfile[x]).reset_index(drop=True)
                                   for x in range(len(standaardtestfile))]
    valueerror = maak_meerdere_vdps(banen_gemaakt_uit_eerste_df, mes=4,
                                    aantal_vdps=1,
                                    ordernummer="test",
                                    pad="",
                                    sluitbarcode_uitvul_waarde_getal="012345678",
                                    etiket_y=10)
    assert valueerror == 0


def test_maak_een_dummy_baan():
    type,dummybaantest=maak_een_dummy_baan(standaardtestfile,100,2)

    assert type, dummybaantest==(type(list),2)

