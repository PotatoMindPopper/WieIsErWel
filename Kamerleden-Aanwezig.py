import requests as req
import xml.etree.ElementTree as ET
import json
from datetime import date


def fetch_file():
    """
    Haalt het meest recente 'vergaderverslag' op van de Tweede Kamer API

    Omdat het meest recente 'vergaderverslag' vaak pas de volgende dag wordt
    gepubliceerd, wordt de datum van gisteren gebruikt om het meest recente
    'vergaderverslag' op te halen.
    """
    today = date.today()
    year, month, day = today.year, today.month, today.day - 1
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{year}%20and%20month(GewijzigdOp)%20eq%20{month}%20and%20day(GewijzigdOp)%20eq%20{day}"
    response = req.get(url)
    return response.content


def extract_meeting_id(content):
    """
    Haalt 'Vergaderverslag' ID uit JSON
    """
    data = json.loads(content)
    return data["value"][0]["Id"]


def fetch_report(meeting_id):
    """
    Haalt de inhoud van 'Vergaderverslag' op
    """
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{meeting_id}/resource"
    response = req.get(url)
    return response.content


def parse_xml(report):
    """
    Parseert de XML ontvangen van de API
    """
    try:
        root = ET.fromstring(report.decode())
    except ET.ParseError:
        raise Exception("Fout bij het parsen van XML")

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

    print(total_matched, "/", len(attendance_list))
    return attendance_list


def create_chart(attendance_list):
    """
    Maakt een grafiek die aangeeft wie aanwezig is en wie niet
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
    plt.show()


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
