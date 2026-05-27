from pathlib import Path
import json

from src.ingestion.csv_loader import (
    load_csv_data
)


def build_sequences():

    df = load_csv_data()

    grouped = df.groupby(
        "case:concept:name"
    )

    sequences = []

    for case_id, group in grouped:

        ordered_group = group.sort_values(
            by="time:timestamp"
        )

        sequence = list(
            ordered_group[
                "concept:name"
            ]
        )

        sequence_entry = {
            "case_id": case_id,
            "sequence": sequence
        }

        sequences.append(
            sequence_entry
        )

    output_path = Path(
        "data/processed/"
        "workflow_sequences.json"
    )

    output_path.parent.mkdir(
        exist_ok=True
    )

    with open(
        output_path,
        "w"
    ) as file:

        json.dump(
            sequences,
            file,
            indent=4
        )

    return sequences


if __name__ == "__main__":

    sequences = build_sequences()

    print(
        "\nWorkflow Sequences:\n"
    )

    for seq in sequences:
        print(seq)

    print(
        "\nSaved to:\n"
        "data/processed/"
        "workflow_sequences.json"
    )