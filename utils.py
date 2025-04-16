from geopy.geocoders import Nominatim
import re
from colorama import Fore, Style, init

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
		elif kod.capitalize()== "1":
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

if __name__ == "__main__":
	kody_pocztowe={}
	is_valid_postcode('05-205')
	missing_postcode('Klembów',"Żymirskiego 97",kody_pocztowe)
