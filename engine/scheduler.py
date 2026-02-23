"""Scheduling Engine - CPM (Critical Path Method) implementation."""

from datetime import date, timedelta
from collections import defaultdict

from engine.date_utils import add_working_days, count_working_days


class Scheduler:
    """Schedule calculator using Critical Path Method."""

    def __init__(self, working_days=None, holidays=None):
        self.working_days = working_days
        self.holidays = holidays or set()

    def _add_days(self, start: date, days: int) -> date:
        return add_working_days(start, days, self.working_days, self.holidays)

    def schedule(self, tasks: list, dependencies: list, project_start: date) -> None:
        """Calculate schedule using forward and backward pass.

        Args:
            tasks: list of task objects (must have id, duration, start_date, end_date,
                   is_milestone, is_summary, manual_scheduling, is_critical)
            dependencies: list of dependency objects (predecessor_id, successor_id,
                          dep_type, lag)
            project_start: project start date
        """
        if not tasks:
            return

        task_map = {t.id: t for t in tasks}

        # Build adjacency lists
        preds = defaultdict(list)  # task_id -> list of (pred_task, dep_type, lag)
        succs = defaultdict(list)  # task_id -> list of (succ_task, dep_type, lag)

        for dep in dependencies:
            if dep.predecessor_id in task_map and dep.successor_id in task_map:
                pred_task = task_map[dep.predecessor_id]
                succ_task = task_map[dep.successor_id]
                preds[dep.successor_id].append((pred_task, dep.dep_type, dep.lag))
                succs[dep.predecessor_id].append((succ_task, dep.dep_type, dep.lag))

        # --- Forward Pass ---
        # Topological sort
        visited = set()
        topo_order = []

        def visit(task_id):
            if task_id in visited:
                return
            visited.add(task_id)
            for succ_task, _, _ in succs.get(task_id, []):
                visit(succ_task.id)
            topo_order.append(task_id)

        for t in tasks:
            if not t.is_summary:
                visit(t.id)

        topo_order.reverse()

        # Early start/finish
        early_start: dict[int, date] = {}
        early_finish: dict[int, date] = {}

        for tid in topo_order:
            task = task_map[tid]

            if task.manual_scheduling:
                if task.start_date:
                    early_start[tid] = task.start_date
                    if task.is_milestone:
                        early_finish[tid] = task.start_date
                    else:
                        early_finish[tid] = self._add_days(task.start_date, task.duration)
                continue

            # Calculate earliest start based on predecessors
            es = project_start
            for pred_task, dep_type, lag in preds.get(tid, []):
                lag_days = int(lag)
                if dep_type == "FS":
                    candidate = self._add_days(early_finish.get(pred_task.id, project_start), lag_days + 1)
                elif dep_type == "SS":
                    candidate = self._add_days(early_start.get(pred_task.id, project_start), lag_days)
                elif dep_type == "FF":
                    dur = max(1, task.duration)
                    ef = self._add_days(early_finish.get(pred_task.id, project_start), lag_days)
                    candidate = self._add_days(ef, -(dur - 1)) if dur > 1 else ef
                elif dep_type == "SF":
                    candidate = self._add_days(early_start.get(pred_task.id, project_start), lag_days)
                else:
                    candidate = project_start

                if candidate > es:
                    es = candidate

            # Apply constraint
            if task.constraint_type == "SNET" and task.constraint_date:
                if task.constraint_date > es:
                    es = task.constraint_date
            elif task.constraint_type == "MSO" and task.constraint_date:
                es = task.constraint_date

            early_start[tid] = es
            if task.is_milestone:
                early_finish[tid] = es
            else:
                early_finish[tid] = self._add_days(es, task.duration)

        # Apply calculated dates
        for tid in topo_order:
            task = task_map[tid]
            if not task.manual_scheduling:
                task.start_date = early_start.get(tid, project_start)
                task.end_date = early_finish.get(tid, project_start)

        # --- Backward Pass for Critical Path ---
        if not early_finish:
            return

        project_end = max(early_finish.values()) if early_finish else project_start

        late_finish: dict[int, date] = {}
        late_start: dict[int, date] = {}

        for tid in reversed(topo_order):
            task = task_map[tid]
            lf = project_end

            for succ_task, dep_type, lag in succs.get(tid, []):
                lag_days = int(lag)
                if dep_type == "FS":
                    candidate = late_start.get(succ_task.id, project_end)
                    candidate = candidate - timedelta(days=max(0, lag_days))
                elif dep_type == "SS":
                    candidate = late_start.get(succ_task.id, project_end)
                else:
                    candidate = late_finish.get(succ_task.id, project_end)

                if candidate < lf:
                    lf = candidate

            late_finish[tid] = lf
            duration_days = max(1, (early_finish.get(tid, project_start) -
                                    early_start.get(tid, project_start)).days)
            late_start[tid] = lf - timedelta(days=duration_days)

        # Mark critical tasks (zero float)
        for tid in topo_order:
            task = task_map[tid]
            es = early_start.get(tid, project_start)
            ls = late_start.get(tid, project_start)
            total_float = (ls - es).days
            task.is_critical = total_float <= 0

        # --- Summary task rollup ---
        self._rollup_summary_tasks(tasks)

    def _rollup_summary_tasks(self, tasks: list) -> None:
        """Calculate summary task dates from their children."""
        # Build parent-child map
        children_map: dict[int | None, list] = defaultdict(list)
        for task in tasks:
            if task.parent_id is not None:
                children_map[task.parent_id].append(task)

        # Process summary tasks bottom-up
        summary_tasks = [t for t in tasks if t.is_summary]
        # Sort by wbs_level descending to process deepest first
        summary_tasks.sort(key=lambda t: t.wbs_level, reverse=True)

        for summary in summary_tasks:
            children = children_map.get(summary.id, [])
            if not children:
                continue

            child_starts = [c.start_date for c in children if c.start_date]
            child_ends = [c.end_date for c in children if c.end_date]

            if child_starts:
                summary.start_date = min(child_starts)
            if child_ends:
                summary.end_date = max(child_ends)
            if summary.start_date and summary.end_date:
                summary.duration = count_working_days(
                    summary.start_date, summary.end_date,
                    self.working_days, self.holidays
                )

            # Roll up progress
            if children:
                total_dur = sum(c.duration for c in children)
                if total_dur > 0:
                    summary.progress = sum(
                        c.progress * c.duration for c in children
                    ) / total_dur

            # Summary is critical if any child is critical
            summary.is_critical = any(c.is_critical for c in children)
