import argparse
from datetime import date, datetime, timedelta
import os
import requests
import xml.etree.ElementTree as ET
import numpy
import pandas

debug = False
API_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"


class PresentieError(Exception):
    """
    Create a default exception
    """

    def __init__(self, *args):
        super().__init__(*args)


def get_url_content(datum):
    """
    Get most recent 'vergaderverslag' from tweedekamer API
    """
    # Write to log file
    directory = "files/logs/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(f"{directory}log{str(datum)}.txt", "w"):
        # Write content to the file if needed
        pass  # Placeholder, you can write content here if required

    url = (
        API_URL
        + "/Verslag"
        + "?$filter="
        + f"year(GewijzigdOp)%20eq%20{datum.year}"
        + "%20and%20"
        + f"month(GewijzigdOp)%20eq%20{datum.month}"
        + "%20and%20"
        + f"day(GewijzigdOp)%20eq%20{datum.day}"
    )

    if debug:
        print(url)

    response = requests.get(url)

    return response.json()


def get_vergader_ids(content):
    """
    Get vergaderID from json
    """
    vergaderingen = []
    for line in content["value"]:
        if line["Verwijderd"] == False:
            if debug:
                print(line)
            vergaderingen.append(line["Id"])
    return vergaderingen


def get_verslagen(vergader_ids):
    """
    Get 'Vergaderverslagen'
    """
    response = []
    for i in range(len(vergader_ids)):
        url = f"{API_URL}/Verslag/{vergader_ids[i]}/resource"
        if debug:
            print(url)
        response.append(requests.get(url))
    return response


def latest_verslag(verslagen):
    # Set a default time, for when a verslag is not valid
    default_time = "0001-01-01T00:00:00.0000000+00:00"

    # Find the timestamps of all verslagen
    tijden = []
    for verslag in verslagen:
        try:
            root = ET.fromstring(verslag.content.decode())
        except Exception as e:
            raise PresentieError(f"Error parsing XML: {e}")

        if (
            root[0][1].text != "Plenaire zaal"
            or root.attrib["soort"] == "Voorpublicatie"
        ):
            tijden.append(datetime.fromisoformat(default_time))
            continue

        timestamp = root.get("Timestamp", default_time)
        timestamp = datetime.fromisoformat(timestamp)
        if debug:
            print(timestamp)
        tijden.append(timestamp)

    # Check which verslag has the latest timestamp
    max_time = datetime.fromisoformat(default_time)
    max_element = -1
    for i, tijd in enumerate(tijden):
        if tijd > max_time:
            max_time = tijd
            max_element = i

    if max_element == -1:
        return -1

    verslag = verslagen[max_element]

    if debug:
        print(verslag, max_time)

    return verslag.content.decode()


def parse_xml(verslagen):
    """
    Parse the XML received from the API
    """
    verslag = latest_verslag(verslagen)

    if not verslag or verslag == -1:
        return -1

    try:
        root = ET.fromstring(verslag)
    except Exception as e:
        raise PresentieError(f"Error parsing XML: {e}")

    # Parse XML and extract specific element
    ns = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
    alinea_elements = root.findall(".//ns:alineaitem", namespaces=ns)

    if debug:
        print(type(alinea_elements))

    next_alinea = False
    kamerleden = None
    for alinea in alinea_elements:
        if next_alinea:
            kamerleden = alinea.text
            if debug:
                print("Kamerleden: ", kamerleden)
            break
        if "leden der Kamer, te weten:" in str(alinea.text):
            # TODO: Check if kamerleden are present in this text, instead of next one
            next_alinea = True

    if type(kamerleden) == type(None):
        return -1

    # Format and transform into array
    kamerleden = (
        kamerleden.lower().rstrip(",").replace(" en ", ",").replace(" ", "").split(",")
    )

    if debug:
        print(type(kamerleden), kamerleden)

    return kamerleden


def stringSimilarity(target, source, matched):
    """
    Match names from present list (source) to total list (target)
    """
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
                        print(f"matched {target} to {source[i]}")
                    return True
                else:
                    break
            # Compare letters
            if target[j] == source[i][j]:
                consistent += 1
    # No match found
    return False


def presentie(aanwezig):
    """
    Checking presence
    """
    matched = []
    afwezig = []
    integer = 0
    # Open file with all members
    f = open("files/2dekmrledn.txt", "r")
    print("----Afwezig:----")

    # Check who are present at vergaderingen and mark in 'matched' array
    for line in f:
        if stringSimilarity(line.rstrip("\n"), aanwezig, matched):
            integer += 1
        else:
            print(line.rstrip("\n"))
            afwezig.append(line.rstrip("\n"))
            pass

    print(f"{integer} / {len(aanwezig)} kamerleden aanwezig, {len(afwezig)} afwezigen")

    # Check if everyone has been matched
    if integer != len(aanwezig):
        print(
            f"Aantal Kamerleden matcht niet met het aanwezige aantal is {integer} maar moet zijn {len(aanwezig)}"
        )

    print(afwezig)

    return aanwezig, afwezig


def arrayParsing(aanwezig, afwezig):
    """
    Parse array to DataFrame
    """
    afwezig = numpy.array(afwezig, dtype=object)
    count = numpy.arange(1, 2 * len(afwezig), 0.5, dtype=int)
    afwezig = afwezig.reshape(-1)
    df = pandas.DataFrame(data=afwezig, columns=["afwezig"])
    df["counts"] = pandas.DataFrame(data=count)
    print(df.groupby("afwezig").count().sort_values(by=["counts"], ascending=False))


def make_graph(aanwezig, afwezig):
    """
    Make nice graph who is present and who is not
    """
    data = arrayParsing(aanwezig, afwezig)


def aanwezigheid(datum):
    # Check of er wel een echte datum doorgegeven is
    if not isinstance(datum, date):
        raise PresentieError(f"{datum}({type(datum)}) is geen {type(date)}")

    # Haal het verslag op
    content = get_url_content(datum)

    # Haal de vergaderID uit het verslag
    vergader_ids = get_vergader_ids(content)

    # Als de ID nul is, is er geen vergaderverslag
    if len(vergader_ids) == 0:
        return None, None

    if debug:
        print(vergader_ids[0])

    # Haal het verslag op a.h.v. de vergaderID
    verslagen = get_verslagen(vergader_ids)

    # Haal de lijst met kamerleden uit de verslagen
    kamerleden = parse_xml(verslagen)

    # Check of er wel echt iets uitgekomen is
    if kamerleden == -1:
        return None, None

    # Geef de aanwezigen terug aan de bovenliggende functie
    aanwezig, afwezig = presentie(kamerleden)
    with open(f"files/logs/log{datum}.txt", "a") as f:
        f.write("Aanwezig:\n")
        for string in aanwezig:
            f.write(string + "\n")
        f.write("\nAfwezig:\n")
        for string in afwezig:
            f.write(string + "\n")

    return aanwezig, afwezig


def convert_to_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()


def process_date(datum):
    if datum.isoweekday() == 6 or datum.isoweekday() == 7:
        return [], []  # Return empty lists for weekends

    if datum == date.today():
        print(
            "Verslag van vandaag is er waarschijnlijk niet, dus deze wordt niet gezocht"
        )
        return [], []  # Return empty lists for today

    result = aanwezigheid(datum)
    if result is None:
        return [], []  # Handle the case when aanwezigheid returns None

    aanwezig, afwezig = result

    if aanwezig and afwezig:
        return aanwezig, afwezig
    else:
        return [], []  # Handle the case when aanwezigheid returns tuple[None, None]


def process_range_of_dates(delta, datum):
    aanwezig_arr = afwezig_arr = []

    for _ in range(delta.days):
        datum += timedelta(days=1)
        aanwezig, afwezig = process_date(datum)
        if aanwezig and afwezig:
            aanwezig_arr.extend(aanwezig)
            afwezig_arr.extend(afwezig)

    return aanwezig_arr, afwezig_arr


def multiprocess_range_of_dates(delta, datum):
    from multiprocessing import Pool

    dates_to_process = [datum + timedelta(days=i) for i in range(delta.days)]

    # Use multiprocessing pool to process dates in parallel with custom number
    # of processes
    with Pool(max(1, os.cpu_count() - 2)) as pool:
        results = pool.map(process_date, dates_to_process)

    # Unpack the results
    aanwezig_arr = afwezig_arr = []
    for aanwezig, afwezig in results:
        if aanwezig and afwezig:
            aanwezig_arr.extend(aanwezig)
            afwezig_arr.extend(afwezig)

    return aanwezig_arr, afwezig_arr


def range_of_dates():
    datum1 = convert_to_date(input("Geef een eerste datum op (YYYY-MM-DD): "))
    datum2 = convert_to_date(input("Geef een tweede datum op (YYYY-MM-DD): "))
    delta = datum2 - datum1

    aanwezig_arr = afwezig_arr = []
    if delta.days <= 10:
        aanwezig_arr, afwezig_arr = process_range_of_dates(delta, datum1)
    else:
        aanwezig_arr, afwezig_arr = multiprocess_range_of_dates(delta, datum1)
    return aanwezig_arr, afwezig_arr


def main():
    aanwezig_arr = []
    afwezig_arr = []

    while True:
        answer = input("1: Zelf datum opgeven\n2: Bereik van data\nUw keuze: ")
        if answer == "1":
            datum = convert_to_date(input("Geef een datum op (YYYY-MM-DD): "))
            aanwezig_arr, afwezig_arr = aanwezigheid(datum)
            break
        elif answer == "2":
            aanwezig_arr, afwezig_arr = range_of_dates()
            break
        else:
            print('Verkeerde invoer (alleen "1" of "2")')

    while True:
        answer = input("Grafiekje maken? j/n: \n").lower()
        if answer == "j":
            make_graph(aanwezig_arr, afwezig_arr)
            break
        elif answer == "n":
            break
        else:
            print("Invoer is j/n")


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
