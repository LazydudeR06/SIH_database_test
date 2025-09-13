import { useUser } from "@clerk/clerk-react";
import type { JSX } from "react";

export default function Dashboard(): JSX.Element {
  const { user } = useUser();

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Welcome, {user?.firstName || "User"}!</h2>
      <p>Your role: {user?.publicMetadata?.role?.toString() || "Not assigned"}</p>

    </div>
  );
}
