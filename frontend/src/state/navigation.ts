import { useEffect, useState } from "react";

export const PAGES = [
  "overview",
  "recommendations",
  "policies",
  "explorer",
  "insights",
  "reports",
  "audit-log",
  "settings",
  "about",
] as const;

export type Page = (typeof PAGES)[number];

const DEFAULT_PAGE: Page = "overview";

function readHash(): Page {
  const raw = window.location.hash.replace(/^#\/?/, "");
  return (PAGES as readonly string[]).includes(raw) ? (raw as Page) : DEFAULT_PAGE;
}

// Hash-based navigation: server.py serves one static index.html/index.js with
// no server-side route handling, so the fragment (which browsers never send
// to the server) is the only routing mechanism that needs zero backend
// changes, while still getting back-button support and a bookmarkable URL.
export function useHashRoute(): [Page, (page: Page) => void] {
  const [page, setPage] = useState<Page>(readHash);

  useEffect(() => {
    const onHashChange = () => setPage(readHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const navigate = (next: Page) => {
    window.location.hash = `/${next}`;
    setPage(next);
  };

  return [page, navigate];
}
