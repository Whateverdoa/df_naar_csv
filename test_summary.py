from summary import summary_splitter_df_2
from rollen import rolstandaardtest,df_sum_met_slice

def test_summary_splitter_df_2():
    functie_splitter_tuple_lijst_maker_voor_test = summary_splitter_df_2(rolstandaardtest, mes=2, aantalvdps=2)
    functie_splitter_tuple_lijst_maker_voor_test1 = summary_splitter_df_2(rolstandaardtest, mes=3, aantalvdps=2)
    functie_splitter_tuple_lijst_maker_voor_test2 = summary_splitter_df_2(rolstandaardtest, mes=4, aantalvdps=2)
    functie_splitter_tuple_lijst_maker_voor_test3 = summary_splitter_df_2(rolstandaardtest, mes=5, aantalvdps=2)

    assert len(functie_splitter_tuple_lijst_maker_voor_test) == 4



