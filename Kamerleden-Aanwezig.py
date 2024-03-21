from cgi import print_form
import sys
from numpy import dtype
import requests as req
import xml.etree.ElementTree as ET
import json
from datetime import date

# Get most recent 'vergaderverslag' from tweedekamer API
def getFile():
  today = date.today()
  # 'vergaderverslag' of today will only be published very late today or early tomorrow
  year = today.year
  month = today.month
  day = today.day - 1
  url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{year}%20and%20month(GewijzigdOp)%20eq%20{month}%20and%20day(GewijzigdOp)%20eq%20{day}"
  r = req.get(url)
  return r.content

# Get vergaderID from json
def vergaderID(content):
  val = json.loads(content)
  return val["value"][0]["Id"]
  
# Get 'Vergaderverslag'
def getVerslag(vergID):
  url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{vergID}/resource"
  print(url)
  r = req.get(url)
  return r.content

# Parse the XML received from the API
def parseXML(verslag):
  next = False
  kamerleden = ""
  verslag = verslag.decode()

  try:
    root = ET.fromstring(verslag)
  except:
    raise Exception("Error parsing XML")

  # Parse XML and extract specific element
  ns = {'ns': 'http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0'}
  alinea_elements  = root.findall(".//ns:alineaitem", namespaces=ns)
  for alinea in alinea_elements:
    if next:
      kamerleden = alinea.text
      break
    if "leden der Kamer, te weten:" in str(alinea.text):
      next = True
  
  # Format and transform into array
  kamerleden = kamerleden.lower().replace(" en ",",").replace(" ","").split(",")
  # Last index is invalid ez fix
  return kamerleden[:len(kamerleden)-1]

# Match names from present list to total list
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
          # print(f"mathced {target} to {source[i]}")
          return True
        else: break

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
  f = open("files/2dekmrledn.txt", 'r')
  print("----Afwezig:----")

  # Check who are present at vergaderingen and mark in 'matched' array
  for line in f:
    if stringSimilarity(line.rstrip('\n'), aanwezig, matched):
      integer += 1
    else:
      print(line.rstrip('\n'))
  
  # Not everyone has been matched
  if integer is not len(aanwezig):
    raise Exception(f"Aantal Kamerleden matcht niet met het aanwezige aantal is {integer} maar moet zijn {len(aanwezig)}")

  print(integer, "/", len(aanwezig))
  return aanwezig
    
# Make nice graph who is present and who is not
def makeGraph(aanwezig):
  pass

def main():
  content = getFile()
  vergID = vergaderID(content)
  verslag = getVerslag(vergID)
  kamerleden = parseXML(verslag)
  aanwezig = presentie(kamerleden)
  makeGraph(aanwezig)

if __name__=="__main__":
  main()