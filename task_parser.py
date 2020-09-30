from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Dict

import yaml
try:
    from yaml import CFullLoader as FullLoader
except ImportError:
    from yaml import FullLoader


@dataclass
class Task:
    """
    A simple dataclass containing the name of the task and the list of dependencies
    Dependencies will default to an empty list
    Overrides __hash__ and __eq__ functions to be used directly in sets, dictionaries
    and comparisons
    """
    name: str
    dependencies: List[Task] = field(default_factory=list)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


def parse_tasks(task_file: Path) -> Set[Task]:
    """
    Creates a set of Tasks from task_file. Yaml file is parsed using FullLoader
    (C implementation if available on the platform) to avoid arbitrary code execution
    Will raise exceptions if file can't be parsed or has an invalid format

    :param task_file: Path of the file containing the tasks encoded as yaml
    :return: Set of all the tasks parsed from the task_file
    :raises TypeError, KeyError, ValueError, YAMLError, OSError
    """
    with task_file.open() as file:
        parsed_file = yaml.load(file, Loader=FullLoader)

    tasks_dict = _cook_task_dict(parsed_file)

    task_set = set()
    for task in tasks_dict.values():
        resolved_dependencies = []
        for dep in task.dependencies:
            resolved_dependencies.append(tasks_dict[dep])
        task.dependencies = resolved_dependencies
        task_set.add(task)

    return task_set


def _cook_task_dict(raw_dict: Dict) -> Dict[str, Task]:
    """
    Creates a dictionary of Tasks with names as keys from the raw yaml object
    Will raise exceptions if essential keys are not found or if data is of the wrong type

    :param raw_dict: The parsed yaml file as a dictionary of raw data
    :return: Dictionary
    :raises TypeError, KeyError, ValueError
    """
    task_list = raw_dict["tasks"]

    if not isinstance(task_list, list):
        raise TypeError(f"Expected tasks list type {type([])}, got : {type(task_list)}")

    tasks_dict = {}
    for task in task_list:
        if not isinstance(task, dict):
            raise TypeError(f"Expected task type {type({})}, got: {type(task)}")
        name = task["name"]
        if not isinstance(name, str):
            raise TypeError(f"Expected name type {type('')}, got: {type(name)}")

        if name in tasks_dict:
            raise ValueError(f"Duplicate task '{name}' found")

        try:
            dependencies = task["dependencies"]
            if not isinstance(dependencies, list):
                raise TypeError(f"Expected dependencies type {type([])} "
                                f"for task '{name}', got: {type(dependencies)}")
        except KeyError:
            pass

        tasks_dict[name] = Task(**task)
    return tasks_dict
