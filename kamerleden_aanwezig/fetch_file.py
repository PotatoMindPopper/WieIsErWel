# Description: Haalt het meest recente 'vergaderverslag' op van de Tweede Kamer API
#
# Omdat het meest recente 'vergaderverslag' vaak pas de volgende dag wordt
# gepubliceerd, wordt de datum van gisteren gebruikt om het meest recente
# 'vergaderverslag' op te halen.
#
# :return: De inhoud van het meest recente 'vergaderverslag'
#

from datetime import datetime, timedelta
import requests


def fetch_file():
    """
    Haalt het meest recente 'vergaderverslag' op van de Tweede Kamer API

    Omdat het meest recente 'vergaderverslag' vaak pas de volgende dag wordt
    gepubliceerd, wordt de datum van gisteren gebruikt om het meest recente
    'vergaderverslag' op te halen.

    :return: De inhoud van het meest recente 'vergaderverslag'
    """
    yesterday = datetime.now() - timedelta(days=1)
    year, month, day = yesterday.year, yesterday.month, yesterday.day

    day = 11  # Debugging

    # Voorbeeld van een response zonder 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[]}
    # Voorbeeld van een response met 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[{"Id":"8176b1f5-b5a8-46f1-9d2c-5e66fd14604f","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":92511,"GewijzigdOp":"2024-04-09T20:08:55.5222825+02:00","ApiGewijzigdOp":"2024-04-10T10:06:34.0095628Z","Verwijderd":false,"Vergadering_Id":"7b123e97-8255-4ac9-adb8-da471891ebca"}]}
    # Voorbeeld van een response met meer dan 1 'value':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[{"Id":"3849ce47-0ccb-417d-b883-7c13f31900e5","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":8614,"GewijzigdOp":"2024-04-05T11:27:48.3707026+02:00","ApiGewijzigdOp":"2024-04-05T09:30:02.6745625Z","Verwijderd":false,"Vergadering_Id":"099c5fab-95f1-407b-bf3c-87e9341e6172"},{"Id":"db2dd399-803b-4147-a92c-ebccdf21d23d","Soort":"Voorpublicatie","Status":"Casco","ContentType":"text/xml","ContentLength":8614,"GewijzigdOp":"2024-04-05T08:37:03.0559843+02:00","ApiGewijzigdOp":"2024-04-05T06:37:33.2206437Z","Verwijderd":false,"Vergadering_Id":"099c5fab-95f1-407b-bf3c-87e9341e6172"}]}
    # Voorbeeld van een response met compleet 'vergaderverslag':
    # {"@odata.context":"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/$metadata#Verslag","value":[{"Id":"7dedd180-7475-4ef4-be81-01963f6e8906","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":173379,"GewijzigdOp":"2024-04-04T10:08:22.7466935+02:00","ApiGewijzigdOp":"2024-04-04T08:09:19.1204238Z","Verwijderd":false,"Vergadering_Id":"505319ed-705f-4f7d-b244-3794ea67ea9b"},{"Id":"bce9fc3c-ffb2-4332-9307-04742c39c35d","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1345672,"GewijzigdOp":"2024-04-04T23:22:52.0263598+02:00","ApiGewijzigdOp":"2024-04-04T21:23:51.237277Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"70b8c22e-871f-42c5-83d6-0ccc7870e980","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1353505,"GewijzigdOp":"2024-04-04T23:31:45.810932+02:00","ApiGewijzigdOp":"2024-04-04T21:35:29.574477Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"d1a14aed-1bd3-4aac-9ae5-2533288f2320","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":373072,"GewijzigdOp":"2024-04-04T15:45:06.1401037+02:00","ApiGewijzigdOp":"2024-04-04T13:45:48.1957918Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"813667dd-4fc7-47b0-8041-3ddb44fbe08b","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1167440,"GewijzigdOp":"2024-04-04T21:45:27.1564723+02:00","ApiGewijzigdOp":"2024-04-04T19:46:51.8415558Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"1b927ea0-ee03-4c30-960a-4b31d8ed8555","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1046537,"GewijzigdOp":"2024-04-04T00:01:12.3852858+02:00","ApiGewijzigdOp":"2024-04-03T22:02:06.9234256Z","Verwijderd":false,"Vergadering_Id":"c212f69a-b79b-4b71-87b4-451a564447c9"},{"Id":"010218a6-9fc3-4c5e-84bf-6bb5e8d18d12","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":808757,"GewijzigdOp":"2024-04-04T19:01:39.6860091+02:00","ApiGewijzigdOp":"2024-04-04T17:02:31.0019271Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"31f3a717-762e-4345-a33b-72052e89c3d5","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1084760,"GewijzigdOp":"2024-04-04T20:32:01.5252439+02:00","ApiGewijzigdOp":"2024-04-04T18:32:57.1520866Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"f1f71904-3bbd-4fe9-bf2b-7fc1baa7d06d","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":213454,"GewijzigdOp":"2024-04-04T14:06:07.8112692+02:00","ApiGewijzigdOp":"2024-04-04T12:07:20.4082851Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"f4ce5c17-97b0-491a-93b5-905d9b65794e","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":673169,"GewijzigdOp":"2024-04-04T17:19:22.5851193+02:00","ApiGewijzigdOp":"2024-04-04T15:20:57.1534537Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"c08d2c58-24b1-4406-ad26-cd236099a45b","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":278051,"GewijzigdOp":"2024-04-04T15:42:22.1291509+02:00","ApiGewijzigdOp":"2024-04-04T13:43:25.5592884Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"0e01ff58-9a64-478d-b5ba-d6bf429a6792","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":258603,"GewijzigdOp":"2024-04-04T16:09:17.1530587+02:00","ApiGewijzigdOp":"2024-04-04T14:11:41.5559455Z","Verwijderd":false,"Vergadering_Id":"fb33e864-a4d1-4d84-9409-1a5306a93953"},{"Id":"81fe53ce-ce31-4dba-843d-e0defc7a3368","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":118343,"GewijzigdOp":"2024-04-04T13:25:24.7639295+02:00","ApiGewijzigdOp":"2024-04-04T11:26:01.7020949Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"b690d8a7-3936-4510-a5d1-e2cd3d68e953","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":258355,"GewijzigdOp":"2024-04-04T14:40:13.8613895+02:00","ApiGewijzigdOp":"2024-04-04T12:41:42.0599952Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"4b1c6dc4-05aa-4c37-b96c-e31074bdfde4","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1067931,"GewijzigdOp":"2024-04-04T00:24:07.6390733+02:00","ApiGewijzigdOp":"2024-04-03T22:27:12.8167896Z","Verwijderd":false,"Vergadering_Id":"c212f69a-b79b-4b71-87b4-451a564447c9"},{"Id":"3a1a1c06-fdae-4030-87d0-edd5e183e0e6","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":1249433,"GewijzigdOp":"2024-04-04T22:40:02.787392+02:00","ApiGewijzigdOp":"2024-04-04T20:41:10.5712446Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"},{"Id":"d15e8b1c-4bdd-44bc-b963-f7ea6daf451f","Soort":"Tussenpublicatie","Status":"Ongecorrigeerd","ContentType":"text/xml","ContentLength":541473,"GewijzigdOp":"2024-04-04T16:36:26.9966646+02:00","ApiGewijzigdOp":"2024-04-04T14:38:27.060681Z","Verwijderd":false,"Vergadering_Id":"768b0ba2-6209-4e0c-811d-f7c5165fc72d"}]}
    # Voorbeeld van een response met een error:
    # {"error":{"code":"","message":"The query specified in the URI is not valid. A binary operator with incompatible types was detected. Found operand types 'Edm.Int32' and 'Edm.String' for operator kind 'Equal'."}}

    while True:
        url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag?$filter=year(GewijzigdOp)%20eq%20{year}%20and%20month(GewijzigdOp)%20eq%20{month}%20and%20day(GewijzigdOp)%20eq%20{day}"
        print("[fetch_file()] URL:", url)  # Debugging
        response = requests.get(url)
        data = response.json()

        if data["value"] and len(data["value"]) > 0:
            # Als value niet leeg is, return de content
            return response.content  # TODO: Return data["value"]
        elif data["value"] and len(data["value"]) == 0:
            # Als value leeg is, probeer de dag ervoor
            print(
                f"[fetch_file()] Geen 'vergaderverslag' gevonden voor {day}-{month}-{year}. Probeer de dag ervoor."
            )
            yesterday = yesterday - timedelta(days=1)
            year, month, day = yesterday.year, yesterday.month, yesterday.day
            print(f"[fetch_file()] Probeer {day}-{month}-{year}")
            # Wacht 1 seconde voordat de volgende fetch wordt uitgevoerd
            import time  # Importeer alleen als het nodig is

            time.sleep(1)
        else:
            # Als value niet bestaat, kijken of er een error is
            if "error" in data:
                raise Exception(data["error"]["message"])
            else:
                raise Exception(
                    "Geen 'value' gevonden in de response van de API"
                )  # Onbekende error

    return None
