import { useEffect, useRef, useState } from 'react'
import { McpClient, type ToolCallRecord } from './lib/mcpClient'
import type { HomeEvent, HomeSnapshot } from './lib/types'
import { ChatPanel, type ChatMessage } from './components/ChatPanel'
import HomeDashboard from './components/HomeDashboard'
import { EventTimeline } from './components/EventTimeline'
import { ToolCallLog } from './components/ToolCallLog'

const MCP_URL = import.meta.env.VITE_MCP_URL || 'http://127.0.0.1:8000/mcp'

export default function App() {
  const clientRef = useRef<McpClient | null>(null)
  const [connected, setConnected] = useState(false)
  const [status, setStatus] = useState('Connecting to MCP server…')
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'aura', text: 'AuraAssist is ready. Ask me about your home or start a routine.' },
  ])
  const [snapshot, setSnapshot] = useState<HomeSnapshot | null>(null)
  const [events, setEvents] = useState<HomeEvent[]>([])
  const [calls, setCalls] = useState<ToolCallRecord[]>([])
  const [pendingRoutine, setPendingRoutine] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const say = (text: string) => setMessages((m) => [...m, { role: 'aura', text }])

  const run = async <T,>(name: string, args: Record<string, unknown> = {}): Promise<T> => {
    const client = clientRef.current!
    try {
      const result = await client.callTool(name, args)
      setCalls((c) => [...c, { id: Date.now() + Math.random(), name, args, result, at: new Date().toISOString() }])
      return result as T
    } catch (e) {
      const error = e instanceof Error ? e.message : String(e)
      setCalls((c) => [...c, { id: Date.now() + Math.random(), name, args, error, at: new Date().toISOString() }])
      throw e
    }
  }

  const refresh = async () => {
    const snap = await run<HomeSnapshot>('get_home_snapshot')
    setSnapshot(snap)
    const ev = await run<{ events: HomeEvent[] }>('get_recent_events', { limit: 50 })
    setEvents(ev.events ?? [])
  }

  useEffect(() => {
    const client = new McpClient(MCP_URL)
    clientRef.current = client
    ;(async () => {
      try {
        await client.initialize()
        setConnected(true)
        setStatus(`Connected · ${client.serverInfo.name ?? 'AuraAssist'} · MCP ${client.protocolVersion}`)
        await refresh()
      } catch (e) {
        setStatus(`Could not connect: ${e instanceof Error ? e.message : String(e)}`)
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSend = async (text: string) => {
    if (busy) return
    setMessages((m) => [...m, { role: 'user', text }])
    setBusy(true)
    const lower = text.toLowerCase()
    try {
      if (pendingRoutine && /^(yes|yeah|yep|ok|okay|sure|confirm|do it|go ahead|please do)/.test(lower)) {
        const res = await run<any>('run_routine', { routine_name: pendingRoutine, confirm: true })
        setPendingRoutine(null)
        say(res?.summary ? `${res.summary}` : 'Done.')
        await refresh()
        return
      }

      if (/(bed|sleep|good night|night routine)/.test(lower)) return await planRoutine('bedtime')
      if (/(leav|away|going out|out for|head out)/.test(lower)) return await planRoutine('leaving_home')
      if (/morning/.test(lower)) return await planRoutine('morning')

      if (/(counter|what is in|what's in|see|look|front of me|describe|room|hazard)/.test(lower)) {
        const scene = await run<any>('describe_scene', { camera_id: 'kitchen' })
        let reply = scene?.summary ?? 'I could not describe the scene.'
        if (scene?.hazards?.length) reply += ` Note: ${scene.hazards.map((h: any) => h.label).join(', ')}.`
        say(reply)
        await refresh()
        return
      }

      if (/(where|find|last seen).*(key|wallet|phone|glass|bag|remote)|find /.test(lower)) {
        const obj = lower.includes('key')
          ? 'keys'
          : lower.includes('wallet')
            ? 'wallet'
            : lower.includes('phone')
              ? 'phone'
              : lower.includes('glass')
                ? 'glasses'
                : 'keys'
        const res = await run<any>('find_object', { object_name: obj })
        if (res?.count > 0) {
          say(`Your ${obj} were last seen in the ${res.results[0].room} at ${new Date(res.results[0].ts).toLocaleTimeString()}.`)
        } else {
          say(`I have not seen your ${obj} recently. Try another room snapshot.`)
        }
        await refresh()
        return
      }

      if (/(changed|briefing|happened|today|summary|unusual)/.test(lower)) {
        const res = await run<any>('generate_daily_briefing', { audience: 'user' })
        say(res?.briefing ?? 'No briefing available.')
        return
      }

      // Default: report home state
      const snap = await run<HomeSnapshot>('get_home_snapshot')
      setSnapshot(snap)
      const lights = (snap.devices ?? []).filter((d) => d.type === 'light' && d.state.on).map((d) => d.name)
      say(
        `Home status: ${snap.summary ?? ''}.` +
          (lower.includes('lock')
            ? ` Locks — front: ${snapshot?.devices.find((d) => d.id === 'front_door')?.state.locked ? 'locked' : 'unlocked'}, back: ${snapshot?.devices.find((d) => d.id === 'back_door')?.state.locked ? 'locked' : 'unlocked'}.`
            : '') +
          (lights.length ? ` Lights on: ${lights.join(', ')}.` : ''),
      )
    } catch (e) {
      say(`Sorry, something went wrong: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setBusy(false)
    }
  }

  const planRoutine = async (name: string) => {
    const res = await run<any>('run_routine', { routine_name: name, confirm: false })
    if (res?.status === 'needs_confirmation') {
      setPendingRoutine(name)
      say(res.message ?? 'I have a plan. Shall I proceed?')
    } else {
      say('Routine finished.')
      await refresh()
    }
  }

  return (
    <div className="app">
      <header>
        <h1>AuraAssist</h1>
        <p>
          Context-aware, hands-free home companion · <small>{status}</small>
        </p>
      </header>
      <div className="grid">
        <ChatPanel messages={messages} onSend={handleSend} disabled={!connected || busy} />
        <HomeDashboard snapshot={snapshot} />
        <EventTimeline events={events} />
        <ToolCallLog calls={calls} />
      </div>
    </div>
  )
}
