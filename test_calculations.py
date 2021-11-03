from calculations import *


def test_splitter_df():
    # test2 = splitter_df(testdf, 3, 2)
    test3 = splitter_df(testdf, 4, 3)

    # assert test2 == (483,125935, 20989)
    assert test3 == (472, 125935, 10494,
                     ['tel_1_7', 'Artnr', 'ColorC', 'ColorN', 'Size',
                      'Price', 'Barcode', 'Aantal', 'beeld'])


def test_dfbouwer():

    test =  dfbouwer(testdf7)
    print(test)
    assert False
