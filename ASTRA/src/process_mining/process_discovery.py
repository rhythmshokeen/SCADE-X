import pm4py

from src.process_mining.event_log_builder import (
    build_event_log
)


def discover_process():

    log = build_event_log()

    process_tree = pm4py.discover_process_tree_inductive(
        log
    )

    print("\nDiscovered process tree:\n")
    print(process_tree)

    variants = pm4py.get_variants(log)

    print("\nWorkflow variants:\n")

    for idx, variant in enumerate(
        variants.keys(),
        start=1
    ):
        print(
            f"Variant {idx}: {variant}"
        )


if __name__ == "__main__":
    discover_process()