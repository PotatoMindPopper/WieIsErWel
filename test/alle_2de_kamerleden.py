import requests


API_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"


def get_fracties():
    """
    Haalt de fracties op

    :return: Een dictionary met fractie ID's als keys en fractie namen als
             values
    """

    # Voorbeeld van een request naar de Tweede Kamer API en de response
    # response = requests.get("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Fractie")
    # response ziet er als volgt uit:
    # {
    #     "@odata.context": "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Fractie",
    #     "value": [
    #       {
    #         "Id": "e133cd98-1b5c-47e0-ac4d-031f34199767",
    #         "Nummer": 2783,
    #         "Afkorting": "BRINK",
    #         "NaamNL": "Brinkman",
    #         "NaamEN": "Brinkman",
    #         "AantalZetels": null,
    #         "AantalStemmen": null,
    #         "DatumActief": "2012-03-20T00:00:00+01:00",
    #         "DatumInactief": "2012-09-19T00:00:00+02:00",
    #         "ContentType": null,
    #         "ContentLength": null,
    #         "GewijzigdOp": "2023-08-29T13:09:50+02:00",
    #         "ApiGewijzigdOp": "2023-08-29T11:23:41.8713166Z",
    #         "Verwijderd": false
    #       },
    #       ...
    #     ]
    # }

    # Haal de fracties op
    response = requests.get(API_URL + "/Fractie")

    # Maak een dictionary met fractie ID's als keys en fractie namen als values
    fracties = {}
    # TODO: Gebruik "UTF-8" encoding voor de Nederlandse namen van de fracties
    for fractie in response.json()["value"]:
        fractie_id = fractie["Id"]
        # Check of de fractie "stemmen" of "zetels" heeft, zo niet, verwijder de
        # fractie
        if "AantalZetels" not in fractie and "AantalStemmen" not in fractie:
            # Attributen "AantalZetels" en "AantalStemmen" zijn niet aanwezig
            continue
        if "AantalZetels" in fractie and not fractie["AantalZetels"]:
            # Attribuut "AantalZetels" is aanwezig, maar de waarde is leeg
            continue
        if "AantalStemmen" in fractie and not fractie["AantalStemmen"]:
            # Attribuut "AantalStemmen" is aanwezig, maar de waarde is leeg
            continue
        
        # Check of de fractie een Nederlandse naam heeft, zo niet gebruik de
        # Engelse naam, zo niet gebruik de afkorting
        if "NaamNL" in fractie and fractie["NaamNL"]:
            fracties[fractie_id] = fractie["NaamNL"]
        elif "NaamEN" in fractie and fractie["NaamEN"]:
            fracties[fractie_id] = fractie["NaamEN"]
        else:
            fracties[fractie_id] = fractie["Afkorting"]
    return fracties
    
    # return {fractie["Id"]: fractie["NaamNL"] for fractie in response.json()["value"]}


def get_fractie_zetels():
    """
    Haalt de fractie zetels op

    :return: Een dictionary met fractie zetel ID's als keys en fractie ID's als
             values
    """

    # Voorbeeld van een request naar de Tweede Kamer API en de response
    # response = requests.get("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/FractieZetel")
    # response ziet er als volgt uit:
    # {
    #     "@odata.context": "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#FractieZetel",
    #     "value": [
    #       {
    #         "Id": "a5fea518-fe51-4b51-8e87-00095827eedb",
    #         "Gewicht": 37,
    #         "Fractie_Id": "65129918-f256-4975-9da4-488da34d6695",
    #         "GewijzigdOp": "2023-12-06T12:30:05+01:00",
    #         "ApiGewijzigdOp": "2023-12-06T13:51:23.4143455Z",
    #         "Verwijderd": false
    #       },
    #       ...
    #     ]
    # }

    # Haal de fractie zetels op
    response = requests.get(API_URL + "/FractieZetel")
    # Maak een dictionary met fractie zetel ID's als keys en fractie ID's als
    # values
    return {zetel["Id"]: zetel["Fractie_Id"] for zetel in response.json()["value"]}


def get_personen():
    """
    Haalt de personen op

    :return: Een dictionary met persoon ID's als keys en persoon informatie als
             values
    """

    # Voorbeeld van een request naar de Tweede Kamer API en de response
    # response = requests.get("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Persoon?$filter=Verwijderd%20eq%20false%20and%20Functie%20eq%20%27Tweede%20Kamerlid%27")
    # response ziet er als volgt uit:
    # {
    #     "@odata.context": "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Persoon",
    #     "value": [
    #       {
    #         "Id": "1c889902-6ede-427c-8682-000f683fffaa",
    #         "Nummer": 2491,
    #         "Titels": "MA",
    #         "Initialen": "M.",
    #         "Tussenvoegsel": null,
    #         "Achternaam": "Agema",
    #         "Voornamen": "Marie-Fleur",
    #         "Roepnaam": "Fleur",
    #         "Geslacht": "vrouw",
    #         "Functie": "Tweede Kamerlid",
    #         "Geboortedatum": "1976-09-16T00:00:00+02:00",
    #         "Geboorteplaats": "Purmerend",
    #         "Geboorteland": "Nederland",
    #         "Overlijdensdatum": null,
    #         "Overlijdensplaats": null,
    #         "Woonplaats": "'s-Gravenhage",
    #         "Land": "NL",
    #         "Fractielabel": null,
    #         "ContentType": "image/jpeg",
    #         "ContentLength": 456668,
    #         "GewijzigdOp": "2023-12-01T15:59:58+01:00",
    #         "ApiGewijzigdOp": "2023-12-01T15:00:24.6710401Z",
    #         "Verwijderd": false
    #       },
    #       ...
    #     ]
    # }

    # Haal de personen op
    response = requests.get(
        API_URL
        + "/Persoon"
        + "?"
        + "$filter="
        + "Verwijderd%20eq%20false"
        + "%20and%20"
        + "Functie%20eq%20%27Tweede%20Kamerlid%27"
    )

    # Maak een dictionary met persoon ID's als keys en persoon informatie als
    # values
    personen = {}
    # TODO: Gebruik "UTF-8" encoding voor de namen van de personen
    for persoon in response.json()["value"]:
        persoon_id = persoon["Id"]
        voornaam = persoon[
            "Voornamen"
        ]  # TODO: Kies tussen de voornamen of de roepnaam van de persoon
        tussenvoegsel = persoon["Tussenvoegsel"] or ""
        achternaam = persoon["Achternaam"]
        if tussenvoegsel:
            naam = f"{voornaam} {tussenvoegsel} {achternaam}"
        else:
            naam = f"{voornaam} {achternaam}"
        personen[persoon_id] = {
            "naam": naam,
            "fractie": None,  # NOTE: Wordt later ingevuld
            "functie": None,  # NOTE: Wordt later ingevuld
        }
    return personen


def get_fractie_zetel_personen():
    """
    Haalt de fractie zetel personen op

    :return: Een dictionary met fractie zetel ID's als keys en persoon ID's en
             functies als values
    """

    # Voorbeeld van een request naar de Tweede Kamer API en de response
    # response = requests.get("https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/FractieZetelPersoon")
    # response ziet er als volgt uit:
    # {
    #     "@odata.context": "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#FractieZetelPersoon",
    #     "value": [
    #       {
    #         "Id": "2788ce23-d15d-471d-9cfb-0014cf484003",
    #         "FractieZetel_Id": "5fc85674-7330-4c3d-ae46-cd14e1f3f4dd",
    #         "Persoon_Id": "1456a009-770b-4820-8919-55287a5780a7",
    #         "Functie": "Lid",
    #         "Van": "2012-09-20T00:00:00+02:00",
    #         "TotEnMet": "2019-02-19T00:00:00+01:00",
    #         "GewijzigdOp": "2023-08-29T13:10:25+02:00",
    #         "ApiGewijzigdOp": "2023-08-29T13:29:23.0613959Z",
    #         "Verwijderd": false
    #       },
    #       ...
    #     ]
    # }

    # Haal de fractie zetel personen op
    response = requests.get(API_URL + "/FractieZetelPersoon")
    # Maak een dictionary met fractie zetel ID's als keys en persoon ID's en
    # functies als values
    return {
        fractie_zetel_persoon["Id"]: (
            fractie_zetel_persoon["Persoon_Id"],
            fractie_zetel_persoon["Functie"],
        )
        for fractie_zetel_persoon in response.json()["value"]
    }


def get_tweede_kamer_leden():
    fracties = get_fracties()
    fractie_zetels = get_fractie_zetels()
    personen = get_personen()
    fractie_zetel_personen = get_fractie_zetel_personen()

    import json

    print(
        "[get_tweede_kamer_leden()] Fracties:", json.dumps(fracties, indent=4)
    )  # Debugging
    print(
        "[get_tweede_kamer_leden()] Fractie zetels:",
        json.dumps(fractie_zetels, indent=4),
    )  # Debugging
    print(
        "[get_tweede_kamer_leden()] Personen:", json.dumps(personen, indent=4)
    )  # Debugging
    print(
        "[get_tweede_kamer_leden()] Fractie zetel personen:",
        json.dumps(fractie_zetel_personen, indent=4),
    )  # Debugging

    # Maak een lijst van leden van de Tweede Kamer
    tweede_kamer_leden = []
    for fractie_zetel_id, (persoon_id, functie) in fractie_zetel_personen.items():
        # fractie_id = fractie_zetels[fractie_zetel_id]
        # fractie_naam = fracties[fractie_id]
        # persoon = personen[persoon_id]
        # leden_tweede_kamer.append(
        #     {
        #         "naam": persoon["naam"],
        #         "fractie": fractie_naam,
        #         "functie": functie,
        #     }
        # )
        fractie_id = fractie_zetels.get(fractie_zetel_id)
        fractie_naam = fracties.get(fractie_id, "Onbekend")
        persoon_info = personen.get(persoon_id)
        print(
            f"[get_tweede_kamer_leden()] Fractie ID: {fractie_id}, Fractie naam: {fractie_naam}"
        )
        print(
            f"[get_tweede_kamer_leden()] Persoon ID: {persoon_id}, Persoon info: {persoon_info}"
        )
        if persoon_info:
            tweede_kamer_leden.append(
                {
                    "naam": persoon_info["naam"],
                    "fractie": fractie_naam,
                    "functie": functie,
                }
            )
    return tweede_kamer_leden


# Ophalen van de leden van de Tweede Kamer
leden_tweede_kamer = get_tweede_kamer_leden()

# Printen van de leden van de Tweede Kamer
for lid in leden_tweede_kamer:
    print(f"Naam: {lid['naam']}, Fractie: {lid['fractie']}, Functie: {lid['functie']}")
