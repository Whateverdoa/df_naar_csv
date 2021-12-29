from calculations import file_to_generator
from rollen import rol_beeld_is_pdf_uit_excel
import itertools


rolstandaardtest= file_to_generator(r"C:\Users\Dhr. Ten Hoonte\PycharmProjects\df_naar_csv\rollen\standaard_aanlever_excel.xlsx")
excel_in_dataframe = rolstandaardtest.itertuples(index=0)
regel1 = [x for x in itertools.islice(excel_in_dataframe,0,1)]

def testiter(df_in, test_functie):
    testlijst = []
    for count, regel in enumerate(df_in):
        testlijst.append(test_functie(regel))
    return testlijst




def test_rol_beeld_is_pdf_uit_excel():
    regel1test = testiter(excel_in_dataframe,rol_beeld_is_pdf_uit_excel())
    # print(type(regel1test))

    assert regel1test == 1000
