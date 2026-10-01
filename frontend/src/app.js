/**
 * Meu Site - frontend (JavaScript puro, ES modules).
 * Fala com o backend Python em /api/*.
 */
const API = '/api'

const els = {
  form: document.getElementById('item-form'),
  title: document.getElementById('title'),
  description: document.getElementById('description'),
  list: document.getElementById('list'),
  empty: document.getElementById('empty'),
  stats: document.getElementById('stats'),
  error: document.getElementById('form-error'),
  refresh: document.getElementById('refresh'),
}

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Erro ${res.status}`)
  }
  return res.status === 204 ? null : res.json()
}

const escapeHtml = (value) =>
  String(value).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]))

const items = {
  list: () => api('/items'),
  create: (data) => api('/items', { method: 'POST', body: JSON.stringify(data) }),
  toggle: (item) =>
    api(`/items/${item.id}`, {
      method: 'PUT',
      body: JSON.stringify({ ...item, done: !item.done }),
    }),
  remove: (id) => api(`/items/${id}`, { method: 'DELETE' }),
  stats: () => api('/stats'),
}

function renderStats({ total, done, pending }) {
  els.stats.textContent = `${total} no total · ${done} concluídos · ${pending} pendentes`
}

function renderList(rows) {
  els.list.innerHTML = ''
  els.empty.hidden = rows.length > 0
  for (const item of rows) {
    const li = document.createElement('li')
    li.className = item.done ? 'item done' : 'item'
    li.innerHTML = `
      <label>
        <input type="checkbox" ${item.done ? 'checked' : ''} />
        <span>
          <strong>${escapeHtml(item.title)}</strong>
          ${item.description ? `<em>${escapeHtml(item.description)}</em>` : ''}
        </span>
      </label>
      <button class="ghost danger" type="button" title="Remover">×</button>
    `
    li.querySelector('input').addEventListener('change', async () => {
      await items.toggle(item)
      await refresh()
    })
    li.querySelector('button').addEventListener('click', async () => {
      await items.remove(item.id)
      await refresh()
    })
    els.list.appendChild(li)
  }
}

async function refresh() {
  const [rows, stats] = await Promise.all([items.list(), items.stats()])
  renderList(rows)
  renderStats(stats)
}

els.form.addEventListener('submit', async (event) => {
  event.preventDefault()
  els.error.hidden = true
  try {
    await items.create({
      title: els.title.value.trim(),
      description: els.description.value.trim(),
      done: false,
    })
    els.form.reset()
    els.title.focus()
    await refresh()
  } catch (error) {
    els.error.textContent = error.message
    els.error.hidden = false
  }
})

els.refresh.addEventListener('click', refresh)
refresh().catch((error) => {
  els.stats.textContent = `Não consegui falar com o backend: ${error.message}`
})
