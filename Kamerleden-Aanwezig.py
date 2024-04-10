import sys
import requests as req
import xml.etree.ElementTree as ET
import json
from datetime import date


# Fetches the most recent 'vergaderverslag' from tweedekamer API
def get_file():
    today = date.today()
    # 'vergaderverslag' of today will only be published very late today or early tomorrow
    year, month, day = today.year, today.month, today.day - 1
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{year}%20and%20month(GewijzigdOp)%20eq%20{month}%20and%20day(GewijzigdOp)%20eq%20{day}"
    response = req.get(url)
    return response.content


# Extracts 'Vergaderverslag' ID from JSON
def extract_vergader_id(content):
    data = json.loads(content)
    return data["value"][0]["Id"]


# Fetches 'Vergaderverslag' content
def get_verslag(vergader_id):
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{vergader_id}/resource"
    response = req.get(url)
    return response.content


# Parses the XML received from the API
def parse_xml(verslag):
    next_flag = False
    kamerleden = ""

    try:
        root = ET.fromstring(verslag.decode())
    except ET.ParseError:
        raise Exception("Error parsing XML")

    # Parse XML and extract specific element
    ns = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
    alinea_elements = root.findall(".//ns:alineaitem", namespaces=ns)
    for alinea in alinea_elements:
        if next_flag:
            kamerleden = alinea.text
            break
        if "leden der Kamer, te weten:" in str(alinea.text):
            next_flag = True

    # Format and transform into array
    kamerleden = kamerleden.lower().replace(" en ", ",").replace(" ", "").split(",")
    # Last index is invalid, removing it
    return kamerleden[:-1]


# Matches names from present list to total list
def string_similarity(target, source, matched):
    for i, src in enumerate(source):
        if src in matched:
            continue
        for j, tgt in enumerate(target):
            if j >= len(src) or j >= len(tgt):
                if len(matched) == len(source) - 1:
                    matched.append(src)
                    return True
                else:
                    break
            if tgt[j] == src[j] and j == len(src) - 1:
                matched.append(src)
                return True
    return False


# Checks presence
def check_presence(present_list):
    matched = []
    integer = 0
    # Open file with all members
    with open("files/2dekmrledn.txt", "r") as f:
        print("----Afwezig:----")
        # Check who are present at vergaderingen and mark in 'matched' array
        for line in f:
            if string_similarity(line.rstrip("\n"), present_list, matched):
                integer += 1
            else:
                print(line.rstrip("\n"))
    # Not everyone has been matched
    if integer != len(present_list):
        raise Exception(
            f"Aantal Kamerleden matcht niet met het aanwezige aantal: {integer}, maar moet zijn {len(present_list)}"
        )

    print(integer, "/", len(present_list))
    return present_list


# Makes a graph indicating who is present and who is not
def make_graph(present_list):
    pass


def main():
    content = get_file()
    vergader_id = extract_vergader_id(content)
    verslag = get_verslag(vergader_id)
    kamerleden = parse_xml(verslag)
    aanwezig = check_presence(kamerleden)
    make_graph(aanwezig)


if __name__ == "__main__":
    main()
