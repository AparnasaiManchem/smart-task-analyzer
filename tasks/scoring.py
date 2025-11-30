from datetime import datetime, date
from collections import defaultdict

DEFAULT_WEIGHTS = {
    "urgency": 0.35,
    "importance": 0.35,
    "effort": 0.15,
    "dependency": 0.15
}

def parse_date(d):
    if not d:
        return None
    if isinstance(d, date):
        return d
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except:
        return None

def detect_circular_dependencies(tasks):
    graph = defaultdict(list)
    ids = [t['id'] for t in tasks]

    for t in tasks:
        tid = t['id']
        for dep in t['dependencies']:
            graph[tid].append(dep)

    visited = set()
    stack = set()
    cycles = set()

    def dfs(node):
        if node in stack:
            cycles.add(node)
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for neigh in graph[node]:
            dfs(neigh)
        stack.remove(node)

    for t in ids:
        dfs(t)

    return cycles

def normalize(val, min_val, max_val):
    if min_val == max_val:
        return 0.5
    return (val - min_val) / (max_val - max_val)

def calculate_scores(task_list, weights=None):
    if weights is None:
        weights = DEFAULT_WEIGHTS

    today = date.today()

    tasks = []
    for idx, t in enumerate(task_list):
        task = dict(t)
        task.setdefault('id', idx)
        task['due_date_obj'] = parse_date(task.get('due_date'))
        task['estimated_hours'] = int(task.get('estimated_hours', 0))
        task['importance'] = int(task.get('importance', 5))
        task['dependencies'] = task.get('dependencies', [])
        tasks.append(task)

    cycles = detect_circular_dependencies(tasks)

    urgency_values = []
    for t in tasks:
        d = t['due_date_obj']
        if d is None:
            urgency_values.append(7)  
        else:
            urgency_values.append((d - today).days)

    importance_values = [t['importance'] for t in tasks]
    effort_values = [t['estimated_hours'] for t in tasks]

    dependency_counts = defaultdict(int)
    for t in tasks:
        for dep in t['dependencies']:
            dependency_counts[dep] += 1
    dependency_values = [dependency_counts[t['id']] for t in tasks]

    scored = []
    for i, t in enumerate(tasks):
        explanation = []
        flags = {}

        days = urgency_values[i]
        urgency_score = 0
        if days < 0:
            urgency_score = 1
            explanation.append(f"Overdue by {-days} days.")
        elif days <= 3:
            urgency_score = 0.8
            explanation.append(f"Due in {days} days.")
        else:
            urgency_score = 0.3
            explanation.append(f"Due in {days} days.")

        importance_score = t['importance'] / 10
        explanation.append(f"Importance {t['importance']}/10.")

        effort = effort_values[i]
        if effort <= 1:
            effort_score = 1
            explanation.append("Quick win task.")
        else:
            effort_score = max(0, 1 - effort / max(effort_values))
            explanation.append(f"Estimated {effort} hours.")

        dep_count = dependency_values[i]
        dependency_score = dep_count / (max(dependency_values) or 1)
        if dep_count > 0:
            explanation.append(f"Blocks {dep_count} other tasks.")

        if t['id'] in cycles:
            flags['circular_dependency'] = True
            explanation.insert(0, "Circular dependency detected.")

        final_score = (
            weights['urgency'] * urgency_score +
            weights['importance'] * importance_score +
            weights['effort'] * effort_score +
            weights['dependency'] * dependency_score
        )

        scored.append({
            "id": t['id'],
            "title": t.get("title", ""),
            "due_date": t.get("due_date"),
            "estimated_hours": t['estimated_hours'],
            "importance": t['importance'],
            "dependencies": t['dependencies'],
            "score": round(final_score * 100, 2),
            "explanation": " ".join(explanation),
            "flags": flags
        })

    return sorted(scored, key=lambda x: x['score'], reverse=True)
