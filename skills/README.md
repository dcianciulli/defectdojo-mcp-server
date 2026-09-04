# Installazione e distribuzione — skill `defectdojo` + server MCP

Guida operativa per installare la skill e/o il server MCP `defectdojo-mcp-server` su qualsiasi
agente di coding. Il repo è pensato per essere distribuito a tutti: nessun passaggio presuppone
strumenti o installazioni particolari dell'autore.

> **Ruolo dei due componenti**
> - **Skill** (`skills/defectdojo/SKILL.md`, formato standard Agent Skills): la *procedura* —
>   come cercare asset, chiudere vulnerabilità, gestire le risk acceptance. È solo testo, portabile.
> - **Server MCP**: gli *strumenti* che la skill usa. È un processo eseguibile sul PC di chi lo usa.
>
> Sono indipendenti: si installano insieme o separatamente. Una skill da sola NON configura
> server MCP (resta configurazione esplicita dell'host), fatta eccezione per il plugin Claude Code.

---

## 1. Prerequisiti (per tutti)

| Prerequisito | A cosa serve | Come verificarlo |
|---|---|---|
| `uv` / `uvx` | avvia il server MCP direttamente da git | `uvx --version` |
| Node.js + npx | solo per l'installatore `npx skills` | `npx --version` |
| `DEFECTDOJO_URL` | env var, es. `https://your-defectdojo.example.com` | nel profilo utente o nella config MCP |
| `DEFECTDOJO_API_KEY` | token personale (DefectDojo → profilo → API v2 Key) | idem |

Il token è **personale**: ogni azione (chiusure, note, accettazioni) risulta attribuita a chi
lo usa. Non condividere token tra colleghi.

---

## 2. Installazione della skill

### Metodo consigliato — `npx skills` (rileva gli agenti installati)

```bash
npx skills add https://github.com/dcianciulli/defectdojo-mcp-server -g
# oppure dal repository (fonte canonica):
npx skills add https://github.com/dcianciulli/defectdojo-mcp-server.git -g
```

Installa in Claude Code, OpenCode, Codex CLI, Cursor e altre harness compatibili in un colpo
solo (usa `-a claude-code -a opencode` per scegliere destinazioni precise). Aggiornamenti:
`npx skills check` / `npx skills update`.

### Manuale (senza Node.js)

Il contenuto della skill è identico per tutte le harness; cambia solo la cartella di destinazione.

| Harness | Percorso globale |
|---|---|
| Claude Code | `~/.claude/skills/defectdojo/` |
| OpenCode | `~/.config/opencode/skills/defectdojo/` |
| Codex CLI | `~/.codex/skills/defectdojo/` |
| Percorso agent-neutral | `~/.agents/skills/defectdojo/` (letto anche da OpenCode, Codex, Cursor e altri) |

```bash
git clone https://github.com/dcianciulli/defectdojo-mcp-server.git
cp -r defectdojo-mcp-server/skills/defectdojo ~/.agents/skills/   # esempio percorso agent-neutral
```

### Solo Claude Code — plugin (skill + MCP in un colpo)

```bash
claude plugin marketplace add dcianciulli/defectdojo-mcp-server
claude plugin install defectdojo@defectdojo-mcp
```

Il plugin configura anche il server MCP (punto 3) automaticamente: resta da impostare le due
env var (prerequisiti sopra) e riavviare Claude Code.

---

## 3. Configurazione del server MCP per harness

Snippet esatti, verificati sulla documentazione di ciascuna harness. La parte variabile è solo
il file di destinazione; il comando del server è sempre lo stesso (stdio, avvio da git, nessun
clone richiesto).

### OpenCode — `opencode.json` (progetto) o `~/.config/opencode/opencode.json` (globale)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "defectdojo": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/dcianciulli/defectdojo-mcp-server", "defectdojo-mcp-server"],
      "environment": {
        "DEFECTDOJO_URL": "https://your-defectdojo.example.com",
        "DEFECTDOJO_API_KEY": "{env:DEFECTDOJO_API_KEY}"
      },
      "enabled": true
    }
  }
}
```

(OpenCode v2: chiave `mcp.servers.defectdojo` e campo `disabled` invece di `enabled`.)

### Codex CLI — `~/.codex/config.toml`

```toml
[mcp_servers.defectdojo]
command = "uvx"
args = ["--from", "git+https://github.com/dcianciulli/defectdojo-mcp-server", "defectdojo-mcp-server"]
env = { DEFECTDOJO_URL = "https://your-defectdojo.example.com", DEFECTDOJO_API_KEY = "${DEFECTDOJO_API_KEY}" }
```

### Claude Code — `.mcp.json` (progetto) o `claude mcp add` (globale)

```json
{
  "mcpServers": {
    "defectdojo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/dcianciulli/defectdojo-mcp-server", "defectdojo-mcp-server"],
      "env": { "DEFECTDOJO_URL": "https://your-defectdojo.example.com", "DEFECTDOJO_API_KEY": "il-tuo-token" }
    }
  }
}
```

(Con il plugin del punto 2 questa config non serve: è inclusa.)

### Cursor — `~/.cursor/mcp.json` (stesso formato Claude)

```json
{
  "mcpServers": {
    "defectdojo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/dcianciulli/defectdojo-mcp-server", "defectdojo-mcp-server"],
      "env": { "DEFECTDOJO_URL": "https://your-defectdojo.example.com", "DEFECTDOJO_API_KEY": "il-tuo-token" }
    }
  }
}
```

### Gemini CLI — `~/.gemini/settings.json`

```json
{
  "mcpServers": {
    "defectdojo": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/dcianciulli/defectdojo-mcp-server", "defectdojo-mcp-server"],
      "env": { "DEFECTDOJO_URL": "https://your-defectdojo.example.com", "DEFECTDOJO_API_KEY": "il-tuo-token" }
    }
  }
}
```

### Kiro / Claude Desktop — `mcp.json`

Stesso formato JSON di Cursor/Gemini (vedi sopra); su Kiro il file è `~/.kiro/settings/mcp.json`.

### Altre harness agent-neutral

La skill standard (`SKILL.md`) viene letta da qualsiasi agente compatibile con il formato
Agent Skills anche da percorsi non elencati (es. `.agents/skills/` nel progetto). Per il server
MCP vale sempre la stessa coppia `command` + `env`: adattala al formato di config dell'host.

**Nota Windows**: senza `uvx` nel PATH, indicare il percorso assoluto a `uvx.exe`
(es. `C:\Users\<utente>\.local\bin\uvx.exe`).

---

## 4. Verifica post-installazione

1. Riavvia l'harness (o riconnetti i server MCP).
2. Chiedi all'agente: *"chi sono in DefectDojo?"* → deve rispondere con `get_current_user`.
3. Smoke test in sola lettura: *"elenca le finding attive di un asset a scelta, limit 5"*.
4. Se l'agente non usa la skill: verifica che la cartella sia quella giusta per la tua harness
   (tabella al punto 2) e che il frontmatter `name: defectdojo` corrisponda al nome della cartella.

## 5. Manutenzione

- **Fonte canonica della skill**: `skills/defectdojo/SKILL.md` in questo repo. Le modifiche
  vanno fatte qui, poi ricopiate/aggiornate nelle destinazioni (`npx skills update` per i
  download via `npx skills`).
- Skill e server evolvono insieme: quando si aggiunge/rimuove un tool, aggiornare
  `SKILL.md`, la tabella tool di questo repo (`README.md`) ed eventualmente i manifest
  `.claude-plugin/` (bump versione).
- Il server si scarica da git a ogni avvio (uvx): dopo ogni push è sufficiente riavviare la
  connessione MCP dell'harness per usare il codice aggiornato.
