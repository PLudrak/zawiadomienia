from utils import *
import pandas as pd
from colorama import Fore, Style, init
import time
import os

start = time.time()
id_pracy = "S17K"


def create_base_from_excel(filename, aktualnosc_danych):
    """Tworzy bazę danych na podstawie pliku excel z swde"""
    df_import = pd.read_excel(filename).fillna("")

    # kolumny bazy danych
    osoby_kolumny = [
        "LP",
        "ID_ZASTAPIENIA",
        "ID_ORYGINALNE",
        "SWDE_NAZWA",
        "SWDE_ADRES",
        "IMIĘ_OJCA",
        "IMIĘ_MATKI",
        "TYP_OSOBY",
        "PESEL",
        "NIP",
        "NAZWA",
        "ADRES",
        "ULICA",
        "NR_DOMU",
        "NR_LOKALU",
        "KOD_POCZTOWY",
        "MIASTO",
        "ID_DZIAŁKI",
        "UDZIAŁ",
        "RODZAJ WLASNOSCI",
    ]

    df = pd.DataFrame(columns=osoby_kolumny)

    kody_pocztowe = {}
    for lp, (_, row) in enumerate(df_import.iterrows(), start=1):
        # informacje o osobach z tabeli wlasc.xlsx
        LP = lp + 1
        ID_ORYGINALNE = f"{id_pracy}#{LP}"
        ID_ZASTAPIENIA = ID_ORYGINALNE
        SWDE_NAZWA = create_name(row["nazw"], row["imie"])
        SWDE_ADRES = row["adres"].replace("#", " ")
        IMIE_OJCA = row["imie_o"]
        IMIE_MATKI = row["imie_m"]
        TYP_OSOBY = row["typ_os"]
        PESEL = row["pesel"]
        NIP = row["nip"]
        ULICA, NR_DOMU, NR_LOKALU, KOD_POCZTOWY, MIASTO = convert_adress(
            SWDE_ADRES, kody_pocztowe
        )
        ADRES = f"{ULICA} {NR_DOMU} m.{NR_LOKALU}; {KOD_POCZTOWY} {MIASTO}"

        # informacje o relacjach z tabeli wlasc.xlsx
        ID_DZIALKI = row["ident_dz"]
        UDZIAL = row["udzial"]
        RODZAJ_WLASNOSCI = row["rodz_wl"]

        imported_values = {
            "LP": LP,
            "ID_ZASTAPIENIA": ID_ZASTAPIENIA,
            "ID_ORYGINALNE": ID_ORYGINALNE,
            "SWDE_NAZWA": SWDE_NAZWA,
            "SWDE_ADRES": SWDE_ADRES,
            "IMIE_OJCA": IMIE_OJCA,
            "IMIE_MATKI": IMIE_MATKI,
            "TYP_OSOBY": TYP_OSOBY,
            "PESEL": PESEL,
            "NIP": NIP,
            "NAZWA": SWDE_NAZWA,  #
            "ADRES": ADRES,
            "ULICA": ULICA,
            "NR_DOMU": NR_DOMU,
            "NR_LOKALU": NR_LOKALU,
            "KOD_POCZTOWY": KOD_POCZTOWY,
            "MIASTO": MIASTO,
            "AKTUALNOSC": aktualnosc_danych,
            "ID_DZIALKI": ID_DZIALKI,
            "UDZIAL": UDZIAL,
            "RODZAJ_WLASNOSCI": RODZAJ_WLASNOSCI,
        }

        important_keys = ["SWDE_NAZWA", "PESEL"]
        keys_to_check = [
            "SWDE_NAZWA",
            "IMIE_OJCA",
            "IMIE_MATKI",
            "PESEL",
            "NIP",
            "SWDE_ADRES",
        ]

        new_row = find_similar_record(
            df, imported_values, keys=keys_to_check, critical_keys=important_keys
        )
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        print_import_message(
            new_row,
            [
                "LP",
                "ID_ZASTAPIENIA",
                "SWDE_NAZWA",
                "IMIE_OJCA",
                "IMIE_MATKI",
                "TYP_OSOBY",
                "PESEL",
                "NIP",
                "ULICA",
                "NR_DOMU",
                "NR_LOKALU",
                "KOD_POCZTOWY",
                "MIASTO",
            ],
        )
        # dodaj kod pocztowy do słownika
        kody_pocztowe[MIASTO] = KOD_POCZTOWY

    return df


filename = r"D:\Python\kuba\zawiadomienia\import\5.11.2024\wlasc.xlsx"
df_main = create_base_from_excel(filename, "2024.11.5")

df_relacje = df_main[
    ["ID_ZASTAPIENIA", "ID_ORYGINALNE", "ID_DZIALKI", "UDZIAL", "RODZAJ_WLASNOSCI"]
]
df_osoby = df_main[
    [
        "ID_ZASTAPIENIA",
        "ID_ORYGINALNE",
        "SWDE_NAZWA",
        "SWDE_ADRES",
        "NAZWA",
        "PESEL",
        "IMIE_OJCA",
        "IMIE_MATKI",
        "TYP_OSOBY",
        "ADRES",
        "ULICA",
        "NR_DOMU",
        "NR_LOKALU",
        "KOD_POCZTOWY",
        "MIASTO",
    ]
]

# ZAPIS DO EXCELA
os.makedirs("db", exist_ok=True)
with pd.ExcelWriter(os.path.join("db", "baza.xlsx")) as writer:
    df_osoby.to_excel(writer, sheet_name="OSOBY")
    df_relacje.to_excel(writer, sheet_name="RELACJE")
end = time.time()
print(f"czas wykonania: {end-start:.4f} sekund")
