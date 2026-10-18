// Minimal MCP client for the Streamable HTTP transport (MCP 2025-11-25+).
// Used by the AuraAssist web simulator so it acts as a real MCP client.

export interface ToolDef {
  name: string
  description?: string
  inputSchema?: Record<string, unknown>
}

export interface ToolCallRecord {
  id: number
  name: string
  args: Record<string, unknown>
  result?: unknown
  error?: string
  at: string
}

type JsonRpcResponse = {
  jsonrpc: string
  id: number
  result?: any
  error?: { code: number; message: string }
}

export class McpClient {
  private url: string
  private sessionId: string | null = null
  private nextId = 1
  protocolVersion = ''
  serverInfo: { name?: string; version?: string } = {}
  onToolCall?: (record: ToolCallRecord) => void

  constructor(url: string) {
    this.url = url
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json, text/event-stream',
    }
    if (this.sessionId) h['Mcp-Session-Id'] = this.sessionId
    return h
  }

  private async post(body: unknown, notification = false): Promise<JsonRpcResponse | null> {
    const res = await fetch(this.url, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(body),
    })
    const sid = res.headers.get('mcp-session-id')
    if (sid) this.sessionId = sid

    if (!res.ok) {
      const text = await res.text().catch(() => '')
      throw new Error(`MCP HTTP ${res.status}: ${text.slice(0, 200)}`)
    }
    if (notification) return null

    const ct = res.headers.get('content-type') || ''
    const text = await res.text()
    if (!text) return null
    if (ct.includes('text/event-stream')) return parseSse(text)
    return JSON.parse(text) as JsonRpcResponse
  }

  async initialize(): Promise<void> {
    const res = await this.post({
      jsonrpc: '2.0',
      id: this.nextId++,
      method: 'initialize',
      params: {
        protocolVersion: '2025-11-25',
        capabilities: {},
        clientInfo: { name: 'AuraAssist Simulator', version: '1.0.0' },
      },
    })
    this.protocolVersion = res?.result?.protocolVersion ?? ''
    this.serverInfo = res?.result?.serverInfo ?? {}
    await this.post({ jsonrpc: '2.0', method: 'notifications/initialized' }, true)
  }

  async listTools(): Promise<ToolDef[]> {
    const res = await this.post({ jsonrpc: '2.0', id: this.nextId++, method: 'tools/list', params: {} })
    return res?.result?.tools ?? []
  }

  async callTool(name: string, args: Record<string, unknown> = {}): Promise<unknown> {
    const res = await this.post({
      jsonrpc: '2.0',
      id: this.nextId++,
      method: 'tools/call',
      params: { name, arguments: args },
    })
    if (res?.error) {
      throw new Error(res.error.message)
    }
    const content = res?.result?.content
    if (Array.isArray(content)) {
      const textPart = content.find((c: any) => c.type === 'text')
      if (textPart?.text) {
        try {
          return JSON.parse(textPart.text)
        } catch {
          return textPart.text
        }
      }
    }
    return res?.result
  }
}

function parseSse(text: string): JsonRpcResponse | null {
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith('data:')) {
      const data = line.slice(5).trim()
      if (data) {
        try {
          return JSON.parse(data) as JsonRpcResponse
        } catch {
          /* keep scanning */
        }
      }
    }
  }
  return null
}
