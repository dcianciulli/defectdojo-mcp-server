# Skill `defectdojo` — distribuzione multi-harness

Skill agente portabile nel formato standard **Agent Skills** (`SKILL.md` + frontmatter),
compatibile con Claude Code, OpenCode, Codex CLI, Cursor, Gemini CLI e Hermes.
La skill guida l'uso del server MCP `defectdojo-mcp-server` (stesso repo, cartella `skills/`).

> La skill insegna al modello COME usare i tool; il server MCP fornisce i tool.
> Servono entrambi: skill = procedura, server = esecuzione.

## Installazione

Il percorso cambia per harness, il file no. Copia `skills/defectdojo/` nella destinazione:

| Harness | Percorso (globale) | Percorso (progetto) |
|---|---|---|
| Claude Code | `~/.claude/skills/defectdojo/` | `.claude/skills/defectdojo/` |
| OpenCode | `~/.config/opencode/skills/defectdojo/` | `.opencode/skills/defectdojo/` |
| Codex CLI | `~/.codex/skills/defectdojo/` (`$CODEX_HOME/skills/`) | `~/.agents/skills/defectdojo/` |
| Cursor | `~/.agents/skills/defectdojo/` | `.agents/skills/defectdojo/` |
| Gemini CLI | `~/.gemini/skills/defectdojo/` | `.gemini/skills/defectdojo/` |
| Hermes | gestita dalla skill interna `defectdojo` (già installata) | — |

Installazione rapida (una riga, dalla root di questo repo):

```bash
# Claude Code
mkdir -p ~/.claude/skills && cp -r skills/defectdojo ~/.claude/skills/
# OpenCode
mkdir -p ~/.config/opencode/skills && cp -r skills/defectdojo ~/.config/opencode/skills/
# Codex CLI
mkdir -p ~/.codex/skills && cp -r skills/defectdojo ~/.codex/skills/
# Percorso agent-neutral (Cursor e altri; è anche quello che OpenCode e Codex sanno leggere)
mkdir -p ~/.agents/skills && cp -r skills/defectdojo ~/.agents/skills/
```

Su Windows (Git Bash) i percorsi sono gli stessi con `$HOME` (es. `$HOME/.claude/skills`).
In alternativa al copia: `npx skills add <repo-url>` (il CLI `skills` installa nelle directory standard).

## Configurazione del server MCP per harness

Prerequisiti per tutti: `uv`/`uvx` installato, e le due variabili d'ambiente
`DEFECTDOJO_URL` (es. `https://your-defectdojo.example.com`) e `DEFECTDOJO_API_KEY` (token dal profilo DefectDojo → API v2 Key).

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

### Hermes — `~/AppData/Local/hermes/config.yaml`

```yaml
mcpServers:
  defectdojo:
    command: uvx
    args:
      - --from
      - git+https://github.com/dcianciulli/defectdojo-mcp-server
      - defectdojo-mcp-server
    env:
      DEFECTDOJO_URL: https://your-defectdojo.example.com
      DEFECTDOJO_API_KEY: ${env:DEFECTDOJO_API_KEY}
```

Nota Windows: in assenza di `uvx`, usare il path assoluto a `uv.exe` (es. `C:\Users\<utente>\.local\bin\uvx.exe`).

## Manutenzione

- La fonte canonica della skill è `skills/defectdojo/SKILL.md` in questo repo: modificarla qui e ricopiare nelle harness.
- La skill interna Hermes (`defectdojo`) resta per l'uso locale; questa copia è la versione distribuibile (aggiornata al server v3 con chiusure e risk acceptance).
- Rilasci del server: la skill è indipendente dal codice; i tool citati esistono già nell'istanza.
- Il token API è personale: chi lo usa agisce in DefectDojo come quel utente (attribuzione corretta di note e chiusure).

## Verifica post-installazione

1. Riavvia l'harness (o riconnetti i server MCP).
2. Verifica che il server risponda: chiedi all'agente "chi sono in DefectDojo?" (tool `get_current_user`).
3. Smoke test in sola lettura: "elenca le finding attive di un asset a scelta, limit 5".