# Description: Dit script haalt de aanwezigheid van Kamerleden op uit de
#              'vergaderverslagen' van de Tweede Kamer
#

from kamerleden_aanwezig.fetch_file import fetch_file
from kamerleden_aanwezig.extract_meeting_ids import extract_meeting_ids
from kamerleden_aanwezig.fetch_reports import fetch_reports
from kamerleden_aanwezig.parse_xml import parse_xml
from kamerleden_aanwezig.check_attendance import check_attendance
from kamerleden_aanwezig.create_chart import create_chart


def main():
    """
    Hoofdfunctionaliteit
    """
    content = fetch_file()
    meeting_ids = extract_meeting_ids(content)
    reports = fetch_reports(meeting_ids)
    if not reports:
        print("[main()] Geen 'vergaderverslag' gevonden.")
        return
    for report in reports:
        try:
            print("[main()] ================================") # TODO: Print datum of id of iets dergelijks
            kamerleden = parse_xml(report)
            attendance = check_attendance(kamerleden)
            create_chart(attendance)
        except Exception as e:
            print(f"[main()] Er is een fout opgetreden: {e}")
            continue
    # TODO: Maak een grafiek van de aanwezige Kamerleden over de verschillende
    #       'vergaderverslagen'


if __name__ == "__main__":
    main()
