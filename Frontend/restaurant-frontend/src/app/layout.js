import "./globals.css";
import { AuthProvider } from "./AuthContext";
import AppShell from "../components/AppShell";

export const metadata = {
  title: "Restaurant Booking App",
  description: "Book a table at your favourite restaurant in seconds.",
};

// A server component: the nav's client-side auth state lives in AppShell, so
// the root layout no longer needs "use client" or suppressHydrationWarning.
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-100 text-gray-800">
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
