import { useHealth } from "./api/queries";

function HealthStatus() {
  const health = useHealth();
  if (health.isPending) return <p>Checking the API...</p>;
  if (health.isError) return <p role="alert">API unreachable: {health.error.message}</p>;
  const { cala_mode, llm_mode, demo_mode } = health.data;
  return (
    <p>
      API ok · Cala {cala_mode} · LLM {llm_mode}
      {demo_mode ? " · demo mode" : ""}
    </p>
  );
}

export default function App() {
  return (
    <main className="app">
      <header>
        <h1>Grabbit</h1>
        <HealthStatus />
      </header>
      <div className="panels">
        <section aria-label="Chat">
          <h2>Chat</h2>
          <p>Placeholder (#27).</p>
        </section>
        <section aria-label="Report">
          <h2>Report</h2>
          <p>Placeholder (#27).</p>
        </section>
      </div>
    </main>
  );
}
