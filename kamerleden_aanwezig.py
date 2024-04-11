import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta
from colorama import Fore, Style


def fetch_file():
    """
    Haalt het meest recente 'vergaderverslag' op van de Tweede Kamer API

    Omdat het meest recente 'vergaderverslag' vaak pas de volgende dag wordt
    gepubliceerd, wordt de datum van gisteren gebruikt om het meest recente
    'vergaderverslag' op te halen.

    :return: De inhoud van het meest recente 'vergaderverslag'
    """
    yesterday = datetime.now() - timedelta(days=1)
    year, month, day = yesterday.year, yesterday.month, yesterday.day

    day = 11  # Debugging

    # Voorbeeld van een response zonder 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[]}
    # Voorbeeld van een response met 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[{"Id":"8176b1f5-b5a8-46f1-9d2c-5e66fd14604f","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":92511,"GewijzigdOp":"2024-04-09T20:08:55.5222825+02:00","ApiGewijzigdOp":"2024-04-10T10:06:34.0095628Z","Verwijderd":false,"Vergadering_Id":"7b123e97-8255-4ac9-adb8-da471891ebca"}]}
    # Voorbeeld van een response met meer dan 1 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[{"Id":"3849ce47-0ccb-417d-b883-7c13f31900e5","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":8614,"GewijzigdOp":"2024-04-05T11:27:48.3707026+02:00","ApiGewijzigdOp":"2024-04-05T09:30:02.6745625Z","Verwijderd":false,"Vergadering_Id":"099c5fab-95f1-407b-bf3c-87e9341e6172"},{"Id":"db2dd399-803b-4147-a92c-ebccdf21d23d","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":8614,"GewijzigdOp":"2024-04-05T08:37:03.0559843+02:00","ApiGewijzigdOp":"2024-04-05T06:37:33.2206437Z","Verwijderd":false,"Vergadering_Id":"099c5fab-95f1-407b-bf3c-87e9341e6172"}]}
    # Voorbeeld van een response met compleet 'vergaderverslag':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[{"Id":"7dedd180-7475-4ef4-be81-01963f6e8906","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":173379,"GewijzigdOp":"2024-04-04T10:08:22.7466935+02:00","ApiGewijzigdOp":"2024-04-04T08:09:19.1204238Z","Verwijderd":false,"Vergadering_Id":"505319ed-705f-4f7d-b244-3794ea67ea9b"},{"Id":"bce9fc3c-ffb2-4332-9307-04742c39c35d","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1345672,"GewijzigdOp":"2024-04-04T23:22:52.0263598+02:00","ApiGewijzigdOp":"2024-04-04T21:23:51.237277Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"70b8c22e-871f-42c5-83d6-0ccc7870e980","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1353505,"GewijzigdOp":"2024-04-04T23:31:45.810932+02:00","ApiGewijzigdOp":"2024-04-04T21:35:29.574477Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"d1a14aed-1bd3-4aac-9ae5-2533288f2320","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":373072,"GewijzigdOp":"2024-04-04T15:45:06.1401037+02:00","ApiGewijzigdOp":"2024-04-04T13:45:48.1957918Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"813667dd-4fc7-47b0-8041-3ddb44fbe08b","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1167440,"GewijzigdOp":"2024-04-04T21:45:27.1564723+02:00","ApiGewijzigdOp":"2024-04-04T19:46:51.8415558Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"1b927ea0-ee03-4c30-960a-4b31d8ed8555","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1046537,"GewijzigdOp":"2024-04-04T00:01:12.3852858+02:00","ApiGewijzigdOp":"2024-04-03T22:02:06.9234256Z","Verwijderd":false,"Vergadering_Id":"c212f69a-b79b-4b71-87b4-451a564447c9"},{"Id":"010218a6-9fc3-4c5e-84bf-6bb5e8d18d12","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":808757,"GewijzigdOp":"2024-04-04T19:01:39.6860091+02:00","ApiGewijzigdOp":"2024-04-04T17:02:31.0019271Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"31f3a717-762e-4345-a33b-72052e89c3d5","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1084760,"GewijzigdOp":"2024-04-04T20:32:01.5252439+02:00","ApiGewijzigdOp":"2024-04-04T18:32:57.1520866Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"f1f71904-3bbd-4fe9-bf2b-7fc1baa7d06d","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":213454,"GewijzigdOp":"2024-04-04T14:06:07.8112692+02:00","ApiGewijzigdOp":"2024-04-04T12:07:20.4082851Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"f4ce5c17-97b0-491a-93b5-905d9b65794e","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":673169,"GewijzigdOp":"2024-04-04T17:19:22.5851193+02:00","ApiGewijzigdOp":"2024-04-04T15:20:57.1534537Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"c08d2c58-24b1-4406-ad26-cd236099a45b","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":278051,"GewijzigdOp":"2024-04-04T15:42:22.1291509+02:00","ApiGewijzigdOp":"2024-04-04T13:43:25.5592884Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"0e01ff58-9a64-478d-b5ba-d6bf429a6792","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":258603,"GewijzigdOp":"2024-04-04T16:09:17.1530587+02:00","ApiGewijzigdOp":"2024-04-04T14:11:41.5559455Z","Verwijderd":false,"Vergadering_Id":"fb33e864-a4d1-4d84-9409-1a5306a93953"},{"Id":"81fe53ce-ce31-4dba-843d-e0defc7a3368","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":118343,"GewijzigdOp":"2024-04-04T13:25:24.7639295+02:00","ApiGewijzigdOp":"2024-04-04T11:26:01.7020949Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"b690d8a7-3936-4510-a5d1-e2cd3d68e953","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":258355,"GewijzigdOp":"2024-04-04T14:40:13.8613895+02:00","ApiGewijzigdOp":"2024-04-04T12:41:42.0599952Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"4b1c6dc4-05aa-4c37-b96c-e31074bdfde4","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1067931,"GewijzigdOp":"2024-04-04T00:24:07.6390733+02:00","ApiGewijzigdOp":"2024-04-03T22:27:12.8167896Z","Verwijderd":false,"Vergadering_Id":"c212f69a-b79b-4b71-87b4-451a564447c9"},{"Id":"3a1a1c06-fdae-4030-87d0-edd5e183e0e6","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1249433,"GewijzigdOp":"2024-04-04T22:40:02.787392+02:00","ApiGewijzigdOp":"2024-04-04T20:41:10.5712446Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"d15e8b1c-4bdd-44bc-b963-f7ea6daf451f","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":541473,"GewijzigdOp":"2024-04-04T16:36:26.9966646+02:00","ApiGewijzigdOp":"2024-04-04T14:38:27.060681Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"}]}
    # Voorbeeld van een response met een error:
    # {"error":{"code":"","message":"The query specified in the URI is not valid. A binary operator with incompatible types was detected. Found operand types 'Edm.Int32' and 'Edm.String' for operator kind 'Equal'."}}

    while True:
        url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{year}%20and%20month(GewijzigdOp)%20eq%20{month}%20and%20day(GewijzigdOp)%20eq%20{day}"
        print("[fetch_file()] URL:", url)  # Debugging
        response = requests.get(url)
        data = response.json()

        if data["value"] and len(data["value"]) > 0:
            # Als value niet leeg is, return de content
            return response.content  # TODO: Return data["value"]
        elif data["value"] and len(data["value"]) == 0:
            # Als value leeg is, probeer de dag ervoor
            print(
                f"[fetch_file()] Geen 'vergaderverslag' gevonden voor {day}-{month}-{year}. Probeer de dag ervoor."
            )
            yesterday = yesterday - timedelta(days=1)
            year, month, day = yesterday.year, yesterday.month, yesterday.day
            print(f"[fetch_file()] Probeer {day}-{month}-{year}")
            # Wacht 1 seconde voordat de volgende fetch wordt uitgevoerd
            import time  # Importeer alleen als het nodig is

            time.sleep(1)
        else:
            # Als value niet bestaat, kijken of er een error is
            if "error" in data:
                raise Exception(data["error"]["message"])
            else:
                raise Exception(
                    "Geen 'value' gevonden in de response van de API"
                )  # Onbekende error

    return None


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


def fetch_reports(meeting_ids):
    """
    Haalt de inhoud van 'Vergaderverslag' op

    :param meeting_id: Het ID van het meest recente 'vergaderverslag'
    :return: De inhoud van het 'Vergaderverslag'
    """
    reports = []
    for meeting_id, meeting_type in meeting_ids: # TODO: Add meeting_date
        url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{meeting_id}/resource"
        print("[fetch_report()] URL:", url)  # Debugging
        response = requests.get(url)
        content = response.content
        reports.append((content, meeting_type))
    return reports


def parse_voorpublicatie(report):
    """
    Parseert de 'Voorpublicatie' ontvangen van de API

    :param report: De inhoud van de 'Voorpublicatie'
    :return: Een lijst van Kamerleden die aanwezig waren
    """
    try:
        root = ET.fromstring(report.decode())
    except ET.ParseError:
        raise Exception("Fout bij het parsen van XML")

    namespace = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}

    # Ga op zoek naar alle sprekers
    speakers = root.findall(".//ns:spreker", namespaces=namespace)

    # Kijk naar dubbele namen. Gebruik hiervoor de "objectid" om te kijken
    # of het dezelfde persoon is
    kamerleden = {}
    for speaker in speakers:
        # objectid = speaker.find(".//ns:objectid", namespaces=namespace).text
        # objectid = speaker.attrib["objectid"]
        objectid = speaker.get("objectid")
        weergavenaam = speaker.find(".//ns:weergavenaam", namespaces=namespace).text
        if objectid not in kamerleden:
            functie = speaker.find(".//ns:functie", namespaces=namespace).text
            if functie.lower().startswith("lid tweede kamer") or speaker.get("Soort") == "Tweede Kamerlid":
                # Als de functie begint met "lid Tweede Kamer" of de Soort
                # "Tweede Kamerlid" is, voeg deze toe aan de lijst
                # TODO: Voeg weergavenaam, voornaam, achternaam, partij toe
                kamerleden[objectid] = (
                    weergavenaam.lower().strip(), 
                    speaker.find(".//ns:voornaam", namespaces=namespace).text, 
                    speaker.find(".//ns:achternaam", namespaces=namespace).text, 
                    speaker.find(".//ns:fractie", namespaces=namespace).text
                )

    return list(kamerleden.values())


def parse_tussenpublicatie(report):
    """
    Parseert de 'Tussenpublicatie' ontvangen van de API

    :param report: De inhoud van de 'Tussenpublicatie'
    :return: Een lijst van Kamerleden die aanwezig waren
    """
    try:
        root = ET.fromstring(report.decode())
    except ET.ParseError:
        raise Exception("Fout bij het parsen van XML")

    namespace = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
    paragraphs = root.findall(".//ns:alineaitem", namespaces=namespace)
    for paragraph in paragraphs:
        if "leden der Kamer, te weten:" in str(paragraph.text):
            try:
                aantal_kamerleden = int(paragraph.text.split("Aanwezig zijn ")[1].split("leden der Kamer, te weten:")[0].strip())
            except ValueError:
                aantal_kamerleden = 0

            if aantal_kamerleden == 0:
                return parse_voorpublicatie(report)
            
            # Check of de volgende alinea een lijst van Kamerleden is
            if paragraph.text.split("leden der Kamer, te weten:")[1].strip() != "":
                return (
                    paragraph.text.split("leden der Kamer, te weten:")[1]
                    .strip()  # Verwijder spaties aan het begin en einde
                    .lower()  # Verander naar lowercase
                    .replace(" en ", ",")  # Verander " en " naar ","
                    .replace(" ", "")  # Verwijder spaties
                    .rstrip(",")  # Verwijder laatste komma
                    .split(",")  # Split op komma's
                )
            elif paragraphs[paragraphs.index(paragraph) + 1].text and paragraphs[paragraphs.index(paragraph) + 1].text.strip() != "":
                return (
                    paragraphs[paragraphs.index(paragraph) + 1].text
                    .strip()  # Verwijder spaties aan het begin en einde
                    .lower()  # Verander naar lowercase
                    .replace(" en ", ",")  # Verander " en " naar ","
                    .replace(" ", "")  # Verwijder spaties
                    .rstrip(",")  # Verwijder laatste komma
                    .split(",")  # Split op komma's
                )
            else:
                return parse_voorpublicatie(report)
    return parse_voorpublicatie(report)


def parse_xml(report):
    """
    Parseert de XML ontvangen van de API

    :param report: De inhoud van het 'Vergaderverslag'
    :return: Een lijst van Kamerleden die aanwezig waren
    """

    # Voorbeeld van een XML:
    # <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    # <vlosCoreDocument MessageID="d10950e7-e8b6-479a-9381-ab19423d7502" Source="VLOS2.0"
    #     MessageType="vlos2document" Timestamp="2024-04-09T20:08:55.5222825+02:00" soort="Voorpublicatie"
    #     status="Casco" technischeaanpassing="false" publiceren="Ja" versie="1.3"
    #     xmlns="http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0">
    #     <vergadering soort="Commissie" objectid="f96c0d62-dcba-4f8b-9ee1-f56c08e167d7"
    #         kamer="Tweede Kamer">
    #         <titel>Klimaat Caribisch deel Koninkrijk</titel>
    #         <zaal>Troelstrazaal</zaal>
    #         <vergaderjaar>2023-2024</vergaderjaar>
    #         <vergaderingnummer>0</vergaderingnummer>
    #         <datum>2024-04-09T00:00:00</datum>
    #         <aanvangstijd>2024-04-09T16:30:00</aanvangstijd>
    #         <sluiting>2024-04-09T18:18:40</sluiting>
    #         <activiteit soort="Opening" objectid="93e35a2d-f107-4305-930c-7ad7eb97ecbe">
    #             <titel>Opening</titel>
    #             <onderwerp>Opening</onderwerp>
    #             <parlisid />
    #             <aanvangstijd>2024-04-09T16:31:18</aanvangstijd>
    #             <eindtijd>2024-04-09T16:31:21</eindtijd>
    #             <voortzetting>false</voortzetting>
    #             <activiteithoofd soort="Algemeen" objectid="4fca858e-687f-4a17-8ebf-381b0801834e">
    #                 <titel>Opening</titel>
    #                 <onderwerp>Opening</onderwerp>
    #                 <markeertijdbegin>2024-04-09T16:31:18</markeertijdbegin>
    #                 <markeertijdeind>2024-04-09T16:31:21</markeertijdeind>
    #                 <draadboekfragment soort="Voorzitter selectie"
    #                     objectid="f1bc69b1-2997-4063-b6f8-712d19990ba0">
    #                     <markeertijdbegin>2024-04-09T16:31:19</markeertijdbegin>
    #                     <markeertijdeind>2024-04-09T16:31:20</markeertijdeind>
    #                     <isdraad>true</isdraad>
    #                     <sprekers>
    #                         <spreker soort="Tweede Kamerlid"
    #                             objectid="c284355b-902b-4073-a057-24daec031e39">
    #                             <fractie>D66</fractie>
    #                             <aanhef>De heer</aanhef>
    #                             <verslagnaam>Paternotte</verslagnaam>
    #                             <weergavenaam>Paternotte</weergavenaam>
    #                             <voornaam>Jan</voornaam>
    #                             <achternaam>Paternotte</achternaam>
    #                             <functie>lid Tweede Kamer</functie>
    #                         </spreker>
    #                     </sprekers>
    #                 </draadboekfragment>
    #             </activiteithoofd>
    #         </activiteit>
    #         <activiteit soort="Commissiedebat" objectid="4674b6c2-7b24-4566-b048-099db62ebd00">
    #             <titel>Klimaat Caribisch deel Koninkrijk</titel>
    #             <onderwerp>Klimaat Caribisch deel Koninkrijk</onderwerp>
    #             <parlisid>2023A07965</parlisid>
    #             <aanvangstijd>2024-04-09T16:31:21</aanvangstijd>
    #             <eindtijd>2024-04-09T18:18:36</eindtijd>
    #             <voortzetting>false</voortzetting>
    #             <activiteitenindex>
    #                 <category>Internationaal | Organisatie en beleid</category>
    #                 <category>Natuur en milieu | Organisatie en beleid</category>
    #             </activiteitenindex>
    #             <activiteithoofd soort="Algemeen" objectid="93d50a92-c99c-4176-8455-17fbbed9facd">
    #                 <titel>Klimaat Caribisch deel Koninkrijk</titel>
    #                 <onderwerp>Klimaat Caribisch deel Koninkrijk</onderwerp>
    #                 <markeertijdbegin>2024-04-09T16:31:21</markeertijdbegin>
    #                 <markeertijdeind>2024-04-09T18:18:36</markeertijdeind>
    #                 <activiteitdeel soort="Spreekbeurt" objectid="d0ba6b8e-2c6f-4851-8c6d-147f341d1c13">
    #                     <spreker soort="Tweede Kamerlid" objectid="c284355b-902b-4073-a057-24daec031e39">
    #                         <fractie>D66</fractie>
    #                         <aanhef>De heer</aanhef>
    #                         <verslagnaam>Paternotte</verslagnaam>
    #                         <weergavenaam>Paternotte</weergavenaam>
    #                         <voornaam>Jan</voornaam>
    #                         <achternaam>Paternotte</achternaam>
    #                         <functie>lid Tweede Kamer</functie>
    #                     </spreker>
    #                     <titel>Spreekbeurt - De voorzitter</titel>
    #                     <markeertijdbegin>2024-04-09T16:31:22</markeertijdbegin>
    #                     <markeertijdeind>2024-04-09T16:32:05</markeertijdeind>
    #                     <activiteititem soort="Woordvoerder"
    #                         objectid="3e314437-24ea-4dad-99f2-5c31b920a674">
    #                         <titel>Woordvoerder - De voorzitter</titel>
    #                         <markeertijdbegin>2024-04-09T16:31:22</markeertijdbegin>
    #                         <markeertijdeind>2024-04-09T16:32:05</markeertijdeind>
    #                         <woordvoerder objectid="5d363f0d-9486-445b-999f-9bd98c5d0d56">
    #                             <spreker soort="Tweede Kamerlid"
    #                                 objectid="c284355b-902b-4073-a057-24daec031e39">
    #                                 <fractie>D66</fractie>
    #                                 <aanhef>De heer</aanhef>
    #                                 <verslagnaam>Paternotte</verslagnaam>
    #                                 <weergavenaam>Paternotte</weergavenaam>
    #                                 <voornaam>Jan</voornaam>
    #                                 <achternaam>Paternotte</achternaam>
    #                                 <functie>lid Tweede Kamer</functie>
    #                             </spreker>
    #                             <markeertijdbegin>2024-04-09T16:31:22</markeertijdbegin>
    #                             <markeertijdeind>2024-04-09T16:32:05</markeertijdeind>
    #                             <isvoorzitter>true</isvoorzitter>
    #                             <isdraad>false</isdraad>
    #                             <tekst />
    #                         </woordvoerder>
    #                     </activiteititem>
    #                 </activiteitdeel>
    #                 <activiteitdeel soort="Spreekbeurt" objectid="5e7db250-391b-4c73-ad7c-b32b70e9fb4d">
    #                     <spreker soort="Tweede Kamerlid" objectid="8d489910-4c89-41c6-80ef-6e1bb8a2ea81">
    #                         <fractie>GroenLinks-PvdA</fractie>
    #                         <aanhef>De heer</aanhef>
    #                         <verslagnaam>White</verslagnaam>
    #                         <weergavenaam>White</weergavenaam>
    #                         <voornaam>Raoul</voornaam>
    #                         <achternaam>White</achternaam>
    #                         <functie>lid Tweede Kamer</functie>
    #                     </spreker>
    #                     <titel>Spreekbeurt - White</titel>
    #                     <markeertijdbegin>2024-04-09T16:32:05</markeertijdbegin>
    #                     <markeertijdeind>2024-04-09T16:37:16</markeertijdeind>
    #                     <activiteititem soort="Woordvoerder"
    #                         objectid="f8b13023-5849-4444-a2cb-1ac8b765eca5">
    #                         <titel>Woordvoerder - White</titel>
    #                         <markeertijdbegin>2024-04-09T16:32:05</markeertijdbegin>
    #                         <markeertijdeind>2024-04-09T16:37:16</markeertijdeind>
    #                         <woordvoerder objectid="b631d98f-ab34-4a9a-8a62-01ea3a0205df">
    #                             <spreker soort="Tweede Kamerlid"
    #                                 objectid="8d489910-4c89-41c6-80ef-6e1bb8a2ea81">
    #                                 <fractie>GroenLinks-PvdA</fractie>
    #                                 <aanhef>De heer</aanhef>
    #                                 <verslagnaam>White</verslagnaam>
    #                                 <weergavenaam>White</weergavenaam>
    #                                 <voornaam>Raoul</voornaam>
    #                                 <achternaam>White</achternaam>
    #                                 <functie>lid Tweede Kamer</functie>
    #                             </spreker>
    #                             <markeertijdbegin>2024-04-09T16:32:05</markeertijdbegin>
    #                             <markeertijdeind>2024-04-09T16:36:31</markeertijdeind>
    #                             <isvoorzitter>false</isvoorzitter>
    #                             <isdraad>false</isdraad>
    #                             <tekst />
    #                             <interrumpant objectid="7e96b978-14d4-4a42-96cc-205b24e9407a">
    #                                 <spreker soort="Tweede Kamerlid"
    #                                     objectid="c284355b-902b-4073-a057-24daec031e39">
    #                                     <fractie>D66</fractie>
    #                                     <aanhef>De heer</aanhef>
    #                                     <verslagnaam>Paternotte</verslagnaam>
    #                                     <weergavenaam>Paternotte</weergavenaam>
    #                                     <voornaam>Jan</voornaam>
    #                                     <achternaam>Paternotte</achternaam>
    #                                     <functie>lid Tweede Kamer</functie>
    #                                 </spreker>
    #                                 <markeertijdbegin>2024-04-09T16:36:28</markeertijdbegin>
    #                                 <markeertijdeind>2024-04-09T16:36:31</markeertijdeind>
    #                                 <isvoorzitter>true</isvoorzitter>
    #                                 <isdraad>false</isdraad>
    #                                 <tekst />
    #                             </interrumpant>
    #                         </woordvoerder>
    #                         <woordvoerder objectid="6513bfc7-f12a-4c62-8aa2-907b323335d7">
    #                             <spreker soort="Tweede Kamerlid"
    #                                 objectid="8d489910-4c89-41c6-80ef-6e1bb8a2ea81">
    #                                 <fractie>GroenLinks-PvdA</fractie>
    #                                 <aanhef>De heer</aanhef>
    #                                 <verslagnaam>White</verslagnaam>
    #                                 <weergavenaam>White</weergavenaam>
    #                                 <voornaam>Raoul</voornaam>
    #                                 <achternaam>White</achternaam>
    #                                 <functie>lid Tweede Kamer</functie>
    #                             </spreker>
    #                             <markeertijdbegin>2024-04-09T16:36:31</markeertijdbegin>
    #                             <markeertijdeind>2024-04-09T16:36:58</markeertijdeind>
    #                             <isvoorzitter>false</isvoorzitter>
    #                             <isdraad>false</isdraad>
    #                             <tekst />
    #                             <interrumpant objectid="e3b05c4a-9ba2-4437-bfb9-70bf1a32e4cb">
    #                                 <spreker soort="Tweede Kamerlid"
    #                                     objectid="c284355b-902b-4073-a057-24daec031e39">
    #                                     <fractie>D66</fractie>
    #                                     <aanhef>De heer</aanhef>
    #                                     <verslagnaam>Paternotte</verslagnaam>
    #                                     <weergavenaam>Paternotte</weergavenaam>
    #                                     <voornaam>Jan</voornaam>
    #                                     <achternaam>Paternotte</achternaam>
    #                                     <functie>lid Tweede Kamer</functie>
    #                                 </spreker>
    #                                 <markeertijdbegin>2024-04-09T16:36:57</markeertijdbegin>
    #                                 <markeertijdeind>2024-04-09T16:36:58</markeertijdeind>
    #                                 <isvoorzitter>true</isvoorzitter>
    #                                 <isdraad>false</isdraad>
    #                                 <tekst />
    #                             </interrumpant>
    #                         </woordvoerder>
    #                         <woordvoerder objectid="4c33dbfc-fac5-4bac-8e66-f55decebbaff">
    #                             <spreker soort="Tweede Kamerlid"
    #                                 objectid="8d489910-4c89-41c6-80ef-6e1bb8a2ea81">
    #                                 <fractie>GroenLinks-PvdA</fractie>
    #                                 <aanhef>De heer</aanhef>
    #                                 <verslagnaam>White</verslagnaam>
    #                                 <weergavenaam>White</weergavenaam>
    #                                 <voornaam>Raoul</voornaam>
    #                                 <achternaam>White</achternaam>
    #                                 <functie>lid Tweede Kamer</functie>
    #                             </spreker>
    #                             <markeertijdbegin>2024-04-09T16:36:58</markeertijdbegin>
    #                             <markeertijdeind>2024-04-09T16:37:07</markeertijdeind>
    #                             <isvoorzitter>false</isvoorzitter>
    #                             <isdraad>false</isdraad>
    #                             <tekst />
    #                             <interrumpant objectid="41f67e8a-b70d-4ac0-affc-fc67192077ec">
    #                                 <spreker soort="Tweede Kamerlid"
    #                                     objectid="c284355b-902b-4073-a057-24daec031e39">
    #                                     <fractie>D66</fractie>
    #                                     <aanhef>De heer</aanhef>
    #                                     <verslagnaam>Paternotte</verslagnaam>
    #                                     <weergavenaam>Paternotte</weergavenaam>
    #                                     <voornaam>Jan</voornaam>
    #                                     <achternaam>Paternotte</achternaam>
    #                                     <functie>lid Tweede Kamer</functie>
    #                                 </spreker>
    #                                 <markeertijdbegin>2024-04-09T16:37:06</markeertijdbegin>
    #                                 <markeertijdeind>2024-04-09T16:37:07</markeertijdeind>
    #                                 <isvoorzitter>true</isvoorzitter>
    #                                 <isdraad>false</isdraad>
    #                                 <tekst />
    #                             </interrumpant>
    #                         </woordvoerder>
    #                         <woordvoerder objectid="e14f44b8-f00b-46a6-aa71-ef408bb18032">
    #                             <spreker soort="Tweede Kamerlid"
    #                                 objectid="8d489910-4c89-41c6-80ef-6e1bb8a2ea81">
    #                                 <fractie>GroenLinks-PvdA</fractie>
    #                                 <aanhef>De heer</aanhef>
    #                                 <verslagnaam>White</verslagnaam>
    #                                 <weergavenaam>White</weergavenaam>
    #                                 <voornaam>Raoul</voornaam>
    #                                 <achternaam>White</achternaam>
    #                                 <functie>lid Tweede Kamer</functie>
    #                             </spreker>
    #                             <markeertijdbegin>2024-04-09T16:37:07</markeertijdbegin>
    #                             <markeertijdeind>2024-04-09T16:37:16</markeertijdeind>
    #                             <isvoorzitter>false</isvoorzitter>
    #                             <isdraad>false</isdraad>
    #                             <tekst />
    #                             <interrumpant objectid="097e9db0-bb17-4353-b527-bd7c324321d1">
    #                                 <spreker soort="Tweede Kamerlid"
    #                                     objectid="c284355b-902b-4073-a057-24daec031e39">
    #                                     <fractie>D66</fractie>
    #                                     <aanhef>De heer</aanhef>
    #                                     <verslagnaam>Paternotte</verslagnaam>
    #                                     <weergavenaam>Paternotte</weergavenaam>
    #                                     <voornaam>Jan</voornaam>
    #                                     <achternaam>Paternotte</achternaam>
    #                                     <functie>lid Tweede Kamer</functie>
    #                                 </spreker>
    #                                 <markeertijdbegin>2024-04-09T16:37:08</markeertijdbegin>
    #                                 <markeertijdeind>2024-04-09T16:37:16</markeertijdeind>
    #                                 <isvoorzitter>true</isvoorzitter>
    #                                 <isdraad>false</isdraad>
    #                                 <tekst />
    #                             </interrumpant>
    #                         </woordvoerder>
    #                     </activiteititem>
    #                 </activiteitdeel>
    # ...
    #     </vergadering>
    # </vlosCoreDocument>

    if report[1] == "Tussenpublicatie":
        # Check de meeting_type om te kijken of het een "makkelijk"
        # 'vergaderverslag' is
        return parse_tussenpublicatie(report[0])
    elif report[1] == "Voorpublicatie":
        # Check de meeting_type om te kijken of het een "moeilijk"
        # 'vergaderverslag' is
        return parse_voorpublicatie(report[0])
    else:
        raise Exception("Onbekend 'vergaderverslag' type")
    
    
def print_afwezige_kamerleden(attendance_list, alle_kamerleden, aanwezige_kamerleden):
    """
    Print de afwezige Kamerleden

    :param alle_kamerleden: Een lijst van alle Kamerleden
    :param aanwezige_kamerleden: Een lijst van Kamerleden die aanwezig waren
    """
    # print("----Afwezig:----")
    # for kamerlid in alle_kamerleden:
    #     if kamerlid not in aanwezige_kamerleden:
    #         print(kamerlid) # TODO: Print in tabelvorm
    
    header_length = 38 + 35 + 30 + 18 + 17 + 5 * 2
    
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Style.BRIGHT}{'Afwezige Kamerleden':^{header_length - 2}}{Fore.BLACK}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}| {Style.RESET_ALL}{'Weergavenaam':<44}{'Voornaam':<44}{'Achternaam':<44}{'Partij':<13}{Fore.BLACK}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    
    if not isinstance(alle_kamerleden[0], tuple): # Check of je alle_kamerleden moet hebben, of juist attendance_list
        # alle_kamerleden = [(kamerlid, "", "", "") for kamerlid in alle_kamerleden]
        with open("files/file.txt", "r", encoding="utf-8") as file:
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
        alle_kamerleden = [
            (
                kamerlid, # weergavenaam
                *voor_en_achternamen[alle_kamerleden.index(kamerlid)].split(" "), # voornaam, achternaam # TODO: This doens't work, due to whitespace in last name
                "" # partij
            ) 
            for kamerlid in alle_kamerleden
        ]

    for kamerlid in alle_kamerleden:
        if kamerlid[0] not in aanwezige_kamerleden:
            # print(kamerlid) # TODO: Print in tabelvorm
            # weergavenaam, voornaam, achternaam, partij = kamerlid.split(" - ") TODO: Voeg dit op andere plek toe aan de code
            if not isinstance(kamerlid, tuple):
                weergavenaam = kamerlid
                voornaam = achternaam = partij = "" # TODO: Haal voor en achternaam op uit file.txt of API
            else:
                weergavenaam, voornaam, achternaam, partij = kamerlid
            print(f"{Fore.BLACK}{Style.BRIGHT}| {Style.RESET_ALL}{weergavenaam:<44}{voornaam:<44}{achternaam:<44}{partij:<13}{Fore.BLACK}|{Style.RESET_ALL}")
        
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}|{Style.RESET_ALL}{Style.BRIGHT}{'Einde':^{header_length - 2}}{Fore.BLACK}|{Style.RESET_ALL}")
    print(f"{Fore.BLACK}{Style.BRIGHT}{'-' * header_length}{Style.RESET_ALL}")


def check_attendance(attendance_list):
    """
    Controleert aanwezigheid

    :param attendance_list: Een lijst van Kamerleden die aanwezig waren
    :return: Een lijst van Kamerleden die aanwezig waren
    """
    # Check of er iets in de lijst zit
    if not attendance_list or len(attendance_list) == 0 or attendance_list == [""] or attendance_list[0] == "":
        raise Exception("Geen Kamerleden gevonden.")
    
    # Check of er geen dubbele namen in de lijst zitten
    if len(attendance_list) != len(set(attendance_list)):
        raise Exception(f"Er zitten dubbele namen in de lijst. ({len(attendance_list)} != {len(set(attendance_list))})")
    
    print("[check_attendance()] Aantal Kamerleden:", len(attendance_list))  # Debugging
    print("[check_attendance()] Kamerleden:", attendance_list)  # Debugging
    
    # Lees de namen van de Kamerleden
    alle_kamerleden = []
    with open("files/2dekmrledn.txt", "r", encoding="utf-8") as file:
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
        with open("files/file.txt", "r", encoding="utf-8") as file:
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
                ""
            ) for kamerlid in attendance_list
        ]

    # Check of de Kamerleden in de lijst zitten
    aanwezige_kamerleden = []
    for kamerlid in attendance_list:
        if kamerlid[0] in alle_kamerleden: # TODO: Improve this, because sometimes `('haasen van', 'Peter', 'Haasen van', 'PVV')` is `vanhaasen` in 2dekmrledn.txt
            aanwezige_kamerleden.append(kamerlid[0])
        else:
            print(f"[check_attendance()] {kamerlid} is niet gevonden. Mogelijk een typefout of geen Kamerlid?")
    
    print("[check_attendance()] Aantal aanwezige Kamerleden:", len(aanwezige_kamerleden))  # Debugging
    print("[check_attendance()] Aanwezige Kamerleden:", aanwezige_kamerleden)  # Debugging
    
    # Print de afwezige Kamerleden als er Kamerleden aanwezig waren
    if len(aanwezige_kamerleden) != 0:
        print_afwezige_kamerleden(attendance_list, alle_kamerleden, aanwezige_kamerleden)
    else:
        # print("Geen Kamerleden aanwezig.")
        raise Exception("Geen Kamerleden aanwezig.")
    
    return aanwezige_kamerleden


def create_chart(attendance_list):
    """
    Maakt een grafiek die aangeeft wie aanwezig is en wie niet

    :param attendance_list: Een lijst van Kamerleden die aanwezig waren
    """
    # import matplotlib.pyplot as plt

    labels = ["Afwezig", "Aanwezig"]
    sizes = [150 - len(attendance_list), len(attendance_list)]
    colors = ["red", "green"]
    explode = (0.1, 0)  # explode 1st slice

    # plt.pie(
    #     sizes,
    #     explode=explode,
    #     labels=labels,
    #     colors=colors,
    #     autopct="%1.1f%%",
    #     shadow=True,
    #     startangle=140,
    # )
    # plt.axis("equal")
    # plt.show()
    
    # Gebruik numpy om de grafiek te maken
    import numpy as np
    import matplotlib.pyplot as plt
    
    _, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=140)
    ax.axis("equal")
    # plt.show()


def main():
    """
    Hoofdfunctionaliteit
    """
    content = fetch_file()
    meeting_ids = extract_meeting_ids(content)
    reports = fetch_reports(meeting_ids)
    if not reports:
        print("[main()] Geen 'vergaderverslag' gevonden.")
        return
    for report in reports:
        try:
            print("[main()] ================================") # TODO: Print datum of id of iets dergelijks
            kamerleden = parse_xml(report)
            attendance = check_attendance(kamerleden)
            create_chart(attendance)
        except Exception as e:
            print(f"[main()] Er is een fout opgetreden: {e}")
            continue
    # TODO: Maak een grafiek van de aanwezige Kamerleden over de verschillende
    #       'vergaderverslagen'


if __name__ == "__main__":
    main()
