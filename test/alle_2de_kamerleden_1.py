from alle_2de_kamerleden import get_personen
import requests
import json


def match_personen_leden(personen, leden_tweede_kamer):
    # Check of er leden missen in de lijst van leden van de Tweede Kamer
    for persoon_id in personen:
        if persoon_id not in [lid["persoon_id"] for lid in leden_tweede_kamer]:
            # Voeg de persoon toe aan de lijst van leden van de Tweede Kamer
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
                    "fractie_zetel_id": "Onbekend", # Laat de fractie zetel ID leeg
                    "fractie_id": "Onbekend", # Laat de fractie ID leeg
                }
            )
        
    # Check of er "Onbekend"-de velden zijn
    onbekende_leden = []
    for lid in leden_tweede_kamer:
        if lid["fractie"]["nederlands"] == "Onbekend":
            onbekende_leden.append(lid)
        elif lid["functie"] == "Onbekend":
            onbekende_leden.append(lid)

    # print(f"[match_personen_leden()] Onbekende leden(size: {len(onbekende_leden)}): {json.dumps(onbekende_leden, indent=4)}")
    
    return leden_tweede_kamer


def get_tweede_kamer_leden_2(leden_tweede_kamer):
    
    # Haal de personen informatie op
    personen = get_personen()

    # Check of de personen informatie is opgehaald
    if not personen:
        print("[get_tweede_kamer_leden_2()] Personen informatie niet opgehaald.")
        return leden_tweede_kamer
    
    # Check of de personen informatie redelijk overeenkomt met de lijst van
    # leden van de Tweede Kamer
    leden_tweede_kamer = match_personen_leden(personen, leden_tweede_kamer)
    
    # Haal de website op van de Tweede Kamer
    response = requests.get("https://www.tweedekamer.nl/kamerleden_en_commissies/alle_kamerleden")
    
    # Check of de website van de Tweede Kamer is opgehaald
    if response.status_code != 200:
        print(f"[get_tweede_kamer_leden_2()] Status code: {response.status_code}")
        return leden_tweede_kamer
    
    # Parse de website van de Tweede Kamer
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Check of de website van de Tweede Kamer is geparsed
    if not soup:
        print("[get_tweede_kamer_leden_2()] De website van de Tweede Kamer is niet geparsed.")
        return leden_tweede_kamer
    
    # Voorbeeld van een lid van de Tweede Kamer op de website van de Tweede Kamer
    # <div class="t-grid t-grid--none-at-print">
    #   <div class="t-grid__col t-grid__col--full t-grid__col--half-at-tiny t-grid__col--third-at-small">
    #     <div data-history-node-id="9573" class="u-member-card-height u-break-inside--avoid-at-print m-card">
    #       <div class="m-card__main">
    #         <div class="m-card__content">
    #           <div class="u-display--flex u-align-self--start u-align-items--center u-g--small">
    #             <figure class="m-avatar">
    #               <img loading="lazy" class="m-avatar__image"
    #                 src="./Alle Kamerleden _ Tweede Kamer der Staten-Generaal_files/12941235-4f71-4670-bc25-08180586437d.jpg"
    #                 width="75" height="100" alt="" />
    #             </figure>
    #
    #             <div class="u-display--flex u-flex-direction--column">
    #               <h3 class="u-mt--collapse">
    #                 <a href="https://www.tweedekamer.nl/kamerleden_en_commissies/alle_kamerleden/aardema-m-pvv"
    #                   class="u-text-size--large u-text-weight--bold u-text-color--primary u-text-decoration--none u-text-line-height--tiny">Max
    #                   Aardema</a>
    #               </h3>
    #               <span class="u-text-size--small u-text-color--primary">PVV</span>
    #             </div>
    #           </div>
    #
    #           <table class="u-text-size--small u-text-color--default">
    #             <tbody>
    #               <tr>
    #                 <th scope="row" class="u-width--50 u-text-weight--normal u-p--collapse">
    #                   Woonplaats
    #                 </th>
    #                 <td class="u-width--50 u-p--collapse">
    #                   Drachten
    #                 </td>
    #               </tr>
    #               <tr>
    #                 <th scope="row" class="u-width--50 u-text-weight--normal u-p--collapse">
    #                   Leeftijd
    #                 </th>
    #                 <td class="u-width--50 u-p--collapse">61 jaar</td>
    #               </tr>
    #               <tr>
    #                 <th scope="row" class="u-width--50 u-text-weight--normal u-p--collapse">
    #                   Anciënniteit
    #                 </th>
    #                 <td class="u-width--50 u-p--collapse">
    #                   129 dagen
    #                 </td>
    #               </tr>
    #             </tbody>
    #           </table>
    #         </div>
    #       </div>
    #     </div>
    #   </div>
    #   <div class="t-grid__col t-grid__col--full t-grid__col--half-at-tiny t-grid__col--third-at-small">
    #     <div data-history-node-id="6019" class="u-member-card-height u-break-inside--avoid-at-print m-card">
    #       <div class="m-card__main">
    #         <div class="m-card__content">
    #           <div class="u-display--flex u-align-self--start u-align-items--center u-g--small">
    #             <figure class="m-avatar">
    #               <img loading="lazy" class="m-avatar__image"
    #                 src="./Alle Kamerleden _ Tweede Kamer der Staten-Generaal_files/397c857a-fda0-414d-8fdc-8288cd3284aa.jpg"
    #                 width="75" height="100" alt="" />
    #             </figure>
    #
    #             <div class="u-display--flex u-flex-direction--column">
    #               <h3 class="u-mt--collapse">
    #                 <a href="https://www.tweedekamer.nl/kamerleden_en_commissies/alle_kamerleden/aartsen-aa-vvd"
    #                   class="u-text-size--large u-text-weight--bold u-text-color--primary u-text-decoration--none u-text-line-height--tiny">Thierry
    #                   Aartsen</a>
    #               </h3>
    #               <span class="u-text-size--small u-text-color--primary">VVD</span>
    #             </div>
    #           </div>
    #
    #           <table class="u-text-size--small u-text-color--default">
    # ...
    
    # Zoek naar de leden van de Tweede Kamer
    member_cards = soup.find_all("div", class_="u-member-card-height u-break-inside--avoid-at-print m-card")
    if not member_cards:
        print("[get_tweede_kamer_leden_2()] Leden van de Tweede Kamer niet gevonden.")
        return leden_tweede_kamer
    
    # Maak een lijst van tussenvoegsels
    tussenvoegsels = [
        # fmt: off
        "aan",
        "af",
        "bij",
        "de", "den", "der", "d'",
        "het", "'t",
        "in",
        "onder",
        "op",
        "over",
        "'s",
        "'t",
        "te", "ten", "ter",
        "tot",
        "uit", "uijt",
        "van",
        "ver",
        "voor",
        "aan de", "aan den", "aan der", "aan het", "aan 't",
        "bij de", "bij den", "bij het", "bij 't",
        "boven d'",
        "de die", "de die le", "de l'", "de la", "de las", "de le", "de van der",
        "in de", "in den", "in der", "in het", "in 't",
        "onder de", "onder den", "onder het", "onder 't",
        "over de", "over den", "over het", "over 't",
        "op de", "op den", "op der", "op gen", "op het", "op 't", "op ten",
        "van de", "van de l'", "van den", "van der", "van gen", "van het", "van la", "van 't", "van ter",
        "uit de", "uit den", "uit het", "uit 't", "uit te", "uit ten",
        "uijt de", "uijt den", "uijt het", "uijt 't", "uijt te", "uijt ten",
        "voor de", "voor den", "voor in 't",
        "a",
        "al",
        "am",
        "auf",
        "aus",
        "ben", "bin",
        "da",
        "dal", "dalla", "della",
        "das", "die", "den", "der", "des",
        "deca",
        "degli",
        "dei",
        "del",
        "di",
        "do",
        "don",
        "dos",
        "du",
        "el",
        "i",
        "im",
        "L",
        "la", "las",
        "le", "les",
        "lo", "los",
        "o'",
        "tho", "thoe", "thor", "to", "toe",
        "unter",
        "vom", "von",
        "vor",
        "zu", "zum", "zur",
        "am de",
        "auf dem", "auf den", "auf der", "auf ter",
        "aus dem", "aus den", "aus der", "aus 'm",
        "die le",
        "von dem", "von den", "von der", "von 't",
        "vor der",
        # fmt: on
    ]
    
    # Ga door de leden van de Tweede Kamer
    member_info = []
    
    # Zoek naar de namen van de leden van de Tweede Kamer
    for member_card in member_cards:
        # Maak een dictionary voor het lid van de Tweede Kamer
        member = {}
        
        # Zoek naar de naam van het lid van de Tweede Kamer
        naam = {
            "volledig": "",
            "roepnaam": "",
            "voornaam": "",
            "tussenvoegsel": "",
            "achternaam": "",
        }
        # Zoek naar de parent met een zoekbare class
        name = member_card.find("h3", class_="u-mt--collapse")
        if not name:
            print("[get_tweede_kamer_leden_2()] Naam niet gevonden.")
            continue
        # Zoek naar de <a> tag, want de naam van het lid van de Tweede Kamer
        # staat in de tekst van de <a> tag
        name = name.find("a")
        if not name:
            print("[get_tweede_kamer_leden_2()] Naam niet gevonden.")
            continue
        # Sla de naam van het lid van de Tweede Kamer op
        name = name.text.strip()
        # Sla de volledige naam van het lid van de Tweede Kamer op
        naam["volledig"] = name
        # Splits de naam van het lid van de Tweede Kamer
        gesplitste_naam = name.split(" ")
        # Sla de roepnaam van het lid van de Tweede Kamer op
        naam["roepnaam"] = gesplitste_naam[0]
        # Probeer te zoeken naar een tussenvoegsel in de naam van het lid van de
        # Tweede Kamer
        for tussenvoegsel in tussenvoegsels:
            # Zoek naar het tussenvoegsel in de naam van het lid van de Tweede
            # Kamer (tussen de meest linkse en meest rechtse naam)
            if tussenvoegsel in gesplitste_naam[1:-1]:
                naam["tussenvoegsel"] = tussenvoegsel
                break
        # Sla de voornamen van het lid van de Tweede Kamer op (op basis van het
        # gevonden tussenvoegsel, check dus of het tussenvoegsel is gevonden)
        if naam["tussenvoegsel"]:
            tussenvoegsel_index = gesplitste_naam.index(naam["tussenvoegsel"])
            # Sla de voornaam van het lid van de Tweede Kamer op (vanaf de
            # eerste naam tot de naam voor het tussenvoegsel)
            naam["voornaam"] = " ".join(gesplitste_naam[:tussenvoegsel_index])
            # Sla de achternaam van het lid van de Tweede Kamer op (vanaf de
            # naam na het tussenvoegsel tot de laatste naam)
            naam["achternaam"] = " ".join(gesplitste_naam[tussenvoegsel_index+1:])
        else:
            # Sla de voornaam van het lid van de Tweede Kamer op (alleen de
            # eerste naam)
            naam["voornaam"] = gesplitste_naam[:-1]
            # Sla de achternaam van het lid van de Tweede Kamer op (alleen de
            # laatste naam)
            naam["achternaam"] = gesplitste_naam[-1]
        # Sla de naam van het lid van de Tweede Kamer op
        member["naam"] = naam

        # Zoek naar de fractie van het lid van de Tweede Kamer
        party = member_card.find("span", class_="u-text-size--small u-text-color--primary")
        if not party:
            print("[get_tweede_kamer_leden_2()] Fractie niet gevonden.")
            continue
        party = party.text.strip()
        # Sla de fractie van het lid van de Tweede Kamer op
        member["fractie"] = {
            "nederlands": party, # Hetzelfde als de afkorting
            "engels": party, # Hetzelfde als de afkorting
            "afkorting": party, # Alleen de afkorting is bekend
        }
        
        # Zoek naar ids gebonden aan de leden van de Tweede Kamer
        # Zoek naar de persoon ID van het lid van de Tweede Kamer
        person_id = member_card.find("img", class_="m-avatar__image")
        if not person_id:
            print("[get_tweede_kamer_leden_2()] Persoon ID niet gevonden.")
            continue
        person_id = person_id["src"].split("/")[-1].split(".")[0]
        # Zoek naar zelf gebruikte ID van het lid van de Tweede Kamer
        call_id = member_card.find("a")["href"].split("/")[-1]
        # Gebruik alles tot de laatste "-" in de call ID (dit is de fractie)
        call_id = call_id.rsplit("-", 1)[0]
        # Sla de persoon ID van het lid van de Tweede Kamer op
        member["persoon_id"] = person_id
        # Sla de call ID van het lid van de Tweede Kamer op
        member["call_id"] = call_id # TODO: Moet misschien nog een keer gesplitst worden
        
        # Sla de functie van het lid van de Tweede Kamer op
        member["functie"] = "Lid"
        
        # Voeg het lid van de Tweede Kamer toe aan de lijst van leden van de
        # Tweede Kamer
        member_info.append(member)
        
    # Check of de leden van de Tweede Kamer zijn gevonden
    if not member_info:
        print("[get_tweede_kamer_leden_2()] Leden van de Tweede Kamer niet gevonden.")
        return leden_tweede_kamer
    
    # Check of de leden van de Tweede Kamer zijn toegevoegd
    if not leden_tweede_kamer:
        leden_tweede_kamer = member_info
    else:
        # Check of de leden van de Tweede Kamer al in de lijst van leden van de
        # Tweede Kamer staan
        # TODO: Check persoon_id en daarna de rest van de informatie, om te kijken wat overschreven moet worden
        for member in member_info:
            if member["naam"]["volledig"] not in [lid["naam"]["volledig"] for lid in leden_tweede_kamer]:
                leden_tweede_kamer.append(member)
                
    return leden_tweede_kamer
        
    # # Check of het lid van de Tweede Kamer al in de lijst van leden van de Tweede Kamer staat
    # if name not in [lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] for lid in leden_tweede_kamer]:
    #     # TODO: Maak eerst het naam onderdeel van het lid van de Tweede Kamer
    #     # Voeg het lid van de Tweede Kamer toe aan de lijst van leden van de Tweede Kamer
    #     leden_tweede_kamer.append(
    #         {
    #             "naam": {
    #                 "volledig": name,
    #                 "roepnaam": name.split(" ", 1)[0],
    #                 "voornaam": name.split(" ", 1)[0],
    #                 "tussenvoegsel": "Onbekend", # TODO: Probeer het tussenvoegsel uit de naam te halen (bijv. "van")
    #                 "achternaam": name.split(" ", 1)[1],
    #             },
    #             "fractie": {
    #                 "nederlands": party, # Hetzelfde als de afkorting
    #                 "engels": "Unknown",
    #                 "afkorting": party, # Alleen de afkorting is bekend
    #             },
    #             "functie": "Onbekend",
    #             "persoon_id": person_id,
    #             "fractie_zetel_id": call_id, # Laat de fractie zetel ID leeg # TODO: Plaats de call_id ergens anders
    #             "fractie_id": "Onbekend", # Laat de fractie ID leeg
    #         }
    #     )
        
    # # Check of de fractie van het lid van de Tweede Kamer al in de lijst van leden van de Tweede Kamer staat
    # if party not in [lid["fractie"]["nederlands"] for lid in leden_tweede_kamer]:
    #     # Voeg de fractie toe aan het lid van de Tweede Kamer
    #     for lid in leden_tweede_kamer:
    #         if lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] == name:
    #             lid["fractie"]["nederlands"] = party
    #             lid["fractie"]["engels"] = party
    #             lid["fractie"]["afkorting"] = party
    #             break
    
    # # Voeg de functie toe aan het lid van de Tweede Kamer
    # for lid in leden_tweede_kamer:
    #     if lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] == name:
    #         lid["functie"] = "Lid"
    #         break
        
    
    
    # # Zoek naar de leden van de Tweede Kamer
    # for member in soup.find_all("div", class_="u-member-card-height u-break-inside--avoid-at-print m-card"):
    #     # Zoek naar de naam van het lid van de Tweede Kamer
    #     name = member.find("h3", class_="u-mt--collapse")
    #     if not name:
    #         print("[get_tweede_kamer_leden_2()] Naam niet gevonden.")
    #         continue
    #     # TODO: Ga door naar de <a> tag, want de naam van het lid van de Tweede Kamer staat in de tekst van de <a> tag
    #     name = name.text.strip()
    #     # Zoek naar de fractie van het lid van de Tweede Kamer
    #     party = member.find("span", class_="u-text-size--small u-text-color--primary")
    #     if not party:
    #         print("[get_tweede_kamer_leden_2()] Fractie niet gevonden.")
    #         continue
    #     party = party.text.strip()
    #     # Check of het lid van de Tweede Kamer al in de lijst van leden van de Tweede Kamer staat
    #     if name not in [lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] for lid in leden_tweede_kamer]:
    #         # Voeg het lid van de Tweede Kamer toe aan de lijst van leden van de Tweede Kamer
    #         leden_tweede_kamer.append(
    #             {
    #                 "naam": {
    #                     "volledig": name,
    #                     "roepnaam": name.split(" ", 1)[0],
    #                     "voornaam": name.split(" ", 1)[0],
    #                     "tussenvoegsel": "Onbekend", # TODO: Probeer het tussenvoegsel uit de naam te halen (bijv. "van")
    #                     "achternaam": name.split(" ", 1)[1],
    #                 },
    #                 "fractie": {
    #                     "nederlands": party, # Hetzelfde als de afkorting
    #                     "engels": "Unknown",
    #                     "afkorting": party, # Alleen de afkorting is bekend
    #                 },
    #                 "functie": "Onbekend",
    #                 "persoon_id": "Onbekend", # TODO: Haal dit uit de avatar url
    #                 "fractie_zetel_id": "Onbekend", # Laat de fractie zetel ID leeg
    #                 "fractie_id": "Onbekend", # Laat de fractie ID leeg
    #             }
    #         )
    #     elif party not in [lid["fractie"]["nederlands"] for lid in leden_tweede_kamer]:
    #         # Voeg de fractie toe aan het lid van de Tweede Kamer
    #         for lid in leden_tweede_kamer:
    #             if lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] == name:
    #                 lid["fractie"]["nederlands"] = party
    #                 lid["fractie"]["engels"] = "Unknown"
    #                 lid["fractie"]["afkorting"] = party
    #                 break
    #     else:
    #         # Voeg de functie toe aan het lid van de Tweede Kamer
    #         for lid in leden_tweede_kamer:
    #             if lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] == name:
    #                 lid["functie"] = "Lid"
    #                 break
        
    # return leden_tweede_kamer

# Test de functie
leden_tweede_kamer = get_tweede_kamer_leden_2([])
print(f"[get_tweede_kamer_leden_2()] Leden van de Tweede Kamer (size: {len(leden_tweede_kamer)}): {json.dumps(leden_tweede_kamer, indent=4)}")
