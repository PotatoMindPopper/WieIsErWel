# Description: Check de aanwezigheid van Kamerleden
#
# :param attendance_list: Een lijst van Kamerleden die aanwezig waren
# :return: Een lijst van Kamerleden die aanwezig waren
#

from colorama import Fore, Style
import os
from kamerleden_aanwezig import FILES_DIR


def print_afwezige_kamerleden(alle_kamerleden, aanwezige_kamerleden):
    """
    Print de afwezige Kamerleden

    :param alle_kamerleden: Een lijst van alle Kamerleden
    :param aanwezige_kamerleden: Een lijst van Kamerleden die aanwezig waren
    """
    header_length = 38 + 35 + 30 + 18 + 17 + 5 * 2

    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(
        f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Style.BRIGHT}{'Afwezige Kamerleden':^{header_length - 2}}{Fore.BLACK}|{Style.RESET_ALL}"
    )
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(
        f"{Fore.BLACK}{Style.BRIGHT}| {Style.RESET_ALL}{'Weergavenaam':<44}{'Voornaam':<44}{'Achternaam':<44}{'Partij':<13}{Fore.BLACK}|{Style.RESET_ALL}"
    )
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")

    if not isinstance(alle_kamerleden[0], tuple):
        with open(os.path.join(FILES_DIR, "file.txt"), "r", encoding="utf-8") as file:
            voor_en_achternamen = [line.strip() for line in file.readlines()]
        # Voorbeeld van 2dekmrledn.txt:
        # aardema
        # aartsen
        # elabassi
        # agema
        # vanbaarle
        # bamenga
        # ...

        # Voorbeeld van file.txt:
        # Max Aardema
        # Thierry Aartsen
        # Ismail el Abassi
        # Fleur Agema
        # Stephan van Baarle
        # Mpanzu Bamenga
        # ...

        # Fix kamerleden aantal in voor_en_achternamen
        if len(alle_kamerleden) != len(voor_en_achternamen):
            # Check of de voor en achternaam ook kamerleden zijn
            for voor_en_achternaam in voor_en_achternamen:
                # Alleen achternaam, zonder voornaam en naar lowercase
                temp_achternaam = voor_en_achternaam.split(" ", 1)[1].strip().lower()
                # Alleen achternaam, zonder voornaam en naar lowercase, zonder whitespace
                temp_achternaam_1 = (
                    voor_en_achternaam.split(" ", 1)[1].strip().lower().replace(" ", "")
                )
                # Naam zonder whitespace en naar lowercase
                temp_achternaam_2 = voor_en_achternaam.strip().lower().replace(" ", "")
                # Alleen achternaam, zonder voornaam en naar lowercase, zonder whitespace en dash
                temp_achternaam_3 = (
                    voor_en_achternaam.split(" ", 1)[1]
                    .strip()
                    .lower()
                    .replace(" ", "")
                    .replace("-", "")
                )
                # Alleen achternaam, zonder voornaam en naar lowercase, zonder whitespace en zonder gedeelte achter de dash
                temp_achternaam_4 = (
                    voor_en_achternaam.split(" ", 1)[1]
                    .strip()
                    .lower()
                    .replace(" ", "")
                    .split("-")[0]
                )
                # Sommige namen zijn langer of korter vanwege dubbele achternamen
                for kamerlid in alle_kamerleden:
                    # Probeer de voor en achternaam te vinden in de kamerleden
                    if (
                        temp_achternaam in kamerlid
                        or temp_achternaam_1 in kamerlid
                        or temp_achternaam_2 in kamerlid
                        or temp_achternaam_3 in kamerlid
                        or temp_achternaam_4 in kamerlid
                    ):
                        break
                else:
                    print(
                        f"[print_afwezige_kamerleden()] {voor_en_achternaam} is niet gevonden. {temp_achternaam}, {temp_achternaam_1}, {temp_achternaam_2}, {temp_achternaam_3} en {temp_achternaam_4} zijn niet in {alle_kamerleden}"
                    )
                    # Verwijder de voor en achternaam uit voor_en_achternamen
                    voor_en_achternamen.remove(voor_en_achternaam)

        alle_kamerleden = [
            (
                kamerlid,  # weergavenaam
                *voor_en_achternamen[alle_kamerleden.index(kamerlid)].split(
                    " ", 1
                ),  # voornaam, achternaam
                "",  # partij
            )
            for kamerlid in alle_kamerleden
        ]

    for kamerlid in alle_kamerleden:
        if kamerlid[0] not in aanwezige_kamerleden:
            if not isinstance(kamerlid, tuple):
                weergavenaam = kamerlid
                voornaam = achternaam = partij = ""
            else:
                weergavenaam, voornaam, achternaam, partij = kamerlid
            print(
                f"{Fore.BLACK}{Style.BRIGHT}| {Style.RESET_ALL}{weergavenaam:<44}{voornaam:<44}{achternaam:<44}{partij:<13}{Fore.BLACK}|{Style.RESET_ALL}"
            )

    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(
        f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Style.BRIGHT}{'Einde':^{header_length - 2}}{Fore.BLACK}|{Style.RESET_ALL}"
    )
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")


def check_attendance(attendance_list):
    """
    Controleert aanwezigheid

    :param attendance_list: Een lijst van Kamerleden die aanwezig waren
    :return: Een lijst van Kamerleden die aanwezig waren
    """
    # Check of er iets in de lijst zit
    if (
        not attendance_list
        or len(attendance_list) == 0
        or attendance_list == [""]
        or attendance_list[0] == ""
    ):
        raise Exception("Geen Kamerleden gevonden.")

    # Check of er geen dubbele namen in de lijst zitten
    if len(attendance_list) != len(set(attendance_list)):
        raise Exception(
            f"Er zitten dubbele namen in de lijst. ({len(attendance_list)} != {len(set(attendance_list))})"
        )

    print("[check_attendance()] Aantal Kamerleden:", len(attendance_list))  # Debugging
    print("[check_attendance()] Kamerleden:", attendance_list)  # Debugging

    # Lees de namen van de Kamerleden
    alle_kamerleden = []
    with open(os.path.join(FILES_DIR, "2dekmrledn.txt"), "r", encoding="utf-8") as file:
        # Voorbeeld van 2dekmrledn.txt:
        # aardema
        # aartsen
        # elabassi
        # agema
        # vanbaarle
        # bamenga
        # ...
        alle_kamerleden = file.read().splitlines()

    # Check of attendance_list een lijst van tuples is
    if not isinstance(attendance_list[0], tuple):
        with open(os.path.join(FILES_DIR, "file.txt"), "r", encoding="utf-8") as file:
            # Voorbeeld van file.txt:
            # Max Aardema
            # Thierry Aartsen
            # Ismail el Abassi
            # Fleur Agema
            # Stephan van Baarle
            # ...
            voor_en_achternamen = [line.strip() for line in file.readlines()]
        attendance_list = [
            (
                kamerlid,
                *voor_en_achternamen[attendance_list.index(kamerlid)].split(" "),
                "",
            )
            for kamerlid in attendance_list
        ]

    # Check of de Kamerleden in de lijst zitten
    aanwezige_kamerleden = []
    for kamerlid in attendance_list:
        if (
            kamerlid[0] in alle_kamerleden
        ):  # TODO: Improve this, because sometimes `('haasen van', 'Peter', 'Haasen van', 'PVV')` is `vanhaasen` in 2dekmrledn.txt
            aanwezige_kamerleden.append(kamerlid[0])
        else:
            print(
                f"[check_attendance()] {kamerlid} is niet gevonden. Mogelijk een typefout of geen Kamerlid?"
            )

    print(
        "[check_attendance()] Aantal aanwezige Kamerleden:", len(aanwezige_kamerleden)
    )  # Debugging
    print(
        "[check_attendance()] Aanwezige Kamerleden:", aanwezige_kamerleden
    )  # Debugging

    # Print de afwezige Kamerleden als er Kamerleden aanwezig waren
    if len(aanwezige_kamerleden) != 0:
        print_afwezige_kamerleden(alle_kamerleden, aanwezige_kamerleden)
    else:
        # print("Geen Kamerleden aanwezig.")
        raise Exception("Geen Kamerleden aanwezig.")

    return aanwezige_kamerleden
