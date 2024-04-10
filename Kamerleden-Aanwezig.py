import sys
import requests as req
import xml.etree.ElementTree as ET
import json
from datetime import date


# Haalt het meest recente 'vergaderverslag' op van de Tweede Kamer API
def haal_bestand_op():
    vandaag = date.today()
    # Het 'vergaderverslag' van vandaag wordt pas erg laat vandaag of vroeg morgen gepubliceerd
    jaar, maand, dag = vandaag.year, vandaag.month, vandaag.day - 1
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{jaar}%20and%20month(GewijzigdOp)%20eq%20{maand}%20and%20day(GewijzigdOp)%20eq%20{dag}"
    reactie = req.get(url)
    return reactie.content


# Haalt 'Vergaderverslag' ID uit JSON
def haal_vergader_id_op(inhoud):
    gegevens = json.loads(inhoud)
    return gegevens["value"][0]["Id"]


# Haalt de inhoud van 'Vergaderverslag' op
def haal_verslag_op(vergader_id):
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{vergader_id}/resource"
    reactie = req.get(url)
    return reactie.content


# Parseert de XML ontvangen van de API
def parseer_xml(verslag):
    volgende_vlag = False
    kamerleden = ""

    try:
        wortel = ET.fromstring(verslag.decode())
    except ET.ParseError:
        raise Exception("Fout bij het parsen van XML")

    # Parseer XML en haal specifiek element eruit
    ns = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
    alinea_elementen = wortel.findall(".//ns:alineaitem", namespaces=ns)
    for alinea in alinea_elementen:
        if volgende_vlag:
            kamerleden = alinea.text
            break
        if "leden der Kamer, te weten:" in str(alinea.text):
            volgende_vlag = True

    # Formatteer en transformeer naar array
    kamerleden = kamerleden.lower().replace(" en ", ",").replace(" ", "").split(",")
    # Laatste index is ongeldig, verwijder deze
    return kamerleden[:-1]


# Koppelt namen van de aanwezige lijst aan de totale lijst
def string_gelijkheid(doel, bron, overeenkomend):
    for i, src in enumerate(bron):
        if src in overeenkomend:
            continue
        for j, tgt in enumerate(doel):
            if j >= len(src) or j >= len(tgt):
                if len(overeenkomend) == len(bron) - 1:
                    overeenkomend.append(src)
                    return True
                else:
                    break
            if tgt[j] == src[j] and j == len(src) - 1:
                overeenkomend.append(src)
                return True
    return False


# Controleert aanwezigheid
def controleer_aanwezigheid(aanwezigheidslijst):
    overeenkomend = []
    integer = 0
    # Open het bestand met alle leden
    with open("files/2dekmrledn.txt", "r") as f:
        print("----Afwezig:----")
        # Controleer wie aanwezig is bij vergaderingen en markeer in 'overeenkomend' array
        for regel in f:
            if string_gelijkheid(regel.rstrip("\n"), aanwezigheidslijst, overeenkomend):
                integer += 1
            else:
                print(regel.rstrip("\n"))
    # Niet iedereen is gematcht
    if integer != len(aanwezigheidslijst):
        raise Exception(
            f"Aantal Kamerleden komt niet overeen met het aantal aanwezigen: {integer}, maar zou moeten zijn {len(aanwezigheidslijst)}"
        )

    print(integer, "/", len(aanwezigheidslijst))
    return aanwezigheidslijst


# Maakt een grafiek die aangeeft wie aanwezig is en wie niet
def maak_grafiek(aanwezigheidslijst):
    pass


def hoofd():
    inhoud = haal_bestand_op()
    vergader_id = haal_vergader_id_op(inhoud)
    verslag = haal_verslag_op(vergader_id)
    kamerleden = parseer_xml(verslag)
    aanwezig = controleer_aanwezigheid(kamerleden)
    maak_grafiek(aanwezig)


if __name__ == "__main__":
    hoofd()
