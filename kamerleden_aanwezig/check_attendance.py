# Description: Check de aanwezigheid van Kamerleden
#
# :param attendance_list: Een lijst van Kamerleden die aanwezig waren
# :return: Een lijst van Kamerleden die aanwezig waren
#

from colorama import Fore, Style
import os
from kamerleden_aanwezig import FILES_DIR


def check_names(alle_kamerleden, voor_en_achternamen):
    """
    Check of de namen van de Kamerleden overeenkomen met de namen in de lijst

    :param alle_kamerleden: Een lijst van alle Kamerleden
    :param voor_en_achternamen: Een lijst van voor en achternamen
    :return: Een lijst van voor en achternamen
    """
    # Fix kamerleden aantal in voor_en_achternamen
    if len(alle_kamerleden) != len(voor_en_achternamen):
        # Check of de voor en achternaam ook kamerleden zijn
        for voor_en_achternaam in voor_en_achternamen:
            # Alleen achternaam, zonder voornaam en naar lowercase
            temp_achternaam = voor_en_achternaam.split(" ", 1)[1].strip().lower()
            # Alleen achternaam, zonder voornaam en naar lowercase, zonder
            # whitespace
            temp_achternaam_1 = (
                voor_en_achternaam.split(" ", 1)[1].strip().lower().replace(" ", "")
            )
            # Naam zonder whitespace en naar lowercase
            temp_achternaam_2 = voor_en_achternaam.strip().lower().replace(" ", "")
            # Alleen achternaam, zonder voornaam en naar lowercase, zonder
            # whitespace en dash
            temp_achternaam_3 = (
                voor_en_achternaam.split(" ", 1)[1]
                .strip()
                .lower()
                .replace(" ", "")
                .replace("-", "")
            )
            # Alleen achternaam, zonder voornaam en naar lowercase, zonder
            # whitespace en zonder gedeelte achter de dash
            temp_achternaam_4 = (
                voor_en_achternaam.split(" ", 1)[1]
                .strip()
                .lower()
                .replace(" ", "")
                .split("-")[0]
            )
            # Sommige namen zijn langer of korter vanwege dubbele
            # achternamen
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
                if len(alle_kamerleden) == 150:  # Aantal kamerleden in 2dekmrledn.txt
                    print(
                        f"[check_names()] {voor_en_achternaam} is niet gevonden. Mogelijk een typefout of geen Kamerlid? {temp_achternaam}, {temp_achternaam_1}, {temp_achternaam_2}, {temp_achternaam_3} en {temp_achternaam_4} zijn geprobeerd."
                    )
                # Verwijder de voor en achternaam uit voor_en_achternamen
                voor_en_achternamen.remove(voor_en_achternaam)

    return voor_en_achternamen


def print_afwezige_kamerleden(
    alle_kamerleden, aanwezige_kamerleden, vergaderverslag_id
):
    """
    Print de afwezige Kamerleden

    :param alle_kamerleden: Een lijst van alle Kamerleden
    :param aanwezige_kamerleden: Een lijst van Kamerleden die aanwezig waren
    """
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
        voor_en_achternamen = check_names(alle_kamerleden, voor_en_achternamen)

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

    header_length = 38 + 35 + 30 + 18 + 17 + 5 * 2

    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(
        f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Style.BRIGHT}{'Afwezige Kamerleden':^{header_length - 2}}{Fore.BLACK}|{Style.RESET_ALL}"
    )
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    # Breedste weergavenaam: faber-vandeklashorst (20)
    print(
        f"{Fore.BLACK}{Style.BRIGHT}| {Style.RESET_ALL}{'Weergavenaam':<44}{'Voornaam':<44}{'Achternaam':<44}{'Partij':<13}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}"
    )
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")

    for kamerlid in alle_kamerleden:
        if kamerlid[0] not in aanwezige_kamerleden:
            if not isinstance(kamerlid, tuple):
                weergavenaam = kamerlid
                voornaam = achternaam = partij = ""
            else:
                weergavenaam, voornaam, achternaam, partij = kamerlid
            print(
                f"{Fore.BLACK}{Style.BRIGHT}| {Style.RESET_ALL}{weergavenaam:<44}{voornaam:<44}{achternaam:<44}{partij:<13}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}"
            )

    # print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    # print(
    #     f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Style.BRIGHT}{f'Einde ({vergaderverslag_id})':^{header_length - 2}}{Fore.BLACK}|{Style.RESET_ALL}"
    # )
    # print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")


def print_aanwezige_kamerleden(aanwezige_kamerleden, vergaderverslag_id):
    """
    Print de aanwezige Kamerleden

    :param aanwezige_kamerleden: Een lijst van Kamerleden die aanwezig waren
    """
    if not isinstance(aanwezige_kamerleden[0], tuple):
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
        voor_en_achternamen = check_names(aanwezige_kamerleden, voor_en_achternamen)

        aanwezige_kamerleden = [
            (
                kamerlid,  # weergavenaam
                *voor_en_achternamen[aanwezige_kamerleden.index(kamerlid)].split(
                    " ", 1
                ),  # voornaam, achternaam
                "",  # partij
            )
            for kamerlid in aanwezige_kamerleden
        ]

    header_length = 38 + 35 + 30 + 18 + 17 + 5 * 2

    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(
        f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Style.BRIGHT}{'Aanwezige Kamerleden':^{header_length - 2}}{Fore.BLACK}|{Style.RESET_ALL}"
    )
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    # Breedste weergavenaam: faber-vandeklashorst (20)
    print(
        f"{Fore.BLACK}{Style.BRIGHT}| {Style.RESET_ALL}{'Weergavenaam':<44}{'Voornaam':<44}{'Achternaam':<44}{'Partij':<13}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}"
    )
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")

    for kamerlid in aanwezige_kamerleden:
        if not isinstance(kamerlid, tuple):
            weergavenaam = kamerlid
            voornaam = achternaam = partij = ""
        else:
            weergavenaam, voornaam, achternaam, partij = kamerlid
        print(
            f"{Fore.BLACK}{Style.BRIGHT}| {Style.RESET_ALL}{weergavenaam:<44}{voornaam:<44}{achternaam:<44}{partij:<13}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}"
        )

    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(
        f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Style.BRIGHT}{f'Einde ({vergaderverslag_id})':^{header_length - 2}}{Fore.BLACK}|{Style.RESET_ALL}"
    )
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")


def check_attendance(attendance_list, vergaderverslag_id):
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
    with open(os.path.join(FILES_DIR, "2dekmrledn.txt"), "r", encoding="utf-8") as file: # https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Persoon?$filter=Verwijderd%20eq%20false%20and%20(Functie%20eq%20%27Tweede%20Kamerlid%27)
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
        voor_en_achternamen = check_names(alle_kamerleden, voor_en_achternamen)
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
        print_afwezige_kamerleden(
            alle_kamerleden, aanwezige_kamerleden, vergaderverslag_id
        )
        print_aanwezige_kamerleden(aanwezige_kamerleden, vergaderverslag_id)
    else:
        # print("Geen Kamerleden aanwezig.")
        raise Exception("Geen Kamerleden aanwezig.")

    return aanwezige_kamerleden
