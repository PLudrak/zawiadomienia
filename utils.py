from geopy.geocoders import Nominatim
import re


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
		if len(kod_miejscowosc) < 2 and "-" not in kod_miejscowosc[0]:
			miejscowosc = " ".join(kod_miejscowosc)
			s_adres= f"{ulica_nra}, {" ".join(kod_miejscowosc)}" #adres do  wyszukiwania kodu pocztowego
			kod = missing_postcode(" ".join(kod_miejscowosc),s_adres,kody_pocztowe)
		else :
			kod = kod_miejscowosc[0]
			miejscowosc = " ".join(kod_miejscowosc[1:])
		

		return ulica,nr_a,nr_l,kod,miejscowosc
	except Exception as e:
		print(f"Wystąpił błąd przy przetwarzaniu adresu\n '{SWDE_adres}':{e}")
		print("Wciśnij '-' jeżeli brak adresu, lub wpisz poprawiony adres w formacie:")
		print("ULICA NUMER m.LOKAL; KOD MIEJSCOWOŚĆ")
		adres_input = input()
		if adres_input.upper() == "-":
			return pusty_adres
		ulica,nr_a,nr_l,kod,miejscowosc = convert_adress(adres_input)
		return ulica,nr_a,nr_l,kod,miejscowosc


def missing_postcode(miejscowosc:str,adres, kody_pocztowe):
	"""Uzupełnij kod ręcznie lub wyszukaj automatycznie"""
	print(f"W adresie brak kodu dla miejscowości: {miejscowosc} ")
	
	ostatni_kod = kody_pocztowe.get(miejscowosc)
		
	print("Wpisz poprawny kod lub:")
	if ostatni_kod:
		print(f"[Y] Użyj ostaniego kodu dla {miejscowosc}: {kody_pocztowe[miejscowosc]}")
	kod=input("[X] żeby wyszukać\n")
	
	if kod.capitalize() == "X":
		kod = search_postcode(adres)
	elif kod.capitalize== "Y":
		kod= kody_pocztowe[miejscowosc]
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
		print(f"Kod pocztowy dla adresu {miejscowosc} to {postcode}:\n Y-zatwierdź lub wpisz poprawny kod")
		zatwierdz = input()
		if zatwierdz.capitalize() == "Y":
			return postcode
		else:
			return zatwierdz
	else: 
		print("Nie znaleziono kodu")
	return postcode
