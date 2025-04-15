from utils import *
import pandas as pd

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
			
	df_osoby = pd.DataFrame(columns=osoby_kolumny)

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
		
		#dodaj kod pocztowy do słownika
		if MIASTO not in kody_pocztowe:
			kody_pocztowe[MIASTO] = KOD_POCZTOWY
		
		print([LP,ID_ORYGINALNE,SWDE_NAZWA,SWDE_ADRES,IMIE_OJCA,IMIE_MATKI,TYP_OSOBY,ULICA,NR_DOMU,NR_LOKALU,KOD_POCZTOWY,MIASTO])





filename=r"D:\Python\kuba\zawiadomienia\import\5.11.2024\wlasc.xlsx"
create_base_from_excel(filename)