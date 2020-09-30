from __future__ import annotations

from typing import List, Set, Iterable

from task_parser import Task


def sequence_tasks(task_set) -> List[List[Task]]:
    """
    Creates an optimized sequence of tasks to be launched in parallel.
    Each item in the returned list represents an execution step containing
    the set of tasks that can be launched in parallel. Raises a ValueError
    if a circular dependency is found

    :param task_set: Set of all tasks to be executed
    :return: Sequence of execution of the tasks in task_set
    :raises ValueError
    """

    # Check for circular dependencies
    # We can't sequence if a circular dependency is found
    if is_circular(task_set):
        raise ValueError("Circular dependencies found")

    # Remaining tasks to sequence
    remaining = task_set.copy()
    # Tasks already sequenced
    sequenced = set()

    sequence = []

    while remaining:
        ready = []

        for task in remaining.copy():
            # A task can be executed iff all of its depencies are already sequenced
            if all([dep in sequenced for dep in task.dependencies]):
                ready.append(task)

        # Remove tasks being launched from remaining
        remaining.difference_update(ready)
        # Add tasks being launched to sequenced tasks
        sequenced.update(ready)
        sequence.append(ready)

    return sequence


def is_circular(task_set: Iterable[Task]) -> bool:
    """
    Check for circular dependencies in a given set of Tasks using a recursive DFS algorithm

    :param task_set: Iterable over tasks
    :return: True if a circular dependency is found, False otherwise
    """
    checked = set()
    current_tree = set()

    for task in task_set:
        if task not in checked:
            if _recurse_circular_check(task, checked, current_tree):
                return True
    return False


def _recurse_circular_check(task: Task, checked: Set[Task], current_tree: Set[Task]) -> bool:
    """
    Check if any of the dependencies of the current task leads back to any
    of the connected nodes currently being checked. If any of the dependencies
    have not been checked previously, recursively check that task for cycles as well.

    :param task: Task used a the current point to check
    :param checked: Nodes that have previously been checked
    :param current_tree: Set of currently connected nodes
    :return: True if any cycle is found, False otherwise
    """
    checked.add(task)
    current_tree.add(task)
    for dep in task.dependencies:
        if dep not in checked:
            if _recurse_circular_check(dep, checked, current_tree):
                return True
        elif dep in current_tree:
            return True

    current_tree.remove(task)
    return False
