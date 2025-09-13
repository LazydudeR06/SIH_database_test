import ReactDOM from "react-dom/client";
import App from "./App";
import { ClerkProvider } from "@clerk/clerk-react";

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!clerkPubKey) {
  throw new Error("Missing Clerk Publishable Key! Check .env file.");
}

const root = ReactDOM.createRoot(document.getElementById("root")!);

root.render(
  <ClerkProvider publishableKey={clerkPubKey}>
    <App />
  </ClerkProvider>
);
