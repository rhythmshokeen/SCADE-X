from pathlib import Path
from datetime import timedelta
import random
import pandas as pd


NORMAL_WORKFLOW = [
    "CREATE_PO",
    "APPROVE_PO",
    "SHIPMENT_CREATED",
    "INVENTORY_UPDATED",
    "PAYMENT_COMPLETED"
]


SUPPLIER_PROFILES = {
    "supplier_A": {
        "delay_factor": 1.0,
        "cost_multiplier": 1.0,
        "risk": 0.02
    },
    "supplier_B": {
        "delay_factor": 1.8,
        "cost_multiplier": 1.1,
        "risk": 0.08
    },
    "supplier_C": {
        "delay_factor": 1.3,
        "cost_multiplier": 2.2,
        "risk": 0.05
    },
    "supplier_D": {
        "delay_factor": 2.5,
        "cost_multiplier": 1.4,
        "risk": 0.15
    }
}


ROLE_USERS = {
    "CREATE_PO": [
        "buyer_1",
        "buyer_2",
        "buyer_3"
    ],
    "APPROVE_PO": [
        "manager_1",
        "manager_2"
    ],
    "SHIPMENT_CREATED": [
        "logistics_1",
        "logistics_2"
    ],
    "INVENTORY_UPDATED": [
        "warehouse_1",
        "warehouse_2"
    ],
    "PAYMENT_COMPLETED": [
        "finance_1",
        "finance_2"
    ]
}


TIME_RULES = {
    "CREATE_PO": (1, 8),
    "APPROVE_PO": (1, 24),
    "SHIPMENT_CREATED": (24, 120),
    "INVENTORY_UPDATED": (24, 168),
    "PAYMENT_COMPLETED": (48, 336)
}


def generate_synthetic_data(
    n_cases=10000,
    anomaly_ratio=0.30,
    seed=42
):

    random.seed(seed)

    rows = []

    suppliers = list(
        SUPPLIER_PROFILES.keys()
    )

    start_date = pd.Timestamp(
        "2026-01-01"
    )

    for i in range(n_cases):

        case_id = f"PO{i:05d}"

        workflow = (
            NORMAL_WORKFLOW.copy()
        )

        supplier = random.choice(
            suppliers
        )

        profile = (
            SUPPLIER_PROFILES[
                supplier
            ]
        )

        anomaly_type = "normal"
        severity = "none"
        true_anomaly = False

        rand = random.random()

        # Mild anomalies
        if rand < 0.10:

            workflow.remove(
                "INVENTORY_UPDATED"
            )

            anomaly_type = (
                "missing_inventory"
            )

            severity = "mild"
            true_anomaly = True

        elif rand < 0.15:

            workflow.insert(
                2,
                "APPROVE_PO"
            )

            anomaly_type = (
                "duplicate_approval"
            )

            severity = "mild"
            true_anomaly = True

        elif rand < 0.20:

            workflow.remove(
                "APPROVE_PO"
            )

            anomaly_type = (
                "missing_approval"
            )

            severity = "mild"
            true_anomaly = True

        # Severe anomalies
        elif rand < 0.25:

            workflow = [
                "CREATE_PO",
                "PAYMENT_COMPLETED",
                "SHIPMENT_CREATED"
            ]

            anomaly_type = (
                "payment_before_shipment"
            )

            severity = "severe"
            true_anomaly = True

        elif rand < anomaly_ratio:

            workflow = workflow[::-1]

            anomaly_type = (
                "workflow_reversal"
            )

            severity = "severe"
            true_anomaly = True

        base_cost = random.randint(
            1000,
            10000
        )

        cost = int(
            base_cost
            * profile[
                "cost_multiplier"
            ]
        )

        if true_anomaly:
            cost *= random.randint(
                2,
                5
            )

        timestamp = (
            start_date
            + timedelta(
                days=random.randint(
                    0,
                    180
                )
            )
        )

        for activity in workflow:

            min_h, max_h = (
                TIME_RULES.get(
                    activity,
                    (1, 24)
                )
            )

            delay = random.randint(
                min_h,
                max_h
            )

            delay = int(
                delay
                * profile[
                    "delay_factor"
                ]
            )

            user = random.choice(
                ROLE_USERS.get(
                    activity,
                    ["unknown_user"]
                )
            )

            rows.append({
                "case_id":
                    case_id,

                "activity":
                    activity,

                "timestamp":
                    timestamp,

                "user":
                    user,

                "supplier":
                    supplier,

                "cost":
                    cost,

                "true_anomaly":
                    true_anomaly,

                "anomaly_type":
                    anomaly_type,

                "severity":
                    severity
            })

            timestamp += timedelta(
                hours=delay
            )

    df = pd.DataFrame(rows)

    output_path = Path(
        "data/raw/"
        "synthetic_supply_chain.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    return df


if __name__ == "__main__":

    data = generate_synthetic_data()

    print(
        "\nSynthetic data generated.\n"
    )

    print(data.head())

    print("\nSaved to:")
    print(
        "data/raw/"
        "synthetic_supply_chain.csv"
    )

    print(
        "\nTotal events:",
        len(data)
    )

    print(
        "Total cases:",
        data["case_id"]
        .nunique()
    )

    print(
        "\nAnomaly distribution:"
    )

    print(
        data[
            [
                "case_id",
                "anomaly_type"
            ]
        ]
        .drop_duplicates()
        [
            "anomaly_type"
        ]
        .value_counts()
    )