# Description: Dit bestand bevat de functies om de XML van de API te parsen
#
# :param report: De inhoud van het 'Vergaderverslag'
# :return: Een lijst van Kamerleden die aanwezig waren
#

import xml.etree.ElementTree as ET


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
            if (
                functie.lower().startswith("lid tweede kamer")
                or speaker.get("Soort") == "Tweede Kamerlid"
            ):
                # Als de functie begint met "lid Tweede Kamer" of de Soort
                # "Tweede Kamerlid" is, voeg deze toe aan de lijst
                # TODO: Voeg weergavenaam, voornaam, achternaam, partij toe
                kamerleden[objectid] = (
                    weergavenaam.lower().strip(),
                    speaker.find(".//ns:voornaam", namespaces=namespace).text,
                    speaker.find(".//ns:achternaam", namespaces=namespace).text,
                    speaker.find(".//ns:fractie", namespaces=namespace).text,
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
                aantal_kamerleden = int(
                    paragraph.text.split("Aanwezig zijn ")[1]
                    .split("leden der Kamer, te weten:")[0]
                    .strip()
                )
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
            elif (
                paragraphs[paragraphs.index(paragraph) + 1].text
                and paragraphs[paragraphs.index(paragraph) + 1].text.strip() != ""
            ):
                return (
                    paragraphs[paragraphs.index(paragraph) + 1]
                    .text.strip()  # Verwijder spaties aan het begin en einde
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
