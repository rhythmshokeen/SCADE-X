import json
from pathlib import Path

import torch
import torch.nn.functional as F

from src.models.transformers.process_transformer import (
    ProcessTransformer
)


def score_sequences():

    device = (
        "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )

    with open(
        "data/processed/process_vocab.json",
        "r"
    ) as file:

        vocab = json.load(file)

    with open(
        "data/processed/tokenized_sequences.json",
        "r"
    ) as file:

        sequences = json.load(file)

    model = ProcessTransformer(
        vocab_size=len(vocab)
    )

    model.load_state_dict(
        torch.load(
            "models_store/process_transformer.pth",
            map_location=device
        )
    )

    model.to(device)
    model.eval()

    results = []

    with torch.no_grad():

        for row in sequences:

            tokens = row["tokens"]

            if len(tokens) < 2:
                continue

            inputs = torch.tensor(
                [tokens[:-1]],
                dtype=torch.long
            ).to(device)

            targets = tokens[1:]

            outputs = model(inputs)

            probs = F.softmax(
                outputs,
                dim=-1
            )

            confidence_scores = []

            for i, target in enumerate(targets):

                confidence = probs[
                    0,
                    i,
                    target
                ].item()

                confidence_scores.append(
                    confidence
                )

            avg_confidence = sum(
                confidence_scores
            ) / len(
                confidence_scores
            )

            anomaly_score = (
                1 - avg_confidence
            )

            results.append({
                "case_id":
                    row["case_id"],

                "avg_confidence":
                    round(
                        avg_confidence,
                        4
                    ),

                "behavioral_anomaly_score":
                    round(
                        anomaly_score,
                        4
                    )
            })

    output_path = Path(
        "data/processed/"
        "transformer_scores.json"
    )

    with open(
        output_path,
        "w"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print(
        "\nTransformer Behavioral Scores:\n"
    )

    for result in results[:20]:
        print(result)

    print(
        "\nSaved to:\n"
        "data/processed/"
        "transformer_scores.json"
    )


if __name__ == "__main__":
    score_sequences()