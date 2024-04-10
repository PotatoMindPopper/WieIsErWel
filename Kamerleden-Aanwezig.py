import requests
import xml.etree.ElementTree as ET
import json
from datetime import date


def fetch_file():
    """
    Haalt het meest recente 'vergaderverslag' op van de Tweede Kamer API

    Omdat het meest recente 'vergaderverslag' vaak pas de volgende dag wordt
    gepubliceerd, wordt de datum van gisteren gebruikt om het meest recente
    'vergaderverslag' op te halen.

    :return: De inhoud van het meest recente 'vergaderverslag'
    """
    today = date.today()
    year, month, day = today.year, today.month, today.day - 1

    # Voorbeeld van een response zonder 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[]}
    # Voorbeeld van een response met 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[{"Id":"8176b1f5-b5a8-46f1-9d2c-5e66fd14604f","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":92511,"GewijzigdOp":"2024-04-09T20:08:55.5222825+02:00","ApiGewijzigdOp":"2024-04-10T10:06:34.0095628Z","Verwijderd":false,"Vergadering_Id":"7b123e97-8255-4ac9-adb8-da471891ebca"}]}
    # Voorbeeld van een response met meer dan 1 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[{"Id":"3849ce47-0ccb-417d-b883-7c13f31900e5","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":8614,"GewijzigdOp":"2024-04-05T11:27:48.3707026+02:00","ApiGewijzigdOp":"2024-04-05T09:30:02.6745625Z","Verwijderd":false,"Vergadering_Id":"099c5fab-95f1-407b-bf3c-87e9341e6172"},{"Id":"db2dd399-803b-4147-a92c-ebccdf21d23d","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":8614,"GewijzigdOp":"2024-04-05T08:37:03.0559843+02:00","ApiGewijzigdOp":"2024-04-05T06:37:33.2206437Z","Verwijderd":false,"Vergadering_Id":"099c5fab-95f1-407b-bf3c-87e9341e6172"}]}
    # TODO: Blijf fetchen totdat er een value is (print welke datum er wordt geprobeerd te fetchen)

    while True:
        url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{year}%20and%20month(GewijzigdOp)%20eq%20{month}%20and%20day(GewijzigdOp)%20eq%20{day}"
        print("[fetch_file()] URL:", url)  # Debugging
        response = requests.get(url)
        data = response.json()

        if data["value"]:
            # Als value niet leeg is, return de content
            if len(data["value"]) > 0:
                return response.content
            else:
                print(
                    f"Geen 'vergaderverslag' gevonden voor {day}-{month}-{year}. Probeer de dag ervoor."
                )
                day -= 1
        else:
            # Als value niet bestaat, kijken of er een error is
            if "error" in data:
                raise Exception(data["error"]["message"])
            else:
                raise Exception(
                    "Geen 'value' gevonden in de response van de API"
                )  # Onbekende error

        # Als de dag 0 is, ga naar de vorige maand
        if day == 0:
            day = 31
            month -= 1
        # Als de maand 0 is, ga naar het vorige jaar
        if month == 0:
            month = 12
            year -= 1

    return None


def extract_meeting_id(content):
    """
    Haalt 'Vergaderverslag' ID uit JSON

    :param content: De inhoud van het meest recente 'vergaderverslag'
    :return: Het ID van het meest recente 'vergaderverslag'
    """
    data = json.loads(content)
    return data["value"][0]["Id"]  # 0 is het meest recente 'vergaderverslag'


def fetch_report(meeting_id):
    """
    Haalt de inhoud van 'Vergaderverslag' op

    :param meeting_id: Het ID van het meest recente 'vergaderverslag'
    :return: De inhoud van het 'Vergaderverslag'
    """
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{meeting_id}/resource"
    print("[fetch_report()] URL:", url)  # Debugging
    response = requests.get(url)
    return response.content


def parse_xml(report):
    """
    Parseert de XML ontvangen van de API

    :param report: De inhoud van het 'Vergaderverslag'
    :return: Een lijst van Kamerleden die aanwezig waren
    """
    try:
        root = ET.fromstring(report.decode())
    except ET.ParseError:
        raise Exception("Fout bij het parsen van XML")

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

    # TODO: Vernieuw dit om de juiste alinea te vinden
    namespace = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
    paragraphs = root.findall(".//ns:alineaitem", namespaces=namespace)
    for paragraph in paragraphs:
        if "leden der Kamer, te weten:" in str(paragraph.text):
            # TODO: Volgende alinea is de lijst van kamerleden
            # TODO: Laatste index is ongeldig, verwijder deze
            return (
                paragraph.text.lower().replace(" en ", ",").replace(" ", "").split(",")
            )
    return []


def check_attendance(attendance_list):
    """
    Controleert aanwezigheid

    :param attendance_list: Een lijst van Kamerleden die aanwezig waren
    :return: Een lijst van Kamerleden die aanwezig waren
    """
    matching = []
    total_matched = 0
    with open("files/2dekmrledn.txt", "r", encoding="utf-8") as file:
        print("----Afwezig:----")
        for line in file:
            if line.strip() in attendance_list:
                matching.append(line.strip())
                total_matched += 1
            else:
                print(line.strip())

    if total_matched != len(attendance_list):
        raise Exception(
            f"Aantal Kamerleden komt niet overeen met het aantal aanwezigen: {total_matched}, maar zou moeten zijn {len(attendance_list)}"
        )

    print("Aantal Kamerleden aanwezig:", total_matched, "/", len(attendance_list))
    return attendance_list


def create_chart(attendance_list):
    """
    Maakt een grafiek die aangeeft wie aanwezig is en wie niet

    :param attendance_list: Een lijst van Kamerleden die aanwezig waren
    """
    import matplotlib.pyplot as plt

    labels = ["Afwezig", "Aanwezig"]
    sizes = [150 - len(attendance_list), len(attendance_list)]
    colors = ["red", "green"]
    explode = (0.1, 0)  # explode 1st slice

    plt.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        shadow=True,
        startangle=140,
    )
    plt.axis("equal")
    # plt.show()


def main():
    """
    Hoofdfunctionaliteit
    """
    content = fetch_file()
    meeting_id = extract_meeting_id(content)
    report = fetch_report(meeting_id)
    kamerleden = parse_xml(report)
    attendance = check_attendance(kamerleden)
    create_chart(attendance)


if __name__ == "__main__":
    main()
