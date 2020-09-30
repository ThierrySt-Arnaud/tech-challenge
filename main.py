import sys
import argparse
from pathlib import Path

from yaml import YAMLError

from task_parser import parse_tasks
from task_sequencer import sequence_tasks


def setup_arg_parser() -> argparse.ArgumentParser:
    """
    Create an argument parser to get the path of the file to parse
    If a path is not found, looks in the current directory for 'tasks.yml'

    :return: The generated argument parser
    """
    parser = argparse.ArgumentParser(description="Parse and optimize sequence of tasks from yaml file")
    parser.add_argument("path", nargs='?', default="tasks.yml",
                        help="Path of the task file (defaults to './tasks.yml'")
    return parser


if __name__ == "__main__":
    # Get the path of the file from arguments
    arg_parser = setup_arg_parser()
    args = arg_parser.parse_args()
    task_file = Path(args.path)

    # Attempt to create a set of tasks from the specified file
    try:
        task_set = parse_tasks(task_file)
    except OSError as e:
        print(f"Unable to open file '{task_file}': {e}", file=sys.stderr)
        sys.exit(1)
    except (TypeError, ValueError, YAMLError) as e:
        print(f"Invalid file format: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Invalid file format: {e} not found", file=sys.stderr)
        sys.exit(1)

    # Attempt to create an optimized order of execution for the tasks
    try:
        sequence = sequence_tasks(task_set)
    except ValueError as e:
        print(f"Unable to sequence tasks: {e}", file=sys.stderr)
        sys.exit(1)

    # Print the order of execution
    for parallel_tasks in sequence:
        print([task.name for task in parallel_tasks])
