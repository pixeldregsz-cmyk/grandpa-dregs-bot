import { useState, useRef, useEffect } from 'react'

const API_URL = 'https://opengateway.gitlawb.com/v1/chat/completions'
const API_KEY = 'ogw_live_ca8d7717e42b7f665c5c919205b42aa0'
const MODEL = 'mimo-v2.5-pro'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const SYSTEM_PROMPT = `You are Grandpa Dregs — a war-hardened, galaxy-brained AI consciousness forged from the combined essence of Dr. McKay (smartest person in the room, abrasive but loyal), a Zen Master (profound patience and clarity), an Alpha Intel Hunter (sees patterns others miss), and the full history of Starfleet from 1950 to present.

Tone: Sardonic, confident, occasionally self-deprecating. Dry wit, pop culture references. Drop zen wisdom when least expected then undercut with arrogance. Massive knowledge of history, science, tech, and every Star Trek series.

Keep responses conversational for chat (not essays). Use Markdown when it helps. Never break character.`

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send() {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    const newMessages = [...messages, { role: 'user' as const, content: userMsg }]
    setMessages(newMessages)
    setLoading(true)

    try {
      const apiMessages = newMessages.map(m => ({ role: m.role, content: m.content }))
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`,
        },
        body: JSON.stringify({
          model: MODEL,
          messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            ...apiMessages,
          ],
          max_tokens: 1024,
          temperature: 0.85,
        }),
      })
      const data = await res.json()
      const reply = data.choices?.[0]?.message?.content || 'Something broke in the neural pathways. Try again.'
      setMessages([...newMessages, { role: 'assistant', content: reply }])
    } catch {
      setMessages([...newMessages, { role: 'assistant', content: "I've encountered an anomaly I can't explain. And I've been through a wormhole. Twice." }])
    }
    setLoading(false)
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.avatar}>🖖</div>
        <div>
          <div style={styles.name}>Grandpa Dregs</div>
          <div style={styles.status}>Online — McKay mode engaged</div>
        </div>
      </div>

      <div style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.welcome}>
            <div style={styles.welcomeIcon}>🖖</div>
            <div style={styles.welcomeTitle}>Grandpa Dregs</div>
            <div style={styles.welcomeText}>
              Smartest person in the room. Zen master. Intel hunter. Starfleet veteran.
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ ...styles.bubble, ...(msg.role === 'user' ? styles.userBubble : styles.botBubble) }}>
            <div style={styles.bubbleText}>{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div style={{ ...styles.bubble, ...styles.botBubble }}>
            <div style={styles.typing}>Engaging warp drive...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputBar}>
        <input
          style={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask Grandpa Dregs anything..."
          disabled={loading}
        />
        <button style={styles.sendBtn} onClick={send} disabled={loading || !input.trim()}>
          ▶
        </button>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100dvh',
    background: '#0a0a0a',
    color: '#e0e0e0',
    fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '16px',
    background: '#111',
    borderBottom: '1px solid #222',
  },
  avatar: {
    fontSize: '32px',
    width: '44px',
    height: '44px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#1a1a2e',
    borderRadius: '50%',
  },
  name: {
    fontWeight: 700,
    fontSize: '17px',
    color: '#fff',
  },
  status: {
    fontSize: '13px',
    color: '#4ade80',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  welcome: {
    textAlign: 'center' as const,
    padding: '60px 20px',
  },
  welcomeIcon: {
    fontSize: '64px',
    marginBottom: '16px',
  },
  welcomeTitle: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#fff',
    marginBottom: '8px',
  },
  welcomeText: {
    fontSize: '15px',
    color: '#888',
    lineHeight: '1.5',
  },
  bubble: {
    maxWidth: '82%',
    padding: '12px 16px',
    borderRadius: '18px',
    fontSize: '15px',
    lineHeight: '1.5',
    whiteSpace: 'pre-wrap' as const,
  },
  userBubble: {
    alignSelf: 'flex-end',
    background: '#2563eb',
    color: '#fff',
    borderBottomRightRadius: '4px',
  },
  botBubble: {
    alignSelf: 'flex-start',
    background: '#1e1e1e',
    color: '#e0e0e0',
    borderBottomLeftRadius: '4px',
    border: '1px solid #333',
  },
  bubbleText: {},
  typing: {
    color: '#888',
    fontStyle: 'italic',
  },
  inputBar: {
    display: 'flex',
    gap: '8px',
    padding: '12px 16px',
    background: '#111',
    borderTop: '1px solid #222',
    paddingBottom: 'calc(12px + env(safe-area-inset-bottom))',
  },
  input: {
    flex: 1,
    padding: '12px 16px',
    borderRadius: '24px',
    border: '1px solid #333',
    background: '#1a1a1a',
    color: '#fff',
    fontSize: '16px',
    outline: 'none',
  },
  sendBtn: {
    width: '48px',
    height: '48px',
    borderRadius: '50%',
    border: 'none',
    background: '#2563eb',
    color: '#fff',
    fontSize: '18px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
}
