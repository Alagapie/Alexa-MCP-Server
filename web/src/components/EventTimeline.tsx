import type { HomeEvent } from '../lib/types'

export function EventTimeline({ events }: { events: HomeEvent[] }) {
  return (
    <div className="card">
      <h3>Event Timeline</h3>
      {events.length === 0 ? (
        <small>No events yet. Try a routine, a scene description, or ask what changed.</small>
      ) : (
        <ul className="events">
          {events.map((e) => (
            <li key={e.id}>
              <span className="event-type">{e.event_type}</span>{' '}
              <small>
                {new Date(e.ts).toLocaleTimeString()} {e.room ? `· ${e.room}` : ''}{' '}
                {e.device_id ? `· ${e.device_id}` : ''} {e.action ? `· ${e.action}` : ''}
              </small>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
