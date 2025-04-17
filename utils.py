from geopy.geocoders import Nominatim
from colorama import Fore, Style, init
from rapidfuzz import fuzz
import pandas as pd
import re
def c_input():
	return input(Fore.YELLOW + ">>> " +Style.RESET_ALL)

def print_import_message(new_row:dict,keys:list[str]):
	print(Fore.GREEN + "Załadowano:" + Style.RESET_ALL, end=": ")
	for key in keys:
		print(new_row[key],end=" ")
	print()


def create_name(SWDE_nazwa:str, SWDE_imie:str):
	"""tworzy nazwę Osoby: NAZWISKO + IMIĘ(jeżeli imię występuje)"""
	if SWDE_imie:
		nazwa = f"{SWDE_nazwa} {SWDE_imie}".strip()
		return nazwa
	else:
		return SWDE_nazwa

def convert_adress(SWDE_adres:str,kody_pocztowe:dict):
	"""Wyodrębnia z adresu ULICĘ,NUMER DOMU,NUMER LOKALU, KOD POCZTOWY,MIEJSCOWOŚĆ"""
	pusty_adres =["-","-","-","-","-"]
	try:
		SWDE_adres = SWDE_adres.upper()
		if not SWDE_adres:
			return pusty_adres


		ulica_nra_nrl, kod_miejscowosc = [a.strip() for a in SWDE_adres.split(";")]

		#wyodrębnianie ulicy, numeru domu, numeru lokalu
		if "M." in ulica_nra_nrl:
			ulica_nra, nr_l = ulica_nra_nrl.split("M.")
			nr_a = ulica_nra.split()[-1]
			ulica =" ".join(ulica_nra.split()[0:-1])
		else: 
			nr_l=None
			nr_a = ulica_nra_nrl.split()[-1]
			ulica= " ".join(ulica_nra_nrl.split()[0:-1])

		#wyodrębnianie ulicy, numeru domu, numeru lokalu
		if "M." in ulica_nra_nrl:
			ulica_nra, nr_l = ulica_nra_nrl.split("M.")
			nr_a = ulica_nra.split()[-1]
			ulica =" ".join(ulica_nra.split()[0:-1])
		else: 
			nr_l=None
			nr_a = ulica_nra_nrl.split()[-1]
			ulica_nra = ulica_nra_nrl
			ulica= " ".join(ulica_nra_nrl.split()[0:-1])
		
		#wyodrębnianie miejscowości i kodu pocztowego
		kod_miejscowosc=kod_miejscowosc.split()
		if len(kod_miejscowosc) < 2 and "-" not in kod_miejscowosc[0]: #Sprawdza czy kod pocztowy nie znajduje się w zmiennej
			miejscowosc = " ".join(kod_miejscowosc)
			s_adres= f"{ulica_nra}, {" ".join(kod_miejscowosc)}" #adres do  wyszukiwania kodu pocztowego
			kod = missing_postcode(" ".join(kod_miejscowosc),s_adres,kody_pocztowe)
		else :
			kod = kod_miejscowosc[0]
			miejscowosc = " ".join(kod_miejscowosc[1:])
		

		return ulica,nr_a,nr_l,kod,miejscowosc
	except Exception as e:
		while True:
			warning_strong("BRAK ADRESU")
			print("\n\nWystąpił błąd przy przetwarzaniu adresu")
			print(Fore.YELLOW + SWDE_adres +Style.RESET_ALL)
			print("Wpisz poprawiony adres w formacie:")
			print("ULICA NUMER m.LOKAL; KOD MIEJSCOWOŚĆ lub \n[3] Zatwierdź brak adresu\n[4] Zagranica")
			adres_input = input(Fore.YELLOW + ">>> " +Style.RESET_ALL)
			if adres_input.upper() == "3":
				return pusty_adres
			elif adres_input == "4":
				pass
			elif len(adres_input) < 10:
				print("Nierozpoznano adresu lub wyobru")
			else:
				try:
					ulica,nr_a,nr_l,kod,miejscowosc = convert_adress(adres_input, kody_pocztowe)
					return ulica,nr_a,nr_l,kod,miejscowosc
				except:
					print("Nierozpoznano adresu lub wyobru")
def warning(text:str):
	print()
	print(Fore.YELLOW + f"! {text} !"+ Style.RESET_ALL)

def warning_strong(text:str):
	print()
	print(Fore.RED + f"! {text} !"+ Style.RESET_ALL)

def missing_postcode(miejscowosc:str,adres, kody_pocztowe):
	"""Uzupełnij kod ręcznie lub wyszukaj automatycznie"""
	warning("BRAK KODU")
	print(f"W adresie brak kodu dla miejscowości: {miejscowosc} ")
	
	ostatni_kod = kody_pocztowe.get(miejscowosc)
	while True:
		print("Wpisz poprawny kod lub:")
		if ostatni_kod:
			print(f"[1] Użyj ostaniego kodu dla {miejscowosc}: {kody_pocztowe[miejscowosc]}")
		print(f"[2] żeby wyszukać {adres}")
		kod=input(Fore.YELLOW + ">>> " +Style.RESET_ALL)
		
		if kod.capitalize() == "2":
			kod = search_postcode(adres)
			break
		elif kod.capitalize()== "1" and ostatni_kod:
			kod= kody_pocztowe[miejscowosc]
			break
		elif is_valid_postcode(kod):
			break
	return kod

def search_postcode(miejscowosc:str):
	"""Wyszukaj kod pocztowy w openstreetmap"""
	
	#wyszukiwanie miejscowości w osm
	geolocator = Nominatim(user_agent="my_postcode_finder")
	location = geolocator.geocode(f"{miejscowosc}, Polska")
	
	if location is None:
		print("Nie znaleziono miejscowości")
		return None
	
	#Sprawdź czy kod jest w polu postcode
	adress = location.raw.get("address", {})
	postcode = adress.get('postcode')

	#Jeżeli brak w polu postcode, przeszukaj regexem:
	if not postcode:
		display = location.raw.get("display_name","")
		match = re.search(r'\b\d{2}-\d{3}\b',display)
		if match:
			postcode = match.group()
		
	if postcode:
		print(f"Kod pocztowy dla adresu {miejscowosc} to {postcode}:\n [1] zatwierdź lub wpisz poprawny kod")
		zatwierdz = input(Fore.YELLOW + ">>> " +Style.RESET_ALL)
		if zatwierdz.capitalize() == "1":
			return postcode
		else:
			return zatwierdz
	else: 
		print("Nie znaleziono kodu")
	return postcode

def is_valid_postcode(postcode:str):
	"""Sprawdź czy kod pocztowy jest w formacie NN-NNN"""
	valid=bool(re.match(r"^\d{2}-\d{3}$",postcode))
	if valid:
		return valid
	else:
		print("Niepoprawny kod pocztowy, spróbuj ponownie")
		return valid

def is_empty_val(val):
	return val is None or str(val).strip().upper() in ["","NONE","NAN"]

def compare_values(val1,val2, prog):
	"""porównuje dwie wartości, zwraca True jezeli podobne lub identyczne"""
	if is_empty_val(val1) and is_empty_val(val2):
		return True
	val1 = str(val1).upper().strip()
	val2 = str(val2).upper().strip()
	return fuzz.ratio(val1,val2) >=prog 

def has_empty_critical(nowy_rekord,df_row, critical_keys):
	"""Sprawdź czy kotrakolwiek wartosc kluczowa jest pusta"""
	return any(is_empty_val(nowy_rekord[k]) or is_empty_val(df_row[k]) for k in critical_keys)
			
def find_similar_record(df:pd.DataFrame,nowy_rekord:dict,critical_keys=None, keys:list[str]=None,prog:int =90):
	if keys is None:
		keys = list(nowy_rekord.keys())
	if critical_keys is None:
		critical_keys = keys

	first_similar = None

	for _, row in df.iterrows():
		podobienstwa = {key: compare_values(row[key],nowy_rekord[key],prog) for key in keys}
		all_match = all(podobienstwa.values())
		crit_match = any(podobienstwa[key] for key in critical_keys)

		if all_match:
			print("Znaleziono identyczny rekord")
			compare_similarities(row,nowy_rekord,podobienstwa)
			return handle_similar_records(row, nowy_rekord, identical =True)
		
		if first_similar is None and crit_match and not has_empty_critical(nowy_rekord,row,critical_keys):
			first_similar = (row, podobienstwa)
	
	if first_similar:
		row,podobienstwa = first_similar
		print("Znaleziono podobny rekord")
		compare_similarities(row,nowy_rekord,podobienstwa)
		return handle_similar_records(row,nowy_rekord,identical=False)
	return nowy_rekord

def compare_similarities(old:pd.Series,nowy_rekord:dict, podobienstwa:dict):
	"""wyswietla dwa rekordy do porownania"""
	print("W BAZIE:",end=" ")
	print_similarities(old.to_dict(),podobienstwa)
	print("NOWY   :",end=" ")
	print_similarities(nowy_rekord,podobienstwa)
	

def print_similarities(record, similarities):
	"""wyswietla podobienstwa w rekordzie na zielono i elementy rozne na czerwono"""
	for key in similarities.keys():
		item=str(record[key])
		if not item:
			item = "None"
		if similarities[key]:
			print(Fore.GREEN+"| " + item+ Style.RESET_ALL,end=" ")
		else:
			print(Fore.RED +"| " + item +Style.RESET_ALL,end=" ")
	print("|")

def handle_similar_records(old:pd.Series,new:dict,identical=False):
	print("Wybierz dzialanie:\n[1] Połącz z istniejącym\n[2] Utwórz nowy\n[3] Aktualizuj istniejacy")
	if identical: 
		print(Fore.YELLOW+"[4]"+ Style.RESET_ALL +
			 "Usun duplikat z bazy i dodaj działkę do istniejacej osoby")
	old = old.to_dict()
	while True:
		choice = c_input()
		if choice == "1":
			new["ID_ZASTAPIENIA"] = old["ID_ORYGINALNE"]
			return new
		if choice == "2":
			return new
		if choice == "3":
			pass
		if choice == "4" and identical:
			print("Funkcja jeszcze nie obslugiwana")
		else: 
			print("Nieprawidłowy wybór")


if __name__ == "__main__":
	df = pd.DataFrame([
    {"Nazwisko": "Kowalski", "Imię": "Jan", "Ulica": "Warszawska", "Nr_domu": "10", "Nr_lokalu": "8", "Kod": "00-001", "Miejscowość": "Warszawa"},
	{"Nazwisko": "Kowalski", "Imię": "Jan", "Ulica": "Podlaska", "Nr_domu": "10", "Nr_lokalu": "8", "Kod": "00-001", "Miejscowość": "Warszawa"},
	{"Nazwisko": "Marciniak", "Imię": "Janusz", "Ulica": "Podbeskidzka", "Nr_domu": "11", "Nr_lokalu": "9", "Kod": "00-000", "Miejscowość": "Niematakiej"}
])

	nowy = {"Nazwisko": "Kowalski", "Imię": "Jan", "Ulica": "Podlaska", "Nr_domu": "10", "Nr_lokalu": "8", "Kod": "00-001", "Miejscowość": "Warszawa"}

	find_similar_record(df,nowy)
