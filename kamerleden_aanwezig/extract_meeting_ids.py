# Description: Extracts the meeting ID from the JSON response of the API
#
# :param content: The content of the most recent 'vergaderverslag'
# :return: The ID and Type of the most recent 'vergaderverslag'
#

import json
from colorama import Fore, Style


def print_and_ask_verslagen(value):
    """
    Print de beschikbare 'vergaderverslagen' en vraag om een keuze
    
    :param value: De 'value' van de response van de API
    :return: De ID(s) van het gekozen 'vergaderverslag'
    """
    header_length = 38 + 35 + 30 + 18 + 17 + 5 * 2
    
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Fore.WHITE}{Style.BRIGHT}{'Beschikbare "vergaderverslagen"':^{header_length-2}}{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}| {'ID':<38}| {'GewijzigdOp':<35}| {'ApiGewijzigdOp':<30}| {'Soort':<18}| {'Status':<16}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    
    for item in value:
        print(
            f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.BLUE}{item['Id']:<37}{Style.RESET_ALL}",
            f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.GREEN}{item['GewijzigdOp']:<34}{Style.RESET_ALL}",
            f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.YELLOW}{item['ApiGewijzigdOp']:<29}{Style.RESET_ALL}",
            f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.CYAN}{item['Soort']:<17}{Style.RESET_ALL}",
            f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.MAGENTA}{item['Status']:<15}{Style.RESET_ALL}",
            f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}",
        )
        
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{'Kies een "vergaderverslag" door het ID in te voeren:':<145}{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|     -{Style.RESET_ALL} Druk op '{Fore.RED}Enter{Style.RESET_ALL}'{' om de meest recente "vergaderverslag" te kiezen;':<124}{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|     -{Style.RESET_ALL} Gebruik '{Fore.RED},{Style.RESET_ALL}'{' om meerdere ID\'s te scheiden;':<128}{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|     -{Style.RESET_ALL} Mogelijk gedeeltelijke ID\'s toegestaan: bijv. '{Fore.BLUE}d1a14aed{Style.RESET_ALL}' in plaats van '{Fore.BLUE}d1a14aed-1bd3-4aac-9ae5-2533288f2320{Style.RESET_ALL}';{'':<29}{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|     -{Style.RESET_ALL} Gebruik '{Fore.RED}all{Style.RESET_ALL}'{' om alle "vergaderverslagen" te kiezen;' + '':<126}{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|     -{Style.RESET_ALL} Gebruik '{Fore.RED}exit{Style.RESET_ALL}'{' om te stoppen;' + '':<125}{Style.RESET_ALL}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Voorbeeld: {Fore.BLUE}d1a14aed{Style.RESET_ALL}{Fore.RED},{Style.RESET_ALL}{Fore.BLUE}813667dd{Style.RESET_ALL}{Fore.RED},{Style.RESET_ALL}{Fore.BLUE}1b927ea0{Style.RESET_ALL}{'':<108}{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    
    # TODO: Print de input line opnieuw als de gebruiker een foutieve input geeft
    # TODO: Print de input line opnieuw als de gebruiker klaar is, om een '|' aan het einde te printen
    meeting_ids = input(f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}ID(s): {Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")

    return meeting_ids


def extract_meeting_ids(content):
    """
    Haalt 'Vergaderverslag' ID uit JSON

    :param content: De inhoud van het meest recente 'vergaderverslag'
    :return: Het ID en Soort van het meest recente 'vergaderverslag'
    """
    data = json.loads(content)
    value = data["value"]
    if len(value) == 0:
        raise Exception("Geen 'value' gevonden in de response van de API")

    # Print de beschikbare 'vergaderverslagen' en vraag om een keuze
    meeting_ids = print_and_ask_verslagen(value)

    if meeting_ids == "":
        # Als meeting_ids leeg is, return het meest recente 'vergaderverslag'
        return [(value[0]["Id"], value[0]["Soort"])]
    elif meeting_ids.lower() == "all":
        # Als meeting_ids 'all' is, return alle 'vergaderverslagen'
        return [(item["Id"], item["Soort"]) for item in value]
    elif meeting_ids.lower() == "exit":
        # Als meeting_ids 'exit' is, stop het programma
        raise SystemExit

    # Als er meerdere ID's zijn ingevoerd, split deze op komma's
    meeting_ids = meeting_ids.split(",")
    matching_meeting_ids = []

    # Kijk of de ingevoerde ID's overeenkomen met de ID's
    for input_id in meeting_ids:
        matching_ids = [item["Id"] for item in value if input_id in item["Id"]]
        if len(matching_ids) == 1:
            # Als er maar 1 ID overeenkomt, voeg deze toe aan de lijst
            matching_meeting_ids.append((matching_ids[0], value[0]["Soort"])) # TODO: Check if value[0] is correct
        elif len(matching_ids) > 1:
            # Als er meerdere ID's overeenkomen, print deze
            print(
                f"Er zijn meerdere vergaderverslagen die overeenkomen met '{input_id}':"
            )
            for matching_id in matching_ids:
                print(f"- {matching_id}")
            # TODO: Vraag om bevestiging / keuze
            confirm = input("Wil je doorgaan met deze vergaderverslagen? (ja/nee): ")
            if confirm.lower() == "ja":
                for matching_id in matching_ids:
                    matching_meeting_ids.append((matching_id, value[0]["Soort"])) # TODO: Check if value[0] is correct

    return matching_meeting_ids


