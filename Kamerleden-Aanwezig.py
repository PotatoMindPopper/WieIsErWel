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

import argparse

debug = False

# Get most recent 'vergaderverslag' from tweedekamer API
def getURLContent(datum):
  # Write to log file
  f = open(f"files/logs/log{str(datum)}.txt", "w")
  f.close() 
  year = datum.year
  month = datum.month
  day = datum.day
  url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{year}%20and%20month(GewijzigdOp)%20eq%20{month}%20and%20day(GewijzigdOp)%20eq%20{day}"
  if debug:
    print(url)
  r = req.get(url)
  return r.content

# Get vergaderID from json
def vergaderID(content):
  val = json.loads(content)
  vergaderingen = []
  for line in val["value"]:
    if line["Verwijderd"] == False:
      if debug:
        print(line)
      vergaderingen.append(line["Id"])
  return vergaderingen
  
# Get 'Vergaderverslagen'
def getVerslag(vergID):
  r = []
  for i in range(len(vergID)):
    url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{vergID[i]}/resource"
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

    if root[0][1].text != "Plenaire zaal" or root.attrib['soort'] == "Voorpublicatie":
      tijden.append(0)
      continue
    
    tijden.append(root.attrib["Timestamp"].split('T')[1].split(':')[0])

  for j in range(len(tijden)):
    if int(tijden[j]) > max:
      max = int(tijden[j])
      max_element = j

  if debug:
    print(max_element, max)
  return max_element


# Parse the XML received from the API
def parseXML(verslagen):
  next = False
  kamerleden = ""

  laatste_vers = laatste(verslagen)
  
  if  laatste_vers == -1:
    return -1
  
  verslag = verslagen[laatste_vers].content.decode()
  
  try:
    root = ET.fromstring(verslag)
  except:
    raise Exception("Error parsing XML")

  # Parse XML and extract specific element
  ns = {'ns': 'http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0'}
  alinea_elements  = root.findall(".//ns:alineaitem", namespaces=ns)
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
  if type(kamerleden) == type(None):
    return -1
  # Format and transform into array
  kamerleden = kamerleden.lower().replace(" en ",",").replace(" ","").split(",")
  if debug:
    print(type(kamerleden), kamerleden)
  # Last index is invalid ez fix
  return kamerleden[:len(kamerleden)-1]

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
  
  print(integer, "/", len(aanwezig), len(afwezig), "afwezigen")
  # Check if everyone has been matched
  if integer is not len(aanwezig):
    print(f"Aantal Kamerleden matcht niet met het aanwezige aantal is {integer} maar moet zijn {len(aanwezig)}")
  print(afwezig)
  return aanwezig, afwezig
    

def arrayParsing(aanwezig, afwezig):
  afwezig = np.array(afwezig, dtype=object)
  count = np.arange(1, 2*len(afwezig), 0.5, dtype=int)
  afwezig = afwezig.reshape(-1)
  df = pd.DataFrame(data=afwezig, columns=["afwezig"])
  df['counts'] = pd.DataFrame(data=count)
  print(df.groupby('afwezig').count().sort_values(by=["counts"], ascending=False))

# Make nice graph who is present and who is not
def makeGraph(aanwezig, afwezig):
  data = arrayParsing(aanwezig, afwezig)

def aanwezigheid(datum):
  # Check of er wel een echte datum doorgegeven is
  assert type(datum) == date
  # Haal het verslag op
  content = getURLContent(datum)
  # Haal de vergaderID uit het verslag
  vergID = vergaderID(content)
  # Als de ID nul is, is er geen vergaderverslag
  if len(vergID) == 0:
    return None, None

  if debug:
    print(vergID[0])
  # Haal het verslag op a.h.v. de vergaderID
  verslagen = getVerslag(vergID)
  # Haal de lijst met kamerleden uit de verslagen
  kamerleden = parseXML(verslagen)
  # Check of er wel echt iets uitgekomen is
  if kamerleden == -1:
    return None, None
  # Geef de aanwezigen terug aan de bovenliggende functie 
  aanwezig, afwezig = presentie(kamerleden)
  f = open(f"files/logs/log{datum}.txt", "a")
  f.write("Aanwezig:\n")
  for str in aanwezig:
    f.write(str + '\n')
  f.write("\nAfwezig:\n")
  for str in afwezig:
    f.write(str + '\n')
  f.close()

  return aanwezig, afwezig
  

def main():
  str = input("1: Zelf datum opgeven \n2: Bereik van data: ")
  aanwezig = ""
  aanwezig_arr = []
  afwezig_arr = []
  if int(str) == 1:
    str = input("Geef een datum op (YYY-MM-DD): ")
    # Check de invoer voor yyyy-mm-dd
    assert str.split('-')[0].__len__() == 4
    assert str.split('-')[1].__len__() == 2
    assert str.split('-')[2].__len__() == 2
    datum = date.fromisoformat(str)
    aanwezig, afwezig = aanwezigheid(datum)
  elif int(str) == 2:
    str1 = input("Geef een eerste datum op (YYY-MM-DD): ")
    str2 = input("Geef een tweede datum op (YYY-MM-DD): ")

    assert str1.split('-')[0].__len__() == 4
    assert str1.split('-')[1].__len__() == 2
    assert str1.split('-')[2].__len__() == 2
    datum1 = date.fromisoformat(str1)

    assert str2.split('-')[0].__len__() == 4
    assert str2.split('-')[1].__len__() == 2
    assert str2.split('-')[2].__len__() == 2
    datum2 = date.fromisoformat(str2)

    delta = datum2 - datum1
    
    for _ in range(delta.days):
      datum1 += timedelta(days=1)
      if datum1.isoweekday == 6 or datum1.isoweekday == 7:
        continue

      if(datum1 == date.today()):
        print("Verslag van vandaag is er waarschijnlijk niet, dus deze wordt niet gezocht")
        continue

      aanwezig, afwezig = aanwezigheid(datum1)
      if type(aanwezig) == type(None) or type(afwezig) == type(None):
        continue

      aanwezig_arr += aanwezig
      afwezig_arr += afwezig
  else:
    print("Verkeerde invoer")
  bezig = True
  while bezig:
    str = input("Grafiekje maken? j/n: \n")
    if str == "j" or str == "J":
      makeGraph(aanwezig_arr, afwezig_arr)
      bezig = False
    elif str == "n" or str == "N":
      bezig = False
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