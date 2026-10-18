import type { HomeSnapshot } from '../lib/types'

export default function HomeDashboard({ snapshot }: { snapshot: HomeSnapshot | null }) {
  if (!snapshot) return <div className="card">Loading home state…</div>
  return (
    <div className="card">
      <h3>Home State</h3>
      <p>
        <small>{snapshot.summary}</small>
      </p>
      <div className="devices">
        {snapshot.devices.map((d) => (
          <div key={d.id} className="device">
            <strong>{d.name}</strong>
            <small> · {d.room}</small>
            <pre>{JSON.stringify(d.state, null, 0)}</pre>
          </div>
        ))}
      </div>
    </div>
  )
}
