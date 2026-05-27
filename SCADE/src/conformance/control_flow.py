import pandas as pd
import pm4py


def score(full_log, net, im, fm) -> pd.DataFrame:
    """
    Run token-based replay on every case in full_log against the Petri net.

    Returns one row per case with:
      case_id         — case identifier
      cf_score        — fitness (0–1), 1 = perfect conformance
      missing_tokens  — tokens the model needed but the trace didn't provide
      remaining_tokens— tokens left over after replay (trace did extra things)
      missing_acts    — activity names that were problematic (skipped/misplaced)
      extra_acts      — activity names replayed beyond model expectation
    """
    replayed = pm4py.conformance_diagnostics_token_based_replay(
        full_log, net, im, fm
    )

    # Case IDs are stored in each trace's attributes inside the EventLog object
    case_ids = [
        trace.attributes["concept:name"]
        for trace in full_log
    ]

    rows = []
    for case_id, result in zip(case_ids, replayed):
        # transitions_with_problems holds transitions that fired with missing tokens
        problem_transitions = result.get("transitions_with_problems", [])
        missing_acts = [t.label for t in problem_transitions if t.label is not None]

        # activated_transitions lists every transition that fired
        activated = result.get("activated_transitions", [])
        activated_labels = [t.label for t in activated if t.label is not None]

        rows.append({
            "case_id":          case_id,
            "cf_score":         round(result["trace_fitness"], 4),
            "missing_tokens":   result["missing_tokens"],
            "remaining_tokens": result["remaining_tokens"],
            "missing_acts":     missing_acts,
            "extra_acts":       [],  # populated by attack mapper from sequence analysis
            "activated_acts":   activated_labels,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    from src.preprocess import load_and_format, split_log, to_event_log
    from src.discover import load_model

    df = load_and_format("data/supply_chain_log.csv")
    train_df, full_df = split_log(df)
    full_log = to_event_log(full_df)
    net, im, fm = load_model()

    cf = score(full_log, net, im, fm)

    print(f"Cases scored: {len(cf)}")
    print(f"Perfect (1.0): {(cf['cf_score'] == 1.0).sum()}")
    print(f"Below 0.8:     {(cf['cf_score'] < 0.8).sum()}")
    print("\nSample low-scoring cases:")
    print(cf[cf["cf_score"] < 0.8][["case_id", "cf_score", "missing_acts", "extra_acts"]].head(6).to_string(index=False))
