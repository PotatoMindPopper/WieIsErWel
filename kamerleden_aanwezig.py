import argparse
from cgi import print_form
import sys
from types import NoneType
from numpy import dtype
import requests as req
import xml.etree.ElementTree as ET
import json
from datetime import date, datetime

import argparse

debug = False


# Get most recent 'vergaderverslag' from tweedekamer API
def get_file():
    today = date.today()
    # 'vergaderverslag' of today will only be published very late today or early tomorrow
    year = today.year
    month = today.month
    day = today.day - 1
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{year}%20and%20month(GewijzigdOp)%20eq%20{month}%20and%20day(GewijzigdOp)%20eq%20{day}"
    if debug:
        print(url)
    r = req.get(url)
    return r.content


# Get vergaderID from json
def vergader_id(content):
    val = json.loads(content)
    vergaderingen = []
    for line in val["value"]:
        if line["Verwijderd"] == False:
            if debug:
                print(line)
            vergaderingen.append(line["Id"])
    return vergaderingen


# Get 'Vergaderverslagen'
def get_verslag(vergader_id):
    r = []
    for i in range(len(vergader_id)):
        url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{vergader_id[i]}/resource"
        if debug:
            print(url)
        r.append(req.get(url))
    return r


def laatste(verslagen):
    tijden = []
    max = 0
    max_element = -1
    for i in range(len(verslagen)):
        verslag = verslagen[i].content.decode()

        try:
            root = ET.fromstring(verslag)
        except:
            raise Exception("Error parsing XML")

        if (
            root[0][1].text != "Plenaire zaal"
            or root.attrib["soort"] == "Voorpublicatie"
        ):
            tijden.append(0)
            continue

        tijden.append(root.attrib["Timestamp"].split("T")[1].split(":")[0])

    for j in range(len(tijden)):
        if int(tijden[j]) > max:
            max = int(tijden[j])
            max_element = j

    if debug:
        print(max_element, max)
    return max_element


# Parse the XML received from the API
def parse_xml(verslagen):
    next = False
    kamerleden = ""

    laatste_vers = laatste(verslagen)
    verslag = verslagen[laatste_vers].content.decode()

    try:
        root = ET.fromstring(verslag)
    except:
        raise Exception("Error parsing XML")

    # Parse XML and extract specific element
    ns = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
    alinea_elements = root.findall(".//ns:alineaitem", namespaces=ns)
    if debug:
        print(type(alinea_elements))

    for alinea in alinea_elements:
        if next:
            kamerleden = alinea.text
            if debug:
                print("Kamerleden: ", kamerleden)
            break
        if "leden der Kamer, te weten:" in str(alinea.text):
            next = True

        if not next or type(kamerleden) == None:
            continue

    # Format and transform into array
    kamerleden = kamerleden.lower().replace(" en ", ",").replace(" ", "").split(",")
    if debug:
        print(type(kamerleden), kamerleden)
    # Last index is invalid ez fix
    return kamerleden[: len(kamerleden) - 1]


# Match names from present list (source) to total list (target)
def string_similarity(target, source, matched):
    consistent = 0
    for i in range(len(source)):
        if source[i] in matched:
            continue
        consistent = 0
        for j in range(len(target)):
            # If the length of one of the strings has been reached or if enough letters are matched
            if (
                j >= len(source[i])
                or j >= len(target)
                or consistent >= len(source[i]) - 1
            ):
                # If enough letters are matched accept it
                if consistent >= len(source[i]) - 1:
                    matched.append(source[i])
                    if debug:
                        print(f"mathced {target} to {source[i]}")
                    return True
                else:
                    break
            # Compare letters
            if target[j] == source[i][j]:
                consistent += 1
    # No match found
    return False


# Checking presence
def presentie(aanwezig):
    matched = []
    integer = 0
    # Open file with all members
    f = open("files/2dekmrledn.txt", "r")
    print("----Afwezig:----")

    # Check who are present at vergaderingen and mark in 'matched' array
    for line in f:
        if string_similarity(line.rstrip("\n"), aanwezig, matched):
            integer += 1
        else:
            print(line.rstrip("\n"))
            pass

    print(integer, "/", len(aanwezig))
    # Check if everyone has been matched
    if integer != len(aanwezig):
        raise Exception(
            f"Aantal Kamerleden matcht niet met het aanwezige aantal is {integer} maar moet zijn {len(aanwezig)}"
        )

    return aanwezig


# Make nice graph who is present and who is not
def make_graph(aanwezig):
    pass


def main():
    content = get_file()
    vergader_id = vergader_id(content)
    if debug:
        print(vergader_id[0])
    verslagen = get_verslag(vergader_id)
    kamerleden = parse_xml(verslagen)
    aanwezig = presentie(kamerleden)
    make_graph(aanwezig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set debug mode for printing")
    parser.add_argument(
        "--debug",
        default=False,
        type=bool,
        metavar=debug,
        help="Set debug to True if you want to see the output of\
                            the getting and parsing process",
    )
    args = parser.parse_args()
    debug = args.debug
    main()
