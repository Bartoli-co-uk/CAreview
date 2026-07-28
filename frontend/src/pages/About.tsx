const GLOSSARY: { term: string; definition: string }[] = [
  { term: "Report-only", definition: "The policy's conditions are evaluated and logged, but access is not actually blocked or challenged yet." },
  { term: "Legacy authentication", definition: "Older sign-in protocols (POP, IMAP, older Office clients) that can't enforce modern controls like MFA or Conditional Access." },
  { term: "Grant control", definition: "What a policy demands before granting access — e.g. multi-factor authentication, a compliant device, or an outright block." },
  { term: "Session control", definition: "Restrictions applied during a session after access is granted — e.g. how often to re-prompt for sign-in." },
  { term: "Break-glass account", definition: "An emergency-access account deliberately excluded from Conditional Access policies so admins are never locked out." },
  { term: "Heuristic score", definition: "A rule-of-thumb score based on this project's own 10 checks — not a Microsoft Secure Score value or a compliance certification." },
];

export function About() {
  return (
    <div className="stack">
      <div className="card">
        <h3>About CAreview</h3>
        <p style={{ fontSize: 14 }}>
          CAreview is a locally-run tool that reads your Microsoft Entra ID Conditional Access policies and scores them
          against a fixed set of security checks. It runs entirely on this machine — your policies and any sign-in
          token never leave it.
        </p>
        <p style={{ fontSize: 13, color: "#667085" }}>
          The security score is heuristic: a rule-of-thumb indicator based on this project's own checks, not a
          Microsoft Secure Score value or a formal compliance certification. Use it to prioritize review, not as an
          audit result.
        </p>
      </div>

      <div className="card">
        <div className="card-header-title" style={{ marginBottom: 12 }}>
          Glossary
        </div>
        {GLOSSARY.map((entry) => (
          <div className="list-row" key={entry.term}>
            <div className="list-row-main">
              <p className="list-row-title">{entry.term}</p>
              <p className="list-row-desc">{entry.definition}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
