import argparse
import pandas as pd
import numpy as np
import array
from cgi import print_form
import sys
from types import NoneType
from numpy import dtype
import requests as req
import xml.etree.ElementTree as ET
import json
from datetime import date, datetime, timedelta
import os

debug = False

# Create a default exception
class PresentieError(Exception):
  def __init__(self, *args: object) -> NoneType:
    super().__init__(*args)

# Get most recent 'vergaderverslag' from tweedekamer API
def get_url_content(datum):
  # Write to log file
  directory = "files/logs/"
  if not os.path.exists(directory):
    os.makedirs(directory)

  with open(f"{directory}log{str(datum)}.txt", "w"):
    # Write content to the file if needed
    pass  # Placeholder, you can write content here if required

  url = ("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
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

  response = req.get(url)

  return response.content

# Get vergaderID from json
def get_vergader_ids(content):
  val = json.loads(content)
  vergaderingen = []
  for line in val["value"]:
    if line["Verwijderd"] == False:
      if debug:
        print(line)
      vergaderingen.append(line["Id"])
  return vergaderingen
  
# Get 'Vergaderverslagen'
def get_verslagen(vergader_ids):
  response = []
  for i in range(len(vergader_ids)):
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{vergader_ids[i]}/resource"
    if debug:
      print(url)
    response.append(req.get(url))
  return response

def latest_verslag(verslagen):
  tijden = []
  max_time = 0
  max_element = -1
  for i in range(len(verslagen)):
    verslag = verslagen[i].content.decode()

    try:
      root = ET.fromstring(verslag)
    except Exception as e:
      raise PresentieError(f"Error parsing XML: {e}")

    if root[0][1].text != "Plenaire zaal" or root.attrib['soort'] == "Voorpublicatie":
      tijden.append(0)
      continue
    
    timestamp = root.get("Timestamp", "0000-00-00T00:00:00.0000000+00:00")
    datetime_object = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
    if debug:
      print(datetime_object)
    tijden.append(root.attrib["Timestamp"].split('T')[1].split(':')[0])

  for j in range(len(tijden)):
    if int(tijden[j]) > max_time:
      max_time = int(tijden[j])
      max_element = j

  if debug:
    print(max_element, max_time)
  return max_element


# Parse the XML received from the API
def parse_xml(verslagen):
  laatste_vers = latest_verslag(verslagen)
  
  if laatste_vers == -1:
    return -1
  
  verslag = verslagen[laatste_vers].content.decode()
  
  try:
    root = ET.fromstring(verslag)
  except Exception as e:
    raise PresentieError(f"Error parsing XML: {e}")

  # Parse XML and extract specific element
  ns = {'ns': 'http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0'}
  alinea_elements  = root.findall(".//ns:alineaitem", namespaces=ns)

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
  kamerleden = kamerleden.lower().rstrip(",").replace(" en ", ",").replace(" ", "").split(",")

  if debug:
    print(type(kamerleden), kamerleden)
  
  return kamerleden

# Match names from present list (source) to total list (target)
def stringSimilarity(target, source, matched):
  consistent = 0
  for i in range(len(source)):
    if source[i] in matched:
      continue
    consistent = 0
    for j in range(len(target)):
      # If the length of one of the strings has been reached or if enough letters are matched
      if j >= len(source[i]) or j >= len(target) or consistent >= len(source[i]) - 1:
        # If enough letters are matched accept it
        if consistent >= len(source[i]) - 1:
          matched.append(source[i])
          if debug:
            print(f"mathced {target} to {source[i]}")
          return True
        else:break
      # Compare letters
      if target[j] == source[i][j]:
        consistent += 1
  # No match found
  return False

# Checking presence
def presentie(aanwezig):
  matched = []
  afwezig = []
  integer = 0
  # Open file with all members
  f = open("files/2dekmrledn.txt", 'r')
  print("----Afwezig:----")

  # Check who are present at vergaderingen and mark in 'matched' array
  for line in f:
    if stringSimilarity(line.rstrip('\n'), aanwezig, matched):
      integer += 1
    else:
      print(line.rstrip('\n'))
      afwezig.append(line.rstrip('\n'))
      pass
  
  print(f"{integer} / {len(aanwezig)} kamerleden aanwezig, {len(afwezig)} afwezigen")

  # Check if everyone has been matched
  if integer != len(aanwezig):
    print(f"Aantal Kamerleden matcht niet met het aanwezige aantal is {integer} maar moet zijn {len(aanwezig)}")

  print(afwezig)

  return aanwezig, afwezig
    
# Parse array to DataFrame
def arrayParsing(aanwezig, afwezig):
  afwezig = np.array(afwezig, dtype=object)
  count = np.arange(1, 2*len(afwezig), 0.5, dtype=int)
  afwezig = afwezig.reshape(-1)
  df = pd.DataFrame(data=afwezig, columns=["afwezig"])
  df['counts'] = pd.DataFrame(data=count)
  print(df.groupby('afwezig').count().sort_values(by=["counts"], ascending=False))

# Make nice graph who is present and who is not
def make_graph(aanwezig, afwezig):
  data = arrayParsing(aanwezig, afwezig)

def aanwezigheid(datum):
  # Check of er wel een echte datum doorgegeven is
  assert isinstance(datum, date)

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


def convert_to_date(string):
  # Check the format for the string (YYYY-MM-DD)
  check_string = string.split("-")
  assert len(check_string[0]) == 4
  assert len(check_string[1]) == 2
  assert len(check_string[2]) == 2
  
  return date.fromisoformat(string)


def range_of_dates():
  datum1 = convert_to_date(input("Geef een eerste datum op (YYYY-MM-DD): "))
  datum2 = convert_to_date(input("Geef een tweede datum op (YYYY-MM-DD): "))
  delta = datum2 - datum1

  aanwezig_arr = afwezig_arr = []
  for _ in range(delta.days): # TODO: Maybe convert this to using multiprocessing
    datum1 += timedelta(days=1)
    if datum1.isoweekday == 6 or datum1.isoweekday == 7:
      continue

    if datum1 == date.today():
      print("Verslag van vandaag is er waarschijnlijk niet, dus deze wordt niet gezocht")
      continue

    aanwezig, afwezig = aanwezigheid(datum1)
    if aanwezig and afwezig:
      aanwezig_arr += aanwezig
      afwezig_arr += afwezig
  
  return aanwezig_arr, afwezig_arr


def main():
  aanwezig_arr = []
  afwezig_arr = []

  answer = input("1: Zelf datum opgeven\n2: Bereik van data\nUw keuze: ")
  if int(answer) == 1:
    datum = convert_to_date(input("Geef een datum op (YYYY-MM-DD): "))
    aanwezig, afwezig = aanwezigheid(datum)
  elif int(answer) == 2:
    aanwezig_arr, afwezig_arr = range_of_dates()
  else:
    print("Verkeerde invoer")

  while True:
    answer = input("Grafiekje maken? j/n: \n").lower()
    if answer == "j":
      make_graph(aanwezig_arr, afwezig_arr)
      break
    elif answer == "n":
      break
    else:
      print("Invoer is j/n")
  


if __name__=="__main__":
  parser = argparse.ArgumentParser(description="Set debug mode for printing")
  parser.add_argument("--debug", default=False, type=bool, metavar=debug,
                      help="Set debug to True if you want to see the output of\
                            the getting and parsing process")
  args = parser.parse_args()
  debug = args.debug
  main()