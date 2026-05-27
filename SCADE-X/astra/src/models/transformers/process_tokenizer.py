from pathlib import Path
import json


def build_tokenizer():

    input_path = Path(
        "data/processed/"
        "workflow_sequences.json"
    )

    with open(input_path, "r") as file:
        workflows = json.load(file)

    unique_activities = set()

    for workflow in workflows:

        unique_activities.update(
            workflow["sequence"]
        )

    vocabulary = {
        activity: idx + 1
        for idx, activity in enumerate(
            sorted(unique_activities)
        )
    }

    tokenized_sequences = []

    for workflow in workflows:

        token_sequence = [
            vocabulary[event]
            for event in workflow[
                "sequence"
            ]
        ]

        tokenized_sequences.append({
            "case_id":
                workflow["case_id"],

            "tokens":
                token_sequence
        })

    vocab_output = Path(
        "data/processed/"
        "process_vocab.json"
    )

    token_output = Path(
        "data/processed/"
        "tokenized_sequences.json"
    )

    with open(vocab_output, "w") as file:
        json.dump(
            vocabulary,
            file,
            indent=4
        )

    with open(token_output, "w") as file:
        json.dump(
            tokenized_sequences,
            file,
            indent=4
        )

    return vocabulary, tokenized_sequences


if __name__ == "__main__":

    vocab, sequences = (
        build_tokenizer()
    )

    print(
        "\nVocabulary:\n"
    )

    print(vocab)

    print(
        "\nTokenized Sequences:\n"
    )

    for seq in sequences:
        print(seq)

    print(
        "\nSaved:\n"
        "process_vocab.json\n"
        "tokenized_sequences.json"
    )