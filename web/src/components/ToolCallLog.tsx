import type { ToolCallRecord } from '../lib/mcpClient'

export function ToolCallLog({ calls }: { calls: ToolCallRecord[] }) {
  return (
    <div className="card">
      <h3>MCP Tool Calls</h3>
      {calls.length === 0 ? (
        <small>Tool calls will appear here as AuraAssist uses the MCP server.</small>
      ) : (
        <ul className="toolcalls">
          {calls.map((c) => (
            <li key={c.id}>
              <code>{c.name}</code> <small>({JSON.stringify(c.args)})</small>
              {c.error ? <span className="err"> error: {c.error}</span> : null}
              <pre>{JSON.stringify(c.result, null, 2).slice(0, 600)}</pre>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
