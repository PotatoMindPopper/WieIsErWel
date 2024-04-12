import requests

def get_fracties():
    response = requests.get('https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Fractie')
    return {fractie['Id']: fractie['NaamNL'] for fractie in response.json()['value']}

def get_personen():
    response = requests.get('https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Persoon?$filter=Verwijderd%20eq%20false%20and%20Functie%20eq%20%27Tweede%20Kamerlid%27')
    return {persoon['Id']: {'naam': f"{persoon['Voornamen']} {persoon['Tussenvoegsel']} {persoon['Achternaam']}".strip(), 'fractie_id': persoon['Fractielabel']} for persoon in response.json()['value']}

def get_fractie_zetel_personen():
    response = requests.get('https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/FractieZetelPersoon')
    fractie_zetel_personen = {}
    for item in response.json()['value']:
        if item['FractieZetel_Id'] not in fractie_zetel_personen:
            fractie_zetel_personen[item['FractieZetel_Id']] = []
        fractie_zetel_personen[item['FractieZetel_Id']].append(item['Persoon_Id'])
    return fractie_zetel_personen

def get_tweede_kamer_leden():
    fracties = get_fracties()
    personen = get_personen()
    fractie_zetel_personen = get_fractie_zetel_personen()

    tweede_kamer_leden = []
    for fractie_zetel_id, personen_ids in fractie_zetel_personen.items():
        fractie_naam = fracties.get(fractie_zetel_id, 'Onbekend')
        for persoon_id in personen_ids:
            persoon_info = personen.get(persoon_id)
            if persoon_info:
                tweede_kamer_leden.append({'naam': persoon_info['naam'], 'fractie': fractie_naam})
    return tweede_kamer_leden

# Ophalen van de leden van de Tweede Kamer
leden_tweede_kamer = get_tweede_kamer_leden()

# Printen van de leden van de Tweede Kamer
for lid in leden_tweede_kamer:
    print(f"Naam: {lid['naam']}, Fractie: {lid['fractie']}")
