export async function checkDocument(title: string, content: string, token: string) {
  const res = await fetch("http://127.0.0.1:8000/check-authenticity", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ title, content }),
  });

  if (!res.ok) throw new Error("Failed to check document");
  return res.json();
}
