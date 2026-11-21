const form = document.querySelector("#add-form");
const notice = document.querySelector("#notice");

function showNotice(message, isError = false) {
  notice.textContent = message;
  notice.style.color = isError ? "var(--red)" : "var(--green)";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = form.querySelector("button");
  button.disabled = true;
  const data = Object.fromEntries(new FormData(form));

  try {
    const response = await fetch("/api/endpoints", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not add endpoint.");
    window.location.reload();
  } catch (error) {
    showNotice(error.message, true);
    button.disabled = false;
  }
});

document.querySelector("#endpoint-list").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const card = button.closest(".endpoint-card");
  const id = card.dataset.id;
  const action = button.dataset.action;

  if (action === "check") {
    button.disabled = true;
    button.textContent = "Checking…";
    try {
      const response = await fetch(`/api/endpoints/${id}/check`, {method: "POST"});
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Check failed.");
      window.location.reload();
    } catch (error) {
      button.disabled = false;
      button.textContent = "Check now ↗";
      showNotice(error.message, true);
    }
  }

  if (action === "delete") {
    if (!window.confirm("Delete this endpoint and its check history?")) return;
    const response = await fetch(`/api/endpoints/${id}`, {method: "DELETE"});
    if (response.ok) window.location.reload();
    else showNotice("Could not delete endpoint.", true);
  }

  if (action === "history") {
    const box = card.querySelector(".history");
    if (!box.hidden) {
      box.hidden = true;
      return;
    }

    box.hidden = false;
    box.textContent = "Loading history…";
    try {
      const response = await fetch(`/api/endpoints/${id}/history`);
      const rows = await response.json();
      box.replaceChildren();

      if (!rows.length) {
        box.textContent = "No checks recorded yet.";
        return;
      }

      rows.forEach((row) => {
        const line = document.createElement("div");
        line.className = "history-row";
        const date = document.createElement("span");
        date.textContent = new Date(row.checked_at).toLocaleString();
        const result = document.createElement("strong");
        result.textContent = row.is_up
          ? `UP · ${row.status_code} · ${row.response_ms} ms`
          : `DOWN · ${row.error || "Unavailable"}`;
        line.append(date, result);
        box.append(line);
      });
    } catch {
      box.textContent = "Unable to load history.";
    }
  }
});
