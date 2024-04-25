import argparse
import logging
from datetime import date, datetime, timedelta
import os
import requests
import xml.etree.ElementTree as ET
import difflib
import numpy
import pandas


# Custom exception class for errors related to presence checking.
class PresentieError(Exception):
  def __init__(self, *args):
    super().__init__(*args)


# Make a request to a given url (tries again, when connection errors occur)
def make_request(url):
  try:
    response = requests.get(url)
  except requests.exceptions.ConnectionError as e:
    logging.info(f"[make_request()] ConnectionError occured: {e}")
    try_again = 10
    while response.status_code != 200 and try_again > 0:
      try:
        response = requests.get(url)
      except requests.exceptions.ConnectionError as e:
        logging.info(f"[make_request()] ConnectionError occured: {e}")
        try_again -= 1
        continue
  return response


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
  return response.json()


# Get vergader id(s) from JSON content
def get_vergader_ids(content):
  vergader_ids = []
  for line in content["value"]:
    if not line["Verwijderd"]:
      logging.debug(f"[get_vergader_ids()] Line: {line}")
      vergader_ids.append(line["Id"])
  return vergader_ids
  

# Get 'Vergaderverslagen' for the given list of vergader id(s)
def get_verslagen(vergader_ids):
  verslagen = []
  for vergader_id in vergader_ids:
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{vergader_id}/resource"
    logging.debug(f"[get_verslagen()] URL: {url}")
    verslagen.append(make_request(url))
  return verslagen


# Determines the latest verslag among list of 'Vergaderverslagen'
def determine_latest_verslag(verslagen):
  default_time = "0001-01-01T00:00:00.0000000+00:00"

  timestamps = []
  for verslag in verslagen:
    try:
      root = ET.fromstring(verslag.content.decode())
    except Exception as e:
      raise PresentieError(f"Error parsing XML: {e}")

    if (
        root[0][1].text != "Plenaire zaal"
        or root.attrib["soort"] == "Voorpublicatie"
    ):
      timestamps.append(datetime.fromisoformat(default_time))
      continue

    timestamp = root.get("Timestamp", default_time)
    timestamp = datetime.fromisoformat(timestamp)
    logging.debug(f"[latest_verslag()] Timestamp: {timestamp}")
    timestamps.append(timestamp)

  max_time = datetime.fromisoformat(default_time)
  max_element = -1
  for i, tijd in enumerate(timestamps):
    if tijd > max_time:
      max_time = tijd
      max_element = i

  if max_element == -1:
    return -1

  logging.debug(
    f"[latest_verslag()] Max element: {max_element}; Max time: {max_time}"
  )

  latest_verslag = verslagen[max_element].content.decode()
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

  next_alinea = False
  kamerleden = None
  for alinea in alinea_elements:
    if next_alinea:
      kamerleden = alinea.text
      logging.debug(f"[parse_xml()] Attending members: {kamerleden}")
      break
    if "leden der Kamer, te weten:" in str(alinea.text):
      # TODO: Check if kamerleden are present in this text, instead of next one
      # Set the flag to check the next alinea for attending members
      next_alinea = True

  if kamerleden is None:
    return -1

  kamerleden = (
    kamerleden
      .lower()
      .rstrip(",")
      .replace(" en ", ",")
      .replace(" ", "")
      .split(",")
  )

  logging.debug(
    f"[parse_xml()] Type of attending members: {type(kamerleden)}; "
    + f"Attending members: {kamerleden}"
  )

  return kamerleden


# Checking presence of members based on list of present members
def presentie(aanwezig):
  matched = []
  afwezig = []
  integer = 0

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
        integer += 1
      else:
        print(line.rstrip("\n"))
        afwezig.append(line.rstrip("\n"))

  print(
    f"{integer} / {len(aanwezig)} kamerleden aanwezig, {len(afwezig)} afwezigen"
  )

  # Check if everyone has been matched
  if integer != len(aanwezig):
    print(
      "Aantal Kamerleden matcht niet met het aantal aanwezige: "
      + f"is {integer}, maar moet zijn {len(aanwezig)}"
    )
    unmatched = [member for member in aanwezig if member not in matched]
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


def process_single_date():
  datum = date.fromisoformat(input("Geef een datum op (YYYY-MM-DD): "))
  aanwezig, afwezig = aanwezigheid(datum)
  aanwezig_arr, afwezig_arr = [], []
  if aanwezig and afwezig:
    aanwezig_arr.extend(aanwezig)
    afwezig_arr.extend(afwezig)
  return aanwezig_arr, afwezig_arr


def process_multi_date():
  datum1 = date.fromisoformat(input("Geef een eerste datum op (YYYY-MM-DD): "))
  datum2 = date.fromisoformat(input("Geef een tweede datum op (YYYY-MM-DD): "))
  delta = datum2 - datum1

  aanwezig_arr, afwezig_arr = [], []
  for _ in range(delta.days):
    datum1 += timedelta(days=1)
    if datum1.isoweekday() in (6, 7):
      continue

    if datum1 == date.today():
      print(
        "Verslag van vandaag is er waarschijnlijk niet, "
        + "dus deze wordt niet gezocht"
      )
      continue

    aanwezig, afwezig = aanwezigheid(datum1)
    if aanwezig and afwezig:
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
  process_graph(aanwezig_arr, afwezig_arr)


if __name__ == "__main__":
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
