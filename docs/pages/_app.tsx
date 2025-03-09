import { useRouter } from "next/router";
import "../globals.css";
import "../overrides.css";
import { GeistMono } from "geist/font/mono";

export default function App({ Component, pageProps }) {
  const router = useRouter();
  return (
    <main className={GeistMono.className}>
      {" "}
      <Component {...pageProps} />
    </main>
  );
}
