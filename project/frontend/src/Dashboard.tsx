import { type JSX } from "react";
import { useUser } from "@clerk/clerk-react";

export default function Dashboard(): JSX.Element {
  const { user } = useUser();

  // safely extract role from Clerk's publicMetadata
  const role = (user?.publicMetadata as { role?: string })?.role || "Not set";

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Welcome, {user?.firstName || "User"}!</h2>
      <p>Your role: {role}</p>
    </div>
  );
}
