"""WBS (Work Breakdown Structure) Manager."""


class WBSManager:
    """Manages WBS hierarchy: indent, outdent, numbering."""

    @staticmethod
    def recalculate_wbs(tasks: list) -> None:
        """Recalculate WBS numbers for all tasks in order.

        Tasks must be sorted by sort_order.
        Each task has wbs_level (0 = top level).
        """
        counters: list[int] = []

        for task in tasks:
            level = task.wbs_level

            # Ensure counters list is long enough
            while len(counters) <= level:
                counters.append(0)

            # Increment counter at this level
            counters[level] += 1

            # Reset deeper counters
            for i in range(level + 1, len(counters)):
                counters[i] = 0

            # Build WBS string
            task.wbs = ".".join(str(counters[i]) for i in range(level + 1))

    @staticmethod
    def update_summary_flags(tasks: list) -> None:
        """Mark tasks as summary if they have children (next task has higher level)."""
        for i, task in enumerate(tasks):
            if i + 1 < len(tasks) and tasks[i + 1].wbs_level > task.wbs_level:
                task.is_summary = True
            else:
                task.is_summary = False

    @staticmethod
    def update_parent_ids(tasks: list) -> None:
        """Set parent_id based on WBS levels."""
        parent_stack: list[int | None] = [None]  # stack of parent task ids

        for task in tasks:
            level = task.wbs_level

            # Adjust stack to current level
            while len(parent_stack) > level + 1:
                parent_stack.pop()
            while len(parent_stack) <= level:
                parent_stack.append(parent_stack[-1])

            task.parent_id = parent_stack[level] if level > 0 else None
            # Update stack for potential children: this task becomes the parent at the next level
            if len(parent_stack) <= level + 1:
                parent_stack.append(task.id)
            else:
                parent_stack[level + 1] = task.id

    @staticmethod
    def indent_task(tasks: list, task_index: int) -> bool:
        """Indent a task (make it a child of the previous task).

        Returns True if successful.
        """
        if task_index <= 0:
            return False

        task = tasks[task_index]
        prev_task = tasks[task_index - 1]

        # Can only indent one level deeper than previous task
        if task.wbs_level > prev_task.wbs_level:
            return False

        task.wbs_level += 1

        # Also indent any children below
        for i in range(task_index + 1, len(tasks)):
            if tasks[i].wbs_level <= tasks[task_index].wbs_level - 1:
                break
            tasks[i].wbs_level += 1

        return True

    @staticmethod
    def outdent_task(tasks: list, task_index: int) -> bool:
        """Outdent a task (move it up one level).

        Returns True if successful.
        """
        task = tasks[task_index]
        if task.wbs_level <= 0:
            return False

        old_level = task.wbs_level
        task.wbs_level -= 1

        # Also outdent any children below
        for i in range(task_index + 1, len(tasks)):
            if tasks[i].wbs_level <= old_level:
                break
            tasks[i].wbs_level -= 1

        return True

    @staticmethod
    def recalculate_all(tasks: list) -> None:
        """Full recalculation of WBS numbers, parent IDs, and summary flags."""
        WBSManager.recalculate_wbs(tasks)
        WBSManager.update_summary_flags(tasks)
        WBSManager.update_parent_ids(tasks)
