import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton } from "@clerk/clerk-react";

export default function Header() {
  return (
    <header style={{ display: "flex", justifyContent: "flex-end", gap: "1rem", padding: "1rem", background: "#f4f4f4" }}>
      <SignedOut>
        <SignInButton />
        <SignUpButton>
          <button>Sign Up</button>
        </SignUpButton>
      </SignedOut>
      <SignedIn>
        <UserButton />
      </SignedIn>
    </header>
  );
}
