from utils import *
import pandas as pd
from colorama import Fore, Style, init

id_pracy = "S17K"

def create_base_from_excel(filename):
	"""Tworzy bazę danych na podstawie pliku excel z swde"""
	df_import = pd.read_excel(filename).fillna('')

	#kolumny bazy danych
	osoby_kolumny = [
		'LP',
		'ID_ZASTAPIENIA',
		'ID_ORYGINALNE',
		'SWDE_NAZWA', 
		'SWDE_ADRES',
		'IMIĘ_OJCA',
		'IMIĘ_MATKI',
		'TYP_OSOBY',
		'PESEL',
		'NIP',
		'NAZWA',
		'ADRES',
		'ULICA',
		'NR_DOMU',
		'NR_LOKALU',
		'KOD_POCZTOWY',
		'MIASTO'] 
			
	df = pd.DataFrame(columns=osoby_kolumny)
	import_message = Fore.GREEN + "Załadowano:" + Style.RESET_ALL
	kody_pocztowe = {}
	for index, row in df_import.iterrows():
		LP = index +1
		ID_ORYGINALNE = f"{id_pracy}#{LP}"
		ID_ZASTAPIENIA = ID_ORYGINALNE
		SWDE_NAZWA = create_name(row['nazw'],row['imie'])
		SWDE_ADRES = row['adres'].replace("#"," ")
		IMIE_OJCA = row['imie_o']
		IMIE_MATKI = row['imie_m']
		TYP_OSOBY = row['typ_os']
		PESEL = row['pesel']
		NIP = row['nip']
		ULICA, NR_DOMU, NR_LOKALU,KOD_POCZTOWY, MIASTO = convert_adress(SWDE_ADRES,kody_pocztowe)
		
		nowy_wiersz = {
		'LP':LP,
		'ID_ZASTAPIENIA':ID_ZASTAPIENIA,
		'ID_ORYGINALNE':ID_ORYGINALNE,
		'SWDE_NAZWA':SWDE_NAZWA, 
		'SWDE_ADRES':SWDE_ADRES,
		'IMIĘ_OJCA':IMIE_OJCA,
		'IMIĘ_MATKI':IMIE_MATKI,
		'TYP_OSOBY':TYP_OSOBY,
		'PESEL':PESEL,
		'NIP':NIP,
		'NAZWA':SWDE_NAZWA, #
		'ULICA':ULICA,
		'NR_DOMU':NR_DOMU,
		'NR_LOKALU':NR_LOKALU,
		'KOD_POCZTOWY':KOD_POCZTOWY,
		'MIASTO':MIASTO
		}
		
		df = pd.concat([df, pd.DataFrame([nowy_wiersz])],ignore_index=True)
		#dodaj kod pocztowy do słownika
		kody_pocztowe[MIASTO] = KOD_POCZTOWY
		
		print(import_message,[LP,ID_ORYGINALNE,SWDE_NAZWA,SWDE_ADRES,IMIE_OJCA,IMIE_MATKI,TYP_OSOBY,ULICA,NR_DOMU,NR_LOKALU,KOD_POCZTOWY,MIASTO])
	return df




filename=r"D:\Python\kuba\zawiadomienia\import\5.11.2024\wlasc.xlsx"
df = create_base_from_excel(filename)
df.to_excel("Osoby.xlsx", index=False)