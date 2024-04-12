import requests
import json
import datetime


API_URL = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
CACHE_DAYS = 1


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
        # TODO: Check of er onderdelen ge-strip-t moeten worden, blijkbaar hebben sommige namen een extra spatie tussen de voornaam en het tussenvoegsel
        persoon_id = persoon["Id"]
        voornaam = persoon[
            "Voornamen"
        ]  # TODO: Kies tussen de voornamen of de roepnaam van de persoon (of beide) # TODO: Strip de voornamen van de persoon
        tussenvoegsel = persoon["Tussenvoegsel"] or ""
        achternaam = persoon["Achternaam"]
        if tussenvoegsel:
            naam = f"{voornaam} {tussenvoegsel} {achternaam}"
        else:
            naam = f"{voornaam} {achternaam}"
        personen[persoon_id] = {
            # "naam": naam, # TODO: Maybe convert this to a dictionary with first name, last name, etc.
            "naam": {
                "volledig": naam,
                "roepnaam": persoon["Roepnaam"],
                "voornaam": voornaam,
                "tussenvoegsel": tussenvoegsel,
                "achternaam": achternaam,
            },
            "fractie": None,  # NOTE: Wordt later ingevuld
            "functie": None,  # NOTE: Wordt later ingevuld
            "persoon_id": persoon_id,
            "fractie_zetel_id": None,  # NOTE: Wordt later ingevuld
            "fractie_id": None,  # NOTE: Wordt later ingevuld
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
        fractie_zetel_persoon["Persoon_Id"]: (
            fractie_zetel_persoon["FractieZetel_Id"],
            fractie_zetel_persoon["Functie"],
        )
        for fractie_zetel_persoon in response.json()["value"]
    }


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
        # # TODO: Maybe convert this to a dictionary with Dutch name, English name, etc.
        # if "NaamNL" in fractie and fractie["NaamNL"]:
        #     fracties[fractie_id] = fractie["NaamNL"]
        # elif "NaamEN" in fractie and fractie["NaamEN"]:
        #     fracties[fractie_id] = fractie["NaamEN"]
        # else:
        #     fracties[fractie_id] = fractie["Afkorting"]
        fracties[fractie_id] = {
            "nederlands": fractie["NaamNL"],
            "engels": fractie["NaamEN"],
            "afkorting": fractie["Afkorting"],
        }
    return fracties

    # return {fractie["Id"]: fractie["NaamNL"] for fractie in response.json()["value"]}


def get_tweede_kamer_leden():
    """
    Haalt de leden van de Tweede Kamer op

    :return: Een lijst van leden van de Tweede Kamer
    """

    # Haal de personen informatie op
    personen = get_personen()
    # Haal de informatie op met links tussen fractie zetels en personen
    fractie_zetel_personen = get_fractie_zetel_personen()
    # Haal de informatie op van de fractie zetels die bij een fractie horen
    fractie_zetels = get_fractie_zetels()
    # Haal de informatie op van de fracties
    fracties = get_fracties()

    import json

    print(
        f"[get_tweede_kamer_leden()] Personen(size: {len(personen)}): {json.dumps(personen, indent=4)}"
    )  # Debugging
    print(
        f"[get_tweede_kamer_leden()] Fractie zetel personen(size: {len(fractie_zetel_personen)}): {json.dumps(fractie_zetel_personen, indent=4)}"
    )  # Debugging
    print(
        f"[get_tweede_kamer_leden()] Fractie zetels(size: {len(fractie_zetels)}): {json.dumps(fractie_zetels, indent=4)}"
    )  # Debugging
    print(
        f"[get_tweede_kamer_leden()] Fracties(size: {len(fracties)}): {json.dumps(fracties, indent=4)}"
    )  # Debugging

    # Maak een lijst van leden van de Tweede Kamer (Let op: er kunnen meer
    # fractie_zetel_personen zijn dan personen)
    leden_tweede_kamer = []
    for persoon_id in personen:
        if persoon_id in fractie_zetel_personen:
            fractie_zetel_id, functie = fractie_zetel_personen.get(persoon_id)
            if not fractie_zetel_id:
                # print(f"[get_tweede_kamer_leden()] Fractie zetel ID niet gevonden voor persoon ID: {persoon_id}")
                # continue
                leden_tweede_kamer.append(
                    {
                        "naam": personen[persoon_id]["naam"],
                        "fractie": {
                            "nederlands": "Onbekend",
                            "engels": "Unknown",
                            "afkorting": "ONB",
                        },
                        "functie": functie,
                        "persoon_id": persoon_id,
                        "fractie_zetel_id": "Onbekend",
                        "fractie_id": "Onbekend",
                    }
                )
                continue
            fractie_id = fractie_zetels.get(fractie_zetel_id)
            if not fractie_id:
                # print(f"[get_tweede_kamer_leden()] Fractie zetel niet gevonden voor persoon ID: {persoon_id}")
                # continue
                leden_tweede_kamer.append(
                    {
                        "naam": personen[persoon_id]["naam"],
                        "fractie": {
                            "nederlands": "Onbekend",
                            "engels": "Unknown",
                            "afkorting": "ONB",
                        },
                        "functie": functie,
                        "persoon_id": persoon_id,
                        "fractie_zetel_id": fractie_zetel_id,
                        "fractie_id": "Onbekend",
                    }
                )
                continue
            fractie = fracties.get(fractie_id)
            if not fractie:
                # print(f"[get_tweede_kamer_leden()] Fractie niet gevonden voor persoon ID: {persoon_id}")
                # continue
                leden_tweede_kamer.append(
                    {
                        "naam": personen[persoon_id]["naam"],
                        "fractie": {
                            "nederlands": "Onbekend",
                            "engels": "Unknown",
                            "afkorting": "ONB",
                        },
                        "functie": functie,
                        "persoon_id": persoon_id,
                        "fractie_zetel_id": fractie_zetel_id,
                        "fractie_id": fractie_id,
                    }
                )
                continue
            leden_tweede_kamer.append(
                {
                    "naam": personen[persoon_id]["naam"],
                    "fractie": fractie,
                    "functie": functie,
                    "persoon_id": persoon_id,
                    "fractie_zetel_id": fractie_zetel_id,
                    "fractie_id": fractie_id,
                }
            )
        else:
            # print(f"[get_tweede_kamer_leden()] Persoon ID niet gevonden: {persoon_id}")
            leden_tweede_kamer.append(
                {
                    "naam": personen[persoon_id]["naam"],
                    "fractie": {
                        "nederlands": "Onbekend",
                        "engels": "Unknown",
                        "afkorting": "ONB",
                    },
                    "functie": "Onbekend",
                    "persoon_id": persoon_id,
                    "fractie_zetel_id": "Onbekend",
                    "fractie_id": "Onbekend",
                }
            )
    return leden_tweede_kamer


def get_tweede_kamer_leden_2(leden_tweede_kamer):
    return leden_tweede_kamer


def save_tweede_kamer_leden(leden_tweede_kamer):
    """
    Slaat de leden van de Tweede Kamer op

    Doe dit als onderdeel van een cache mechanisme

    :param leden_tweede_kamer: Een lijst van leden van de Tweede Kamer
    """

    data = {
        "datum": datetime.datetime.now().isoformat(),
        "leden_tweede_kamer": leden_tweede_kamer,
    }

    # Sla de leden van de Tweede Kamer op
    with open("leden_tweede_kamer.json", "w", encoding="utf-8") as file:
        json.dump(data, file)

    # DEBUGGING
    with open("test_leden_tweede_kamer.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_tweede_kamer_leden():
    """
    Laadt de leden van de Tweede Kamer

    Doe dit als onderdeel van een cache mechanisme

    :return: Een lijst van leden van de Tweede Kamer
    """

    try:
        # Laad de leden van de Tweede Kamer
        with open("leden_tweede_kamer.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return None


def main():
    """
    Hoofdfunctionaliteit
    """

    # Laden van de leden van de Tweede Kamer
    data = load_tweede_kamer_leden()

    # Check de cache datum van de leden van de Tweede Kamer
    if data:
        print(f"[main()] Cache datum: {data['datum']}")
    if data and datetime.datetime.now() - datetime.datetime.fromisoformat(
        data["datum"]
    ) < datetime.timedelta(days=7):
        print("[main()] Gebruik maken van de cache.")
        leden_tweede_kamer = data["leden_tweede_kamer"]
    else:
        # Ophalen van de leden van de Tweede Kamer
        leden_tweede_kamer = get_tweede_kamer_leden()

    # Check of er leden van de Tweede Kamer zijn gevonden
    if not leden_tweede_kamer:
        print("[main()] Geen leden van de Tweede Kamer gevonden.")
        return

    # Check het aantal leden van de Tweede Kamer
    if len(leden_tweede_kamer) != 150:
        print(f"[main()] Aantal leden van de Tweede Kamer: {len(leden_tweede_kamer)}")
        # Vraag de gebruiker of er nog doorgegaan moet worden met zoeken
        # if input("Doorgaan met zoeken? (ja/nee): ").lower() != "ja":
        #     print("[main()] Zoeken is gestopt.")
        #     return
        if input("Doorgaan met zoeken? (ja/nee): ").lower() == "ja":
            # TODO: Doe hetzelfde als er 'Onbekend'-de velden zijn
            print("[main()] Zoeken wordt voortgezet.")
            leden_tweede_kamer = get_tweede_kamer_leden_2(leden_tweede_kamer)
    else:
        print("[main()] Alle leden van de Tweede Kamer zijn gevonden.")

    # Printen van de leden van de Tweede Kamer
    for lid in leden_tweede_kamer:
        # print(f"[main()] Naam: {lid['naam']}, Fractie: {lid['fractie']}, Functie: {lid['functie']}")
        print(
            f"Naam: {lid['naam']['volledig']}, Fractie: {lid['fractie']['nederlands']}, Functie: {lid['functie']}"
        )

    # Sorteer de leden van de Tweede Kamer op achternaam
    leden_tweede_kamer.sort(key=lambda lid: lid["naam"]["achternaam"])

    # Printen van de leden van de Tweede Kamer gesorteerd op achternaam
    print("\nLeden van de Tweede Kamer gesorteerd op achternaam:")
    for lid in leden_tweede_kamer:
        print(
            f"Naam: {lid['naam']['volledig']}, Fractie: {lid['fractie']['nederlands']}, Functie: {lid['functie']}"
        )

    # Opslaan van de leden van de Tweede Kamer als onderdeel van een cache
    if not data or datetime.datetime.now() - datetime.datetime.fromisoformat(
        data["datum"]
    ) >= datetime.timedelta(days=7):
        # Opslaan van de leden van de Tweede Kamer
        save_tweede_kamer_leden(leden_tweede_kamer)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and (
        sys.argv[1] == "test"
        or sys.argv[1] == "debug"
        or sys.argv[1] == "cache"
        or sys.argv[1] == "clear"
        or sys.argv[1] == "clean"
        or sys.argv[1] == "cleanup"
        or sys.argv[1] == "remove"
        or sys.argv[1] == "delete"
        or sys.argv[1] == "clearcache"
        or sys.argv[1] == "cleancache"
    ):
        # Clean up the cache
        import os

        if os.path.exists("leden_tweede_kamer.json"):
            os.remove("leden_tweede_kamer.json")
            print("[main()] Cache is opgeschoond.")
        else:
            print("[main()] Cache is leeg.")

    main()
