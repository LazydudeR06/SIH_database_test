import React, { useState, type JSX } from "react";
import { useUser, useAuth } from "@clerk/clerk-react";
import { checkDocument } from "../api/documents";

export default function ValidateForm(): JSX.Element {
  const { user } = useUser();       // user info
  const { getToken } = useAuth();   // auth token

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!getToken) {
      setError("Authentication token unavailable");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      if (!token) {
        setError("Failed to get auth token");
        setLoading(false);
        return;
      }

      const res = await checkDocument(title, content, token);
      setResult(res);
    } catch (err: any) {
      console.error(err);
      setError("Failed to check document");
      setResult({ title, is_original: false, checked_by: "Error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h3>Check Document Authenticity</h3>
      {user && <p>Welcome, {user?.firstName || "User"}!</p>}

      <input
        type="text"
        placeholder="Title"
        value={title}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)}
        style={{ width: "100%", marginBottom: "0.5rem" }}
      />

      <textarea
        placeholder="Content"
        value={content}
        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setContent(e.target.value)}
        rows={6}
        style={{ width: "100%", marginBottom: "0.5rem" }}
      />

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Checking..." : "Check Authenticity"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: "1rem" }}>
          <p>Title: {result.title}</p>
          <p>Original: {result.is_original ? "Yes" : "No"}</p>
          <p>Checked by: {result.checked_by}</p>
        </div>
      )}
    </div>
  );
}
