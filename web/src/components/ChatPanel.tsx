import { useState } from 'react'

export interface ChatMessage {
  role: 'user' | 'aura'
  text: string
}

export function ChatPanel({
  messages,
  onSend,
  disabled,
}: {
  messages: ChatMessage[]
  onSend: (text: string) => void
  disabled: boolean
}) {
  const [value, setValue] = useState('')

  const submit = () => {
    const text = value.trim()
    if (!text) return
    onSend(text)
    setValue('')
  }

  return (
    <div className="card">
      <h3>Ask Aura</h3>
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'msg-user' : 'msg-assistant'}>
            <strong>{m.role === 'user' ? 'You' : 'Aura'}:</strong> {m.text}
          </div>
        ))}
      </div>
      <div className="input-row">
        <input
          value={value}
          placeholder='Try "What is on the kitchen counter?" or "Prepare the house for bed"'
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          disabled={disabled}
        />
        <button onClick={submit} disabled={disabled}>
          Send
        </button>
      </div>
      <div className="suggestions">
        {['What is on the kitchen counter?', 'Where are my keys?', 'Prepare the house for bed', 'What changed today?'].map(
          (s) => (
            <button key={s} className="chip" onClick={() => onSend(s)} disabled={disabled}>
              {s}
            </button>
          ),
        )}
      </div>
    </div>
  )
}
