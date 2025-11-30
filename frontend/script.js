async function analyzeTasks() {
  const inputEl = document.getElementById('taskInput');
  const messageEl = document.getElementById('message');
  const resultsEl = document.getElementById('results');

  messageEl.textContent = '';
  resultsEl.innerHTML = '';

  if (!inputEl) {
    messageEl.textContent = 'Error: Input box not found';
    return;
  }

  let raw = inputEl.value.trim();
  if (!raw) {
    messageEl.textContent = 'Please paste JSON tasks';
    return;
  }

  let tasks;
  try {
    tasks = JSON.parse(raw);
    if (!Array.isArray(tasks)) throw new Error('Not an array');
  } catch (err) {
    messageEl.textContent = 'Invalid JSON: ' + err.message;
    return;
  }

  const strategy = document.getElementById('strategy')?.value || 'smart';
  let weights = null;
  if (strategy === 'fast') {
    weights = { urgency: 0.2, importance: 0.2, effort: 0.5, dependency: 0.1 };
  } else if (strategy === 'impact') {
    weights = { urgency: 0.2, importance: 0.6, effort: 0.1, dependency: 0.1 };
  } else if (strategy === 'deadline') {
    weights = { urgency: 0.7, importance: 0.15, effort: 0.05, dependency: 0.1 };
  }

  try {
    const res = await fetch('http://127.0.0.1:8001/api/tasks/analyze/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tasks, weights }),
    });

    if (!res.ok) {
      const text = await res.text();
      messageEl.textContent = 'Server error: ' + text;
      return;
    }

    const sorted = await res.json();
    displayResults(sorted);
  } catch (err) {
    messageEl.textContent = 'Network error: ' + err.message;
  }
}

function displayResults(tasks) {
  const container = document.getElementById('results');
  container.innerHTML = '';

  tasks.forEach(t => {
    const card = document.createElement('div');
    card.classList.add('card');

    let pr = 'priority-low';
    if (t.score >= 70) pr = 'priority-high';
    else if (t.score >= 40) pr = 'priority-med';
    card.classList.add(pr);

    card.innerHTML = `
      <strong>${t.title || '(Untitled)'} — ${t.score}</strong>
      <div>Due: ${t.due_date} | Est: ${t.estimated_hours} | Importance: ${t.importance}</div>
      <div class="explanation">${t.explanation || ''}</div>
    `;

    container.appendChild(card);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('analyzeBtn')?.addEventListener('click', analyzeTasks);
});
