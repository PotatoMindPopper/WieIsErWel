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

    print(f"[match_personen_leden()] Onbekende leden(size: {len(onbekende_leden)}): {json.dumps(onbekende_leden, indent=4)}")
    
    return leden_tweede_kamer


def get_tweede_kamer_leden_2(leden_tweede_kamer):
    # https://www.tweedekamer.nl/kamerleden_en_commissies/alle_kamerleden
    
    # Haal de personen informatie op
    personen = get_personen()
    
    # Check of er leden missen in de lijst van leden van de Tweede Kamer
    for persoon_id in personen:
        # if persoon_id not in [lid["naam"] for lid in leden_tweede_kamer]:
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

    print(f"[get_tweede_kamer_leden_2()] Onbekende leden(size: {len(onbekende_leden)}): {json.dumps(onbekende_leden, indent=4)}")
    
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
    for member in soup.find_all("div", class_="u-member-card-height u-break-inside--avoid-at-print m-card"):
        # Zoek naar de naam van het lid van de Tweede Kamer
        name = member.find("h3", class_="u-mt--collapse")
        if not name:
            print("[get_tweede_kamer_leden_2()] Naam niet gevonden.")
            continue
        # TODO: Ga door naar de <a> tag, want de naam van het lid van de Tweede Kamer staat in de tekst van de <a> tag
        name = name.text.strip()
        # Zoek naar de fractie van het lid van de Tweede Kamer
        party = member.find("span", class_="u-text-size--small u-text-color--primary")
        if not party:
            print("[get_tweede_kamer_leden_2()] Fractie niet gevonden.")
            continue
        party = party.text.strip()
        # Check of het lid van de Tweede Kamer al in de lijst van leden van de Tweede Kamer staat
        if name not in [lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] for lid in leden_tweede_kamer]:
            # Voeg het lid van de Tweede Kamer toe aan de lijst van leden van de Tweede Kamer
            leden_tweede_kamer.append(
                {
                    "naam": {
                        "volledig": name,
                        "roepnaam": name.split(" ", 1)[0],
                        "voornaam": name.split(" ", 1)[0],
                        "tussenvoegsel": "Onbekend", # TODO: Probeer het tussenvoegsel uit de naam te halen (bijv. "van")
                        "achternaam": name.split(" ", 1)[1],
                    },
                    "fractie": {
                        "nederlands": party, # Hetzelfde als de afkorting
                        "engels": "Unknown",
                        "afkorting": party, # Alleen de afkorting is bekend
                    },
                    "functie": "Onbekend",
                    "persoon_id": "Onbekend", # TODO: Haal dit uit de avatar url
                    "fractie_zetel_id": "Onbekend", # Laat de fractie zetel ID leeg
                    "fractie_id": "Onbekend", # Laat de fractie ID leeg
                }
            )
        elif party not in [lid["fractie"]["nederlands"] for lid in leden_tweede_kamer]:
            # Voeg de fractie toe aan het lid van de Tweede Kamer
            for lid in leden_tweede_kamer:
                if lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] == name:
                    lid["fractie"]["nederlands"] = party
                    lid["fractie"]["engels"] = "Unknown"
                    lid["fractie"]["afkorting"] = party
                    break
        else:
            # Voeg de functie toe aan het lid van de Tweede Kamer
            for lid in leden_tweede_kamer:
                if lid["naam"]["roepnaam"] + lid["naam"]["achternaam"] == name:
                    lid["functie"] = "Lid"
                    break
        
    return leden_tweede_kamer

# Test de functie
leden_tweede_kamer = get_tweede_kamer_leden_2([])
print(f"[get_tweede_kamer_leden_2()] Leden van de Tweede Kamer (size: {len(leden_tweede_kamer)}): {json.dumps(leden_tweede_kamer, indent=4)}")
