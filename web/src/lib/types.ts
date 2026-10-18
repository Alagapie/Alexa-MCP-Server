export interface Device {
  id: string
  name: string
  type: string
  room: string
  state: Record<string, any>
  enabled: boolean
}

export interface HomeSnapshot {
  devices: Array<{
    id: string
    name: string
    type: string
    room: string
    state: Record<string, any>
    enabled: boolean
  }>
  summary?: string
}

export interface HomeEvent {
  id: number
  ts: string
  event_type: string
  room?: string | null
  device_id?: string | null
  action?: string | null
  details?: string | null
  confidence?: number | null
}
