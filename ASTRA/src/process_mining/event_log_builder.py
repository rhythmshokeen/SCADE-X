from pm4py.objects.conversion.log import converter

from src.ingestion.csv_loader import (
    load_csv_data
)


def build_event_log():

    df = load_csv_data()

    event_log = converter.apply(
        df,
        variant=converter.Variants.TO_EVENT_LOG,
        parameters={
            converter.Variants.TO_EVENT_LOG.value.Parameters.CASE_ID_KEY:
            "case:concept:name"
        }
    )

    return event_log


if __name__ == "__main__":

    log = build_event_log()

    print("\nEvent log created.\n")

    print(f"Total cases: {len(log)}")

    print("\nFirst trace:\n")

    for event in log[0]:
        print(event)