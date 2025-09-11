import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import SignInPage from "./SignInPage";
import SignUpPage from "./SignUpPage";
import Dashboard from "./components/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <main style={{ padding: "2rem" }}>
        <Routes>
          <Route path="/" element={<h1>Welcome to Academic Authenticity Validator</h1>} />
          <Route path="/sign-in/*" element={<SignInPage />} />
          <Route path="/sign-up/*" element={<SignUpPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
