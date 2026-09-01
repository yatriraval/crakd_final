const API_BASE = "http://127.0.0.1:8000";


async function request(path, options = {}) {

  const response =
    await fetch(`${API_BASE}${path}`, options);


  if (!response.ok) {

    const body =
      await response.text().catch(() => "");

    throw new Error(
      `${response.status} ${response.statusText}${
        body ? `: ${body}` : ""
      }`
    );
  }


  return response.json();
}


export function predictTransaction(transaction) {

  return request("/predict", {

    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify(transaction),

  });
}


export function checkHealth() {

  return request("/");
}