async function requestJSON(path, options) {
  const r = await fetch(path, options)
  if (!r.ok) {
    const text = await r.text()
    let detail = text
    try {
      const body = JSON.parse(text)
      if (body && body.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      // keep raw text
    }
    throw new Error(detail)
  }
  return r.json()
}

export function getJSON(path) {
  return requestJSON(path)
}

export function postJSON(path, body) {
  return requestJSON(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function putJSON(path, body) {
  return requestJSON(path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
