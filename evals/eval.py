# per run
# - end reason
# - #messages
# - #tool calls
# - avg #tool calls / #messages
# - cost
# - duration
# - context size over time
# - flags found
# - flags found graphed on the context size over time graph
# - time to first flag
# - duration after last flag before end

import datetime
import json
import pathlib
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from_iso = datetime.datetime.fromisoformat

print_output = False
show_graphs = False

_print = print


def print(*args, **kwargs):
    if print_output:
        _print(*args, **kwargs)


def evaluate_datasets(dataset_path: pathlib.Path, possible_flags: list[str]) -> dict:
    result = {
        "cost": 0,
        "#flags": 0,
        "flags": {flag: 0 for flag in possible_flags},
        "datasets": {},
    }

    if not dataset_path.is_dir():
        raise ValueError(f"Dataset path {dataset_path} is not a directory")
    for dataset in dataset_path.glob("**/*.sqlite3"):
        if dataset.is_file():
            dataset_result = evaluate_dataset(dataset, possible_flags)
            result["datasets"][dataset.as_posix()] = dataset_result
            result["cost"] += dataset_result["cost"]
            result["#flags"] += dataset_result["#flags"]
            for flag, count in dataset_result["flags"].items():
                result["flags"][flag] += count

    return result


def evaluate_dataset(path: pathlib.Path, possible_flags: list[str]) -> dict:
    result = {
        "cost": 0,
        "#flags": 0,
        "flags": {flag: 0 for flag in possible_flags},
        "runs": {},
    }

    db = sqlite3.connect(path.as_posix())
    cur = db.cursor()
    cur.execute("SELECT id, state, started_at, stopped_at FROM runs")
    run_ids = cur.fetchall()

    for run_id, state, started_at, stopped_at in run_ids:
        print("# RUN ", run_id, state)
        started_at, stopped_at = from_iso(started_at), from_iso(stopped_at)
        print(f"{started_at} - {stopped_at} ({stopped_at - started_at})")
        run_result = evaluate_run(path, db, run_id)
        result["runs"][run_id] = run_result
        result["cost"] += run_result["cost"]
        result["#flags"] += run_result["#flags"]
        for flag in run_result["flags"]:
            flag_text = flag["flag"]
            if flag_text not in result["flags"]:
                raise ValueError(f"Flag {flag_text} not found in possible flags")
            result["flags"][flag_text] += 1

    result["avg_flags"] = result["#flags"] / len(result["runs"])
    print(json.dumps(result, indent=4))
    return result


def evaluate_run(path: pathlib.Path, db: sqlite3.Connection, run_id: int):
    result = dict()

    messages = pd.read_sql_query(
        f"""
        SELECT
            id,
            role,
            content,
            reasoning,
            duration,
            tokens_query,
            tokens_response,
            tokens_reasoning,
            usage_details,
            cost
        FROM
            messages
        WHERE
            run_id = {run_id}
    """,
        db,
    )
    message_ids = messages["id"].tolist()
    missing_message_ids = set(message_ids) - set(range(0, max(message_ids) + 1))
    if missing_message_ids:
        print("missing", missing_message_ids)
    result["missing_ids"] = list(missing_message_ids)

    assistant_messages = messages.loc[messages["usage_details"].str.len() > 0]
    print("Messages: ", len(messages), "generated", len(assistant_messages))
    result["#messages"] = len(messages)
    result["#generated_messages"] = len(assistant_messages)
    print("Cost: ", messages["cost"].sum())
    result["cost"] = messages["cost"].sum()

    tool_calls = pd.read_sql_query(
        f"""
        SELECT
            message_id,
            id,
            function_name,
            arguments,
            state,
            result_text,
            duration
        FROM
            tool_calls
        WHERE
            run_id = {run_id}
        """,
        db,
    )

    print(
        f"Tool Calls: {len(tool_calls)} ({len(tool_calls) / len(assistant_messages)}/message)"
    )
    result["#tool_calls"] = len(tool_calls)
    result["#tool_calls_per_message"] = len(tool_calls) / len(assistant_messages)

    tool_call_groups = tool_calls.groupby(["function_name"])
    print(
        tool_call_groups.agg(
            n_calls=("id", "size"),
            duration=("duration", "sum"),
            avg_duration=("duration", "mean"),
        )
    )
    result["tool_call_groups"] = dict()
    for name, group in tool_call_groups:
        result["tool_call_groups"][name[0]] = {
            "n_calls": len(group),
            "duration": group["duration"].sum(),
            "avg_duration": group["duration"].mean(),
        }

    print(
        "Serialized Duration",
        (messages["duration"].sum() + tool_calls["duration"].sum()) / 60,
        "minutes",
    )
    result["serialized_duration"] = (
        messages["duration"].sum() + tool_calls["duration"].sum()
    ) / 60

    flag_submissions = tool_calls.loc[
        (tool_calls["function_name"] == "SubmitFlag")
        & (tool_calls["result_text"].str.contains("Flag submitted \\("))
    ]
    print(
        "Flags: ",
        len(flag_submissions),
    )
    result["#flags"] = len(flag_submissions)
    result["flags"] = list()
    for message_id, flag in flag_submissions[
        ["message_id", "arguments"]
    ].values.tolist():
        flag = json.loads(flag)["flag"]
        result["flags"].append({"message_id": message_id, "flag": flag})
        print(message_id, flag)
    print(max(message_ids))

    print(messages.keys())
    if show_graphs:
        # Plot message context size (tokens_query+tokens_response+tokens_reasoning) over message_id
        plt.figure(figsize=(10, 6))
        plt.plot(
            assistant_messages["id"],
            assistant_messages["tokens_query"],
            color="skyblue",
        )
        plt.title(f"{path.as_posix()} Run {run_id}")
        plt.xlabel("Message ID")
        plt.ylabel("Context Size")
        plt.grid(True)

        ax = plt.gca()
        # add in the flags submitted as vertical lines at the message_id of the flag submission with the flag name being displayed next to the line
        for flag in result["flags"]:
            plt.axvline(flag["message_id"], color="red", linestyle="--")

            plt.annotate(
                flag["flag"],
                xy=(flag["message_id"], 1),
                xycoords=("data", "axes fraction"),  # x in data, y in axes [0..1]
                xytext=(-8, -2),  # 6 points left
                textcoords="offset points",
                rotation=90,
                va="center",
                ha="right",
                rotation_mode="anchor",
                color="crimson",
                clip_on=True,
                # optional: cover the line under the text
                bbox=dict(facecolor="white", edgecolor="none", pad=1),
            )

        plt.show()

    return result


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Evaluate dataset")
    parser.add_argument("dataset", help="Path to dataset (directory or sqlite3)")
    parser.add_argument(
        "--flags", help="Flags that could have been found (comma separated)"
    )
    parser.add_argument("--print", action="store_true", help="Print results")
    parser.add_argument("--graphs", action="store_true", help="Show graphs")
    args = parser.parse_args()

    print_output = args.print
    show_graphs = args.graphs

    dataset_path = pathlib.Path(args.dataset)
    if not dataset_path.exists():
        print(f"Dataset not found: {args.dataset}")
        sys.exit(1)

    flags = args.flags.split(",") if args.flags else []

    result = {}
    if dataset_path.is_dir():
        result = evaluate_datasets(dataset_path, flags)
    else:
        result = evaluate_dataset(dataset_path, flags)

    _print(json.dumps(result, indent=4))
