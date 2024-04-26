import argparse
import logging
from datetime import date, datetime, timedelta
import os
import requests
import time
import xml.etree.ElementTree as ET
import difflib
import numpy
import pandas


# Custom exception class for errors related to presence checking.
class PresentieError(Exception):
  def __init__(self, *args):
    super().__init__(*args)


# Make a request to a given url (tries again, when connection errors occur)
def make_request(url, max_retries=3, retry_delay=2):
  for attempt in range(max_retries):
    try:
      response = requests.get(url)
      if response.status_code == 200:
        return response
    except requests.exceptions.ConnectionError as e:
      logging.error(f"[make_request()] Connection error occurred: {e}")
    logging.info(f"[make_request()] Retrying... ({attempt+1}/{max_retries})")
    time.sleep(retry_delay)
  logging.error(
    "[make_request()] Failed to retrieve data from "
    + f"{url} after {max_retries} attempts."
  )
  return None


# Get the 'Vergaderverslagen' information from the Tweede Kamer API for a given
# date
def get_url_content(datum):
  # Create directory for log files if it doesn't exist
  if not os.path.exists("files/logs/"):
    os.makedirs("files/logs")

  with open(f"files/logs/log{str(datum)}.txt", "w"):
    pass # No content to write at the moment

  url = (
    "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
    + "/Verslag"
    + "?$filter="
    + f"year(GewijzigdOp)%20eq%20{datum.year}"
    + "%20and%20"
    + f"month(GewijzigdOp)%20eq%20{datum.month}"
    + "%20and%20"
    + f"day(GewijzigdOp)%20eq%20{datum.day}"
  )
  logging.debug(f"[get_url_content()] URL: {url}")

  response = make_request(url)
  if response and response.status_code == 200:
    return response.json()
  else:
    logging.error(f"[get_url_content()] Failed to fetch data from URL: {url}")
    return None


# Get vergader id(s) from JSON content
def get_vergader_ids(content):
  vergader_ids = [
    line["Id"] for line in content["value"] if not line.get("Verwijderd", False)
  ]
  logging.debug(f"[get_vergader_ids()] Vergader IDs: {vergader_ids}")
  return vergader_ids  


# Get 'Vergaderverslagen' for the given list of vergader id(s)
def get_verslagen(vergader_ids):
  verslagen = []
  for vergader_id in vergader_ids:
    url = (
      "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
      + f"/Verslag/{vergader_id}/resource"
    )
    logging.debug(f"[get_verslagen()] Fetching data from URL: {url}")
    response = make_request(url)
    if response:
      verslagen.append(response.json())
    else:
      logging.error(f"[get_verslagen()] Failed to fetch data from URL: {url}")
  return verslagen


# Determines the latest verslag among list of 'Vergaderverslagen'
def determine_latest_verslag(verslagen):
  default_time = datetime.min
  latest_verslag_index = -1
  max_time = default_time

  for i, verslag in enumerate(verslagen):
    try:
      root = ET.fromstring(verslag.content.decode())
    except Exception as e:
      raise PresentieError(f"Error parsing XML: {e}")

    ns = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
    if (
        root.find("./ns:zaal", namespaces=ns) != "Plenaire zaal"
        or root.get("soort", "") == "Voorpublicatie"
    ):
      continue

    timestamp = root.get("Timestamp", default_time)
    timestamp = datetime.fromisoformat(timestamp)
    logging.debug(f"[latest_verslag()] Timestamp: {timestamp}")
    if timestamp > max_time:
      max_time = timestamp
      latest_verslag_index = i

  if latest_verslag_index == -1:
    return -1

  logging.debug(
    f"[latest_verslag()] Latest verslag index: {latest_verslag_index}; "
    + f"Max time: {max_time}"
  )

  latest_verslag = verslagen[latest_verslag_index].content.decode()
  return latest_verslag


# Parse the XML received from the API and extract info about attending members
def parse_xml(verslagen):
  verslag = determine_latest_verslag(verslagen)

  if not verslag or verslag == -1:
    return -1

  try:
    root = ET.fromstring(verslag)
  except Exception as e:
    raise PresentieError(f"Error parsing XML: {e}")

  ns = {"ns": "http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0"}
  alinea_elements = root.findall(".//ns:alineaitem", namespaces=ns)

  kamerleden = None
  for alinea in alinea_elements:
    if "leden der Kamer, te weten:" in alinea.text:
      # TODO: Check if kamerleden are present in this text, instead of next one
      kamerleden = alinea.findnext(
        "{http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0}alineaitem"
      )
      if kamerleden is not None:
        kamerleden = kamerleden.text
        logging.debug(f"[parse_xml()] Attending members: {kamerleden}")
      break

  if kamerleden is None:
    return -1

  kamerleden = [
    lid.strip() for lid in 
    kamerleden.lower().rstrip(",").replace(" en ", ",").split(",")
  ]

  logging.debug(
    f"[parse_xml()] Type of attending members: {type(kamerleden)}; "
    + f"Attending members: {kamerleden}"
  )

  return kamerleden


# Checking presence of members based on list of present members
def presentie(aanwezig):
  matched = []
  afwezig = []

  print("----Afwezig:----")
  with open("files/2dekmrledn.txt", "r") as f:
    # Check who are present at vergaderingen and mark in 'matched' array
    for line in f:
      # Try to match names to list of all members (uses 90% string similarity)
      close_matches = difflib.get_close_matches(
        line.rstrip("\n"), aanwezig, 1, 0.9
      )
      logging.debug(
        f"[presentie()] close_matches: {close_matches}, "
        + f"line.rstrip(\"\\n\"): {line.rstrip("\n")}"
      )
      if close_matches:
        matched.append(close_matches[0])
      else:
        print(line.rstrip("\n"))
        afwezig.append(line.rstrip("\n"))

  print(
    f"{len(matched)} / {len(aanwezig)} kamerleden aanwezig, "
    + f"{len(afwezig)} afwezigen"
  )

  # Check if everyone has been matched
  if len(matched) != len(aanwezig):
    print(
      "Aantal Kamerleden matcht niet met het aantal aanwezige: "
      + f"is {len(matched)}, maar moet zijn {len(aanwezig)}"
    )
    unmatched = set(aanwezig) - set(matched)
    print(f"De volgende leden konden niet worden gematched: {unmatched}")

  logging.debug(f"[presentie()] Afwezig: {afwezig}")

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


# Make nice graph who is present and who is not
def make_graph(aanwezig, afwezig):
  # Parse the data into a format suitable for graph creation
  data = array_parsing(aanwezig, afwezig)

  # Code for creating the graph goes here
  # ...


# Checks the presence of members at a meeting on the specified date
def aanwezigheid(datum):
  # Check if a valid date object is passed
  if not isinstance(datum, date):
    raise PresentieError(f"{datum}({type(datum)}) is not a valid date")

  # TODO: Add a waiting text, until presentie(kamerleden) gets called
  print("Processing...")

  # Fetch the content of the meeting report for the specified date
  content = get_url_content(datum)

  # Extract the meeting IDs from the meeting report
  vergader_ids = get_vergader_ids(content)

  # If no meeting ID is found, return None for both present and absent members
  if not vergader_ids:
    return None, None

  logging.debug(f"[aanwezigheid()] Meeting ID: {vergader_ids[0]}")

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
    f.write("\n".join(aanwezig) + "\n")
    f.write("\nAfwezig:\n")
    f.write("\n".join(afwezig) + "\n")

  # Return the lists of present and absent members
  return aanwezig, afwezig


def process_single_date():
  datum_str = input("Geef een datum op (YYYY-MM-DD): ")
  try:
    datum = date.fromisoformat(datum_str)
  except ValueError:
    print("Ongeldige datumformaat. Voer de datum in het formaat YYYY-MM-DD in.")
    return [], []

  aanwezig, afwezig = aanwezigheid(datum)
  aanwezig_arr, afwezig_arr = [], []
  if aanwezig is not None and afwezig is not None:
    aanwezig_arr.extend(aanwezig)
    afwezig_arr.extend(afwezig)
  return aanwezig_arr, afwezig_arr


def process_multi_date():
  datum1_str = input("Geef een eerste datum op (YYYY-MM-DD): ")
  datum2_str = input("Geef een tweede datum op (YYYY-MM-DD): ")
  try:
    datum1 = date.fromisoformat(datum1_str)
    datum2 = date.fromisoformat(datum2_str)
  except ValueError:
    print("Ongeldige datumformaat. Voer de datum in het formaat YYYY-MM-DD in.")
    return [], []

  delta = (datum2 - datum1).days

  aanwezig_arr, afwezig_arr = [], []
  for i in range(1, delta):
    datum = datum1 + timedelta(days=i)
    if datum.isoweekday() in (6, 7):
      continue

    if datum == date.today():
      print(
        "Verslag van vandaag is er waarschijnlijk niet, "
        + "dus deze wordt niet gezocht"
      )
      continue

    aanwezig, afwezig = aanwezigheid(datum)
    if aanwezig is not None and afwezig is not None:
      aanwezig_arr.extend(aanwezig)
      afwezig_arr.extend(afwezig)
  return aanwezig_arr, afwezig_arr


def process_dates():
  while True:
    answer = input("1: Zelf datum opgeven\n2: Bereik van data\nUw keuze: ")
    if answer == "1":
      return process_single_date()
    elif answer == "2":
      return process_multi_date()
    else:
      print("Verkeerde invoer (alleen \"1\" of \"2\")")


def process_graph(aanwezig_arr, afwezig_arr):
  while True:
    answer = input("Grafiekje maken? j/n: ").lower()
    if answer == "j":
      return make_graph(aanwezig_arr, afwezig_arr)
    elif answer == "n":
      return
    else:
      print("Verkeerde invoer (alleen \"j\" of \"n\")")


def main():
  aanwezig_arr, afwezig_arr = process_dates()
  if aanwezig_arr or afwezig_arr:
    process_graph(aanwezig_arr, afwezig_arr)
  else:
    print("Geen aanwezigheidsgegevens beschikbaar om een grafiek te maken.")


if __name__ == "__main__":
  # Parse command-line arguments
  parser = argparse.ArgumentParser(
    description="Process presence status and create a graph."
  )
  parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable debug mode to print detailed output during the process.",
  )
  args = parser.parse_args()

  # Set logging level based on debug mode
  logging_level = logging.DEBUG if args.debug else logging.INFO
  logging.basicConfig(
    level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
  )

  # Call the main function to process presence status and create a graph
  main()
