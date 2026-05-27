import json
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import (
    Dataset,
    DataLoader
)


class ProcessDataset(Dataset):

    def __init__(
        self,
        token_sequences
    ):

        self.data = []

        for row in token_sequences:

            tokens = row["tokens"]

            self.data.append(
                torch.tensor(
                    tokens,
                    dtype=torch.long
                )
            )

    def __len__(self):
        return len(self.data)

    def __getitem__(
        self,
        idx
    ):
        return self.data[idx]


class ProcessTransformer(
    nn.Module
):

    def __init__(
        self,
        vocab_size,
        embed_dim=32,
        num_heads=4,
        hidden_dim=64,
        num_layers=2
    ):

        super().__init__()

        self.embedding = (
            nn.Embedding(
                vocab_size + 1,
                embed_dim
            )
        )

        encoder_layer = (
            nn.TransformerEncoderLayer(
                d_model=embed_dim,
                nhead=num_heads,
                dim_feedforward=
                hidden_dim,
                batch_first=True
            )
        )

        self.transformer = (
            nn.TransformerEncoder(
                encoder_layer,
                num_layers=
                num_layers
            )
        )

        self.output_layer = (
            nn.Linear(
                embed_dim,
                vocab_size + 1
            )
        )

    def forward(
        self,
        x
    ):

        x = self.embedding(x)

        x = self.transformer(x)

        logits = (
            self.output_layer(x)
        )

        return logits


def collate_fn(batch):

    return nn.utils.rnn.pad_sequence(
        batch,
        batch_first=True
    )


def train_model():

    device = (
        "mps"
        if torch.backends.mps
        .is_available()
        else "cpu"
    )

    print(
        f"\nUsing device: "
        f"{device}\n"
    )

    with open(
        "data/processed/"
        "tokenized_sequences.json",
        "r"
    ) as file:

        token_data = (
            json.load(file)
        )

    with open(
        "data/processed/"
        "process_vocab.json",
        "r"
    ) as file:

        vocab = json.load(
            file
        )

    dataset = (
        ProcessDataset(
            token_data
        )
    )

    loader = DataLoader(
        dataset,
        batch_size=32,
        shuffle=True,
        collate_fn=
        collate_fn
    )

    model = (
        ProcessTransformer(
            vocab_size=
            len(vocab)
        )
    )

    model.to(device)

    criterion = (
        nn.CrossEntropyLoss()
    )

    optimizer = (
        torch.optim.Adam(
            model.parameters(),
            lr=0.001
        )
    )

    epochs = 10

    for epoch in range(
        epochs
    ):

        total_loss = 0

        for batch in loader:

            batch = (
                batch.to(device)
            )

            optimizer.zero_grad()

            inputs = (
                batch[:, :-1]
            )

            targets = (
                batch[:, 1:]
            )

            outputs = (
                model(inputs)
            )

            loss = criterion(
                outputs.reshape(
                    -1,
                    outputs.shape[-1]
                ),
                targets.reshape(-1)
            )

            loss.backward()

            optimizer.step()

            total_loss += (
                loss.item()
            )

        print(
            f"Epoch "
            f"{epoch+1}"
            f"/{epochs}"
            f" | Loss: "
            f"{total_loss:.4f}"
        )

    Path(
        "models_store"
    ).mkdir(
        exist_ok=True
    )

    torch.save(
        model.state_dict(),
        "models_store/"
        "process_transformer.pth"
    )

    print(
        "\nModel saved:\n"
        "models_store/"
        "process_transformer.pth"
    )


if __name__ == "__main__":
    train_model()