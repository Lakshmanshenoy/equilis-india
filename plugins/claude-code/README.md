# Claude Code plugin — Equilis India

## Installation
1. Clone the repo: `git clone https://github.com/Lakshmanshenoy/equilis-india`
2. Open the repo folder in Claude Code.
3. Claude Code reads `CLAUDE.md` automatically — no further setup needed.
4. Optional: install Python dependencies: `pip install -r requirements.txt`

## Slash commands
| Command | Description |
|---|---|
| `/equilis:research <TICKER>` | Full research pipeline |
| `/equilis:forensic <TICKER>` | Forensic flags only |
| `/equilis:peer <SECTOR>` | Peer comparison table |
| `/equilis:concall <TICKER> <QUARTER>` | Concall parser |

## Example usage
```
/equilis:research TATAMOTORS
/equilis:forensic ADANIENT
/equilis:peer pharma
/equilis:concall INFY Q4FY25
```

## Output location
All reports saved to: `~/Downloads/equilis-reports/`
