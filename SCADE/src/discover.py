import pickle
import os
import pm4py

MODEL_PATH = "models/normal_model.pkl"


def discover_normal_model(train_log):
    """
    Inductive Miner with a small noise threshold so minor variations in
    normal cases don't bloat the model with spurious branches.
    Returns (net, initial_marking, final_marking).
    """
    net, im, fm = pm4py.discover_petri_net_inductive(
        train_log,
        noise_threshold=0.2,
    )
    return net, im, fm


def save_model(net, im, fm, path=MODEL_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump((net, im, fm), f)
    print(f"Model saved → {path}")


def load_model(path=MODEL_PATH):
    with open(path, "rb") as f:
        net, im, fm = pickle.load(f)
    return net, im, fm


def model_summary(net):
    places     = len(net.places)
    transitions = len(net.transitions)
    arcs       = len(net.arcs)
    visible    = [t for t in net.transitions if t.label is not None]
    print(f"Petri net — places: {places}, transitions: {transitions} "
          f"({len(visible)} visible), arcs: {arcs}")


if __name__ == "__main__":
    from src.generate_data import generate_log
    from src.preprocess import load_and_format, split_log, to_event_log

    df        = load_and_format("data/supply_chain_log.csv")
    train_df, _ = split_log(df)
    train_log = to_event_log(train_df)

    print("Running Inductive Miner on training log...")
    net, im, fm = discover_normal_model(train_log)
    model_summary(net)
    save_model(net, im, fm)
