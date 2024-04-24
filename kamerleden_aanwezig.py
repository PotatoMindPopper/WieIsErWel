import argparse
import logging
from datetime import date, datetime, timedelta
import os
import requests
import xml.etree.ElementTree as ET
import numpy
import pandas

API_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"


class PresentieError(Exception):
    """
    Custom exception class for errors related to presence checking.
    """

    def __init__(self, *args):
        """
        Initialize the PresentieError exception.
        """
        super().__init__(*args)


def get_url_content(date):
    """
    Fetches the 'vergaderverslag'-en data from the Tweede Kamer API for a given
    date.
    """
    # Create directory for log files if it doesn't exist
    log_directory = "files/logs/"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Write to a log file
    log_file_path = f"{log_directory}log{str(date)}.txt"
    with open(log_file_path, "w"):
        # No content to write at the moment
        pass

    # Construct API URL for fetching content based on the provided date
    url = (
        API_URL
        + "/Verslag"
        + "?$filter="
        + f"year(GewijzigdOp)%20eq%20{date.year}"
        + "%20and%20"
        + f"month(GewijzigdOp)%20eq%20{date.month}"
        + "%20and%20"
        + f"day(GewijzigdOp)%20eq%20{date.day}"
    )

    # Log the constructed URL for debugging purposes
    logging.debug(f"[get_url_content()] url: {url}")

    # Send request to the API and return the JSON response
    response = requests.get(url)
    return response.json()


def get_vergader_ids(content):
    """
    Extracts vergaderID from JSON content obtained from the Tweede Kamer API.
    """
    # Initialize an empty list to store the extracted vergaderID values
    vergader_ids = []

    # Iterate through each line (vergadering) in the JSON content
    for line in content["value"]:
        # Check if the 'Verwijderd' field is False
        if not line["Verwijderd"]:
            # Log the line for debugging purposes
            logging.debug(f"[get_vergader_ids()] Line: {line}")
            # Append the 'Id' field to the list of vergaderID values
            vergader_ids.append(line["Id"])

    # Return the list of vergaderID values
    return vergader_ids


def get_verslagen(vergader_ids):
    """
    Fetches 'Vergaderverslagen' from the Tweede Kamer API for the given list of
    vergaderIDs.
    """
    # Initialize an empty list to store the HTTP response objects
    verslagen = []

    # Iterate through each vergaderID in the provided list
    for vergader_id in vergader_ids:
        # Construct the URL for fetching the 'Vergaderverslagen' based on the
        # vergaderID
        url = f"{API_URL}/Verslag/{vergader_id}/resource"
        # Log the URL for debugging purposes
        logging.debug(f"[get_verslagen()] URL: {url}")
        # Send a GET request to the API and append the response object to the
        # list
        verslagen.append(requests.get(url))

    # Return the list of HTTP response objects containing the fetched
    # 'Vergaderverslagen' data
    return verslagen


def latest_verslag(verslagen):
    """
    Determines the latest 'verslag' (meeting report) among a list of provided
    'verslagen'.
    """
    # Set a default time for when a 'verslag' is not valid
    default_time = "0001-01-01T00:00:00.0000000+00:00"

    # Initialize a list to store the timestamps of all 'verslagen'
    timestamps = []

    # Iterate through each 'verslag'
    for verslag in verslagen:
        try:
            # Parse XML content of the 'verslag'
            root = ET.fromstring(verslag.content.decode())
        except Exception as e:
            # Raise an error if there's an issue parsing XML
            raise PresentieError(f"Error parsing XML: {e}")

        # Check if the 'verslag' is valid and not a 'Voorpublicatie'
        if (
            root[0][1].text != "Plenaire zaal"
            or root.attrib["soort"] == "Voorpublicatie"
        ):
            # If not valid, append the default time to the list
            timestamps.append(datetime.fromisoformat(default_time))
            continue

        # Extract the timestamp from the 'verslag'
        timestamp = root.get("Timestamp", default_time)
        timestamp = datetime.fromisoformat(timestamp)
        # Log the timestamp for debugging purposes
        logging.debug(f"[latest_verslag()] Timestamp: {timestamp}")
        timestamps.append(timestamp)

    # Find the 'verslag' with the latest timestamp
    max_time = datetime.fromisoformat(default_time)
    max_element = -1
    for i, tijd in enumerate(timestamps):
        if tijd > max_time:
            max_time = tijd
            max_element = i

    # If no valid 'verslag' is found, return -1
    if max_element == -1:
        return -1

    # Extract the content of the latest 'verslag'
    latest_verslag = verslagen[max_element].content.decode()

    # Log the details of the latest 'verslag' for debugging purposes
    logging.debug(
        f"[latest_verslag()] Max element: {max_element}; Max time: {max_time}"
    )

    # Return the content of the latest 'verslag'
    return latest_verslag


def parse_xml(verslagen):
    """
    Parses XML content received from the Tweede Kamer API to extract information
    about the attending members.
    """
    # Get the latest 'verslag' content
    verslag = latest_verslag(verslagen)

    # If no valid 'verslag' is found, return -1
    if not verslag or verslag == -1:
        return -1

    try:
        # Parse the XML content
        root = ET.fromstring(verslag)
    except Exception as e:
        # Raise an error if there's an issue parsing XML
        raise PresentieError(f"Error parsing XML: {e}")

    # Extract alinea elements from the XML
    ns = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
    alinea_elements = root.findall(".//ns:alineaitem", namespaces=ns)

    # Initialize variables
    next_alinea = False
    kamerleden = None

    # Iterate through alinea elements to find attending members
    for alinea in alinea_elements:
        if next_alinea:
            # Extract attending members from the next alinea
            kamerleden = alinea.text
            logging.debug(f"[parse_xml()] Attending members: {kamerleden}")
            break
        if "leden der Kamer, te weten:" in str(alinea.text):
            # TODO: Check if kamerleden are present in this text, instead of next one
            # Set the flag to check the next alinea for attending members
            next_alinea = True

    # If attending members are not found, return -1
    if kamerleden is None:
        return -1

    # Format attending members into a list
    kamerleden = (
        kamerleden.lower().rstrip(",").replace(" en ", ",").replace(" ", "").split(",")
    )

    logging.debug(
        f"[parse_xml()] Type of attending members: {type(kamerleden)}; "
        + f"Attending members: {kamerleden}"
    )

    return kamerleden


def string_similarity(target, source, matched):
    """
    Matches names from a source list to a target list based on string
    similarity.
    """
    # Initialize a variable to track the number of consistent characters
    consistent = 0

    # Iterate through each name in the source list
    for i in range(len(source)):
        # Skip names that are already matched
        if source[i] in matched:
            continue

        # Reset the consistent count for each new name
        consistent = 0

        # Iterate through each name in the target list
        for j in range(len(target)):
            # If either the length of the source name or target name is reached
            # or enough letters are matched
            if (
                j >= len(source[i])
                or j >= len(target)
                or consistent >= len(source[i]) - 1
            ):
                # If enough letters are matched, accept the match
                if consistent >= len(source[i]) - 1:
                    matched.append(source[i])
                    logging.debug(
                        f"[string_similarity()] Matched {target} to {source[i]}"
                    )
                    return True
                else:
                    break

            # Compare letters of the target and source names
            if target[j] == source[i][j]:
                consistent += 1

    # No match found
    return False


def presentie(aanwezig):
    """
    Checks the presence of members based on a list of present members.
    """
    # Initialize lists to store matched and absent members, and a counter for
    # matched members
    matched = []
    afwezig = []
    integer = 0

    print("----Afwezig:----")
    # Open file with all members
    with open("files/2dekmrledn.txt", "r") as f:
        # Check who are present at vergaderingen and mark in 'matched' array
        for line in f:
            if string_similarity(line.rstrip("\n"), aanwezig, matched):
                integer += 1
            else:
                print(line.rstrip("\n"))
                afwezig.append(line.rstrip("\n"))

    # Print the count of present and absent members
    print(
        f"{integer} / {len(aanwezig)} kamerleden "
        + f"aanwezig, {len(afwezig)} afwezigen"
    )

    # Check if everyone has been matched
    if integer != len(aanwezig):
        print(
            "Aantal Kamerleden matcht niet met het aanwezige aantal "
            + f"is {integer} maar moet zijn {len(aanwezig)}"
        )

    # Log the list of absent members for debugging purposes
    logging.debug(f"[presentie()] Afwezig: {afwezig}")

    # Return lists of present and absent members
    return aanwezig, afwezig


def array_parsing(aanwezig, afwezig):
    """
    Parses arrays of present and absent members into a DataFrame and performs
    data aggregation.
    """
    # Convert the list of absent members to a numpy array
    afwezig = numpy.array(afwezig, dtype=object)

    # Generate an array of counts for each absent member
    count = numpy.arange(1, 2 * len(afwezig), 0.5, dtype=int)

    # Reshape the array of absent members to a 1D array
    afwezig = afwezig.reshape(-1)

    # Create a DataFrame with the absent members and their respective counts
    df = pandas.DataFrame(data=afwezig, columns=["afwezig"])
    df["counts"] = pandas.DataFrame(data=count)

    # Group by the 'afwezig' column and count occurrences, then sort by counts
    # in descending order
    result_df = (
        df.groupby("afwezig").count().sort_values(by=["counts"], ascending=False)
    )

    # Print the DataFrame
    print(result_df)

    # Return the aggregated DataFrame
    return result_df


def make_graph(aanwezig, afwezig):
    """
    Creates a graphical representation of present and absent members.
    """
    # Parse the data into a format suitable for graph creation
    data = array_parsing(aanwezig, afwezig)

    # Code for creating the graph goes here
    # ...


def aanwezigheid(datum):
    """
    Checks the presence of members at a meeting on the specified date.
    """
    # Check if a valid date object is passed
    if not isinstance(datum, date):
        raise PresentieError(f"{datum}({type(datum)}) is not a valid date")

    # TODO: Add a waiting text, until presentie(kamerleden) gets called

    # Fetch the content of the meeting report for the specified date
    content = get_url_content(datum)

    # Extract the meeting IDs from the meeting report
    vergader_ids = get_vergader_ids(content)

    # If no meeting ID is found, return None for both present and absent members
    if len(vergader_ids) == 0:
        return None, None

    logging.debug(f"{vergader_ids[0]}")

    # Fetch the meeting reports based on the meeting IDs
    verslagen = get_verslagen(vergader_ids)

    # Parse the meeting reports to extract the list of members
    kamerleden = parse_xml(verslagen)

    # If no members are found, return None for both present and absent members
    if kamerleden == -1:
        return None, None

    # Check the presence of members and get present and absent lists
    aanwezig, afwezig = presentie(kamerleden)

    # Write present and absent members to a log file
    with open(f"files/logs/log{datum}.txt", "a") as f:
        f.write("Aanwezig:\n")
        for string in aanwezig:
            f.write(string + "\n")
        f.write("\nAfwezig:\n")
        for string in afwezig:
            f.write(string + "\n")

    # Return the lists of present and absent members
    return aanwezig, afwezig


def convert_to_date(date_string):
    """
    Converts a date string in the format 'YYYY-MM-DD' to a date object.
    """
    return datetime.strptime(date_string, "%Y-%m-%d").date()


def process_date(datum):
    """
    Processes the presence status for a given date.
    """
    # Return empty lists for weekends
    if datum.isoweekday() in (6, 7):
        return [], []

    # Return empty lists for today
    if datum == date.today():
        print(
            "Verslag van vandaag is er waarschijnlijk niet, "
            + "dus deze wordt niet gezocht"
        )
        return [], []

    # Get the presence status for the given date
    result = aanwezigheid(datum)

    # Handle the case when aanwezigheid returns None
    if result is None:
        return [], []

    # Unpack the result tuple
    aanwezig, afwezig = result

    # If both present and absent lists are not empty, return them
    if aanwezig and afwezig:
        return aanwezig, afwezig
    else:
        # Handle the case when aanwezigheid returns tuple[None, None]
        return [], []


def process_range_of_dates(delta, datum):
    """
    Processes the presence status for a range of dates starting from a given
    date.
    """
    # Initialize lists to store present and absent members
    aanwezig_arr = []
    afwezig_arr = []

    # Iterate over the range of dates specified by 'delta'
    for _ in range(delta.days):
        # Increment the date by one day
        datum += timedelta(days=1)

        # Process the presence status for the current date
        aanwezig, afwezig = process_date(datum)

        # Extend the lists with the present and absent members for the current
        # date
        if aanwezig and afwezig:
            aanwezig_arr.extend(aanwezig)
            afwezig_arr.extend(afwezig)

    # Return the lists of present and absent members for the entire range of
    # dates
    return aanwezig_arr, afwezig_arr


def multiprocess_range_of_dates(delta, datum):
    """
    Processes the presence status for a range of dates starting from a given
    date using multiprocessing.
    """
    from multiprocessing import Pool

    # Generate a list of dates to process within the specified range
    dates_to_process = [datum + timedelta(days=i) for i in range(delta.days)]

    # Use multiprocessing pool to process dates in parallel with a custom number
    # of processes
    with Pool(max(1, os.cpu_count() - 2)) as pool:
        # Map the 'process_date' function to each date in the list and get the
        # results
        results = pool.map(process_date, dates_to_process)

    # Initialize lists to store present and absent members
    aanwezig_arr = []
    afwezig_arr = []

    # Unpack the results and extend the lists with present and absent members
    for aanwezig, afwezig in results:
        if aanwezig and afwezig:
            aanwezig_arr.extend(aanwezig)
            afwezig_arr.extend(afwezig)

    # Return the lists of present and absent members for the entire range of
    # dates
    return aanwezig_arr, afwezig_arr


def range_of_dates():
    """
    Processes the presence status for a range of dates inputted by the user.
    """
    # Prompt the user to input the first and second dates
    datum1 = convert_to_date(input("Geef een eerste datum op (YYYY-MM-DD): "))
    datum2 = convert_to_date(input("Geef een tweede datum op (YYYY-MM-DD): "))

    # Calculate the timedelta representing the range of dates
    delta = datum2 - datum1

    # Initialize lists to store present and absent members
    aanwezig_arr = []
    afwezig_arr = []

    # Choose the appropriate method based on the range of dates
    if delta.days <= 10:
        # Process the presence status for the range of dates using
        # single-process approach
        aanwezig_arr, afwezig_arr = process_range_of_dates(delta, datum1)
    else:
        # Process the presence status for the range of dates using
        # multiprocessing approach
        aanwezig_arr, afwezig_arr = multiprocess_range_of_dates(delta, datum1)

    # Return the lists of present and absent members for the entire range of
    # dates
    return aanwezig_arr, afwezig_arr


def main():
    """
    Entry point for the program to interactively process presence status and
    optionally create a graph.
    """
    # Initialize lists to store present and absent members
    aanwezig_arr = []
    afwezig_arr = []

    # Prompt the user to choose between two options: specify a single date or a
    # range of dates
    while True:
        answer = input("1: Zelf datum opgeven\n2: Bereik van data\nUw keuze: ")
        if answer == "1":
            # If the user chooses to specify a single date, prompt for the date
            # and process its presence status
            datum = convert_to_date(input("Geef een datum op (YYYY-MM-DD): "))
            aanwezig_arr, afwezig_arr = aanwezigheid(datum)
            break
        elif answer == "2":
            # If the user chooses to specify a range of dates, process the
            # presence status for the range of dates
            aanwezig_arr, afwezig_arr = range_of_dates()
            break
        else:
            print('Verkeerde invoer (alleen "1" of "2")')

    # Prompt the user to choose whether to create a graph based on the processed
    # presence status
    while True:
        answer = input("Grafiekje maken? j/n: \n").lower()
        if answer == "j":
            # If the user chooses to create a graph, call the 'make_graph'
            # function
            make_graph(aanwezig_arr, afwezig_arr)
            break
        elif answer == "n":
            # If the user chooses not to create a graph, exit the loop
            break
        else:
            print("Invoer is j/n")


if __name__ == "__main__":
    """
    Entry point of the script.

    Parses command-line arguments to set debug mode for printing, initializes
    logging, and calls the main function to interactively process presence
    status and optionally create a graph.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Set debug mode for printing")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Set debug to True if you want to see the output of "
        + "the getting and parsing process",
    )
    args = parser.parse_args()

    # Set logging level based on debug mode
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Call the main function to process presence status and create a graph
    main()
