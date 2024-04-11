# Description: Fetches the content of the 'Vergaderverslag' of the most recent meeting
#
# :param meeting_ids: The ID and Type of the most recent 'vergaderverslag'
# :return: The content of the 'Vergaderverslag'
#

import requests


def fetch_reports(meeting_ids):
    """
    Haalt de inhoud van 'Vergaderverslag' op

    :param meeting_id: Het ID van het meest recente 'vergaderverslag'
    :return: De inhoud van het 'Vergaderverslag'
    """
    reports = []
    for meeting_id, meeting_type in meeting_ids:  # TODO: Add meeting_date
        url = f"https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0/Verslag/{meeting_id}/resource"
        print("[fetch_report()] URL:", url)  # Debugging
        response = requests.get(url)
        content = response.content
        reports.append((content, meeting_type))
    return reports
