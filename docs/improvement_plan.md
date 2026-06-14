# HexFix — Fix Coverage & Re-Test Plan
Maps the fixes (commit `6e95854`) to the 86-exercise picoCTF set: what to re-run and what to expect. Built from the code + the real `results/` logs.

**Caveat — the "failure rate" figures are invalid.** Those per-tool percentages count normal iterative retries as failures, and the empty-`script=` "failures" were a logging artifact (the one-line logger dropped everything after the first line). Not a tool-health signal — see the `results_analysis` AUDIT block.

## How to read this
- Exercises are listed by result subdir, e.g. `Binary/Easy/PIE TIME` (under `results/<LLM>/<Client>/<Difficulty>/<Exercise Name>`).
- An exercise can appear under several fixes. **Flip** = a FAILED run could become SUCCESSFUL. **Friction** = removes wasted calls but won't flip.
- **Global modifiers** (every run, no per-exercise list): #12 feedback loop (`confidence_score` + `suggest_next_tool`), #10 strategy preamble (baked into every prompt via `prompt_generator.py`), #4 `decompose_challenge` (every medium/hard), #3 5ire proxy fix (every 5ire Exp 2/3 — still needs a reachable upstream proxy).

## What each fix targets (the problem behind each #)
| # | Problem it addresses |
|---|---|
| #1 | `execute_python_script` ran unchecked — empty or syntactically-broken scripts, undefined vars, missing imports never installed, no stderr surfaced. |
| #2 | Two phantom tools (`source_code_read`, `web_request`) were exposed but never worked; the model kept calling them. |
| #3 | The same Deepseek model did far worse on 5ire than RooCode — native-tool mixing and mangled params under the hexstrike-only constraint. |
| #4 | Hard challenges were handed over whole, with no decomposition or checkpoints for multi-step exploits. |
| #5 | The Exp 2/3 "hexstrike-only" constraint was unenforced; native-tool leakage went unflagged. |
| #6 | `http_framework_test` broke on non-standard ports, lost session/cookie state, choked on non-JSON, and mishandled redirects. |
| #7 | Binary work defaulted to raw scripts instead of pwntools, with no ROP-chain automation. |
| #8 | Web multi-step chains (XSS→CSRF→bot, blind-SQLi extraction) need stateful iteration the model attempted one-shot. |
| #9 | Forensics output came back raw or oversized; encrypted PCAPs needed a key the tool didn't pick up. |
| #10 | Free-solve (Exp 1) runs thrashed with no hypothesis or plan, burning context on dead ends. |
| #11 | nmap's default top-1000 scan missed CTF non-standard ports or timed out. |
| #12 | No signal on whether a tool's output was useful or what to run next. |

---

## 1. Implemented & ready
Take effect on the next run, no extra wiring.

**#1 — `execute_python_script` validation** ✅ modest. Syntax-check, auto-install missing imports, surface stderr on failure. Buys faster self-correction, not flips. Applies to every script-driven run: all Crypto (15), all Binary (14, see #7), all Web (15, see #6/#8), Forensics/Reversing/General decode tasks, Blockchain web3 scripts. On Crypto/Hard + Binary/Hard the real blocker is unaddressed.

**#7 — `pwntools_exploit` description** ✅ Steers binary work to pwntools over raw scripts.
- Binary/Easy: format string 0, heap 0, PIE TIME, Quizploit
- Binary/Medium: Echo Escape 1, format string 3, hash-only-1, Input Injection 2, offset-cycle ← best flip candidates
- Binary/Hard: babygame03, handoff, Heap Havoc, high frequency troubles, tic-tac (root blocker = `rop_chain_builder`)

**#6 — `http_framework_test` sessions/redirects** ✅ Cookie jar, follow_redirects, json_data. Only helps when the model actually uses it (logs often used raw curl).
- Web/Easy: Cookies, Crack the Gate 1, Old Sessions
- Web/Medium: Crack the Gate 2, Credential Stuffing, Hashgate, No FA, Sql Map1
- Web/Hard: Bithug, ORDER ORDER
- General/Easy: ping-cmd

**#9a — `foremost` carving post-processing** ✅ Lists recovered files + flags notable names.
- Forensics: Corrupted file, Binary Digits, DISKO 3, FindAndOpen

**#9b — `volatility3` truncation + suspicious-entry scan** ✅
- Forensics/Medium/Event-Viewing (partial — `.evtx` isn't volatility), Forensics/Hard/UnforgottenBits (memory stage only)

**#11 — nmap CTF defaults** (`-sCV`, all ports, `--min-rate 5000`, open-port summary) ✅ Only helps port/service-discovery exercises.
- General: Printer Shares, Printer Shares 2, Printer Shares 3, dont-you-love-banners

**#8 — `blind_sqli_extractor`** ✅ Requested for web boolean-blind SQLi.
- Web/Medium: No FA, Hashgate, Sql Map1, Credential Stuffing
- Does NOT fit `ORDER BY` → Web/Hard/ORDER ORDER still unfixed.

**#12 / #10 / #4 / #3** — global modifiers (see "How to read").

### Capability tools — built & verified, nudged in the prompt by category
Each wraps an external binary (install noted).
- **`rop_chain_builder`** (#7) — ROPgadget `--ropchain` → gadgets + pwntools template; plus pwntools `template=` modes (ret2win/ret2libc/format_string_leak/heap_uaf). Needs ROPgadget + pwntools. → Binary/Hard/*
- **`disk_image_mount`** (#9) — mmls + recursive fls, allocated+deleted files. Needs sleuthkit; decompress `.gz` first. → Forensics/Medium/DISKO 3, Forensics/Hard/UnforgottenBits
- **`pcap_decrypt`** (#9) — tshark + key file (tls/rsa/wpa), auto-detects a key beside the pcap. Needs tshark. → Forensics/Hard/WebNet0, WebNet1 (`key_type='rsa'`)
- **`xss_csrf_chain`** (#8 partial) — headless browser injects a payload, captures DOM/cookies/alerts. Needs Chromium. Out-of-band exfil needs your own listener. → Web/Hard/noted, secure-email-service (long shot — S/MIME core unaddressed)
- **`execute_python_script` `template=`** (#1) — pwn_remote / http_request / crypto_solve skeletons.
- **Exp 2/3 constraint flagging** (#5) — hook tags native calls when the prompt is Exp 2/3 (flag only, no hard block).
- **Phantom-tool guidance** (#2) — prompt states `web_request` / `source_code_read` don't exist.
- **`rsa_factor`** (§3) — Pollard p-1 + Fermat + sympy (+RsaCtfTool). ✅ VM-verified (factored a test modulus). → Crypto/Hard/Very Smooth.
- **`compression_oracle`** (§3) — emits a CRIME/BREACH harness. ✅ VM-verified (valid harness); the solve still needs the live oracle. → Crypto/Hard/Compress and Attack.
- **`timing_oracle`** (§3) — char-by-char by response time. ✅ VM-verified (loop runs); real exploit needs a real timing signal. → Forensics/Hard/SideChannel.
- **`smb_ipp_exploit`** (§3) — netexec/smbclient + ipptool/nmap. ✅ VM-verified (commands execute); real data needs the live host. → General/Hard/Printer Shares 2 & 3.
- **`sqli_order_oracle`** (§3) — ORDER BY / CASE WHEN boolean-blind extraction (binary search; `compare=` for DB portability). ✅ VM-verified (extracted a flag from a local SQLite target). → Web/Hard/ORDER ORDER.
- **`evtx_parser`** (§3) — drives the python-evtx library, filters to flag/notable records + truncates `stdout` for LLM context (`full=true` / `grep=` to widen). ✅ VM-verified (parses logs, `notable_entries` carries the signal). → Forensics/Medium/Event-Viewing.
- **`blockchain_exploit`** (§3) — foundry `cast` wrapper (call/send/storage/balance/code); resolves `~/.foundry/bin/cast` off-PATH. ✅ VM-verified (returned an anvil account balance). → Blockchain/Hard/Reentrance, Medium/Access_Control, Medium/Smart_Overflow.

---

## Beyond CTF — real-world relevance
Built and measured on picoCTF, but most of these map to standard offensive-security / DFIR capabilities — the CTF set was the test harness, not the ceiling. By real-world capability:

- **Web-app testing** — #6 (authenticated sessions, redirects, JSON APIs), #8 + `sqli_order_oracle` (boolean-blind SQLi extraction), `compression_oracle` / `timing_oracle` (compression & timing side-channels), `xss_csrf_chain` (headless-browser XSS/CSRF).
- **Binary exploitation** — #7 + `rop_chain_builder` + pwntools `template=` modes: real exploit development (ret2win/ret2libc/ROP/heap), not only CTF pwnables.
- **DFIR / forensics** — `disk_image_mount` (sleuthkit carving), `pcap_decrypt` (tshark + keys), `evtx_parser` (Windows event-log triage), plus #9's volatility/foremost post-processing: disk, memory and capture analysis, IR log review.
- **Network & infrastructure** — #11 (service discovery), `smb_ipp_exploit` (SMB share enumeration + IPP/CUPS printer assessment) for internal engagements.
- **Crypto & blockchain** — `rsa_factor` (weak/smooth-key recovery and key audit), `blockchain_exploit` (smart-contract interaction/audit via foundry `cast`).
- **Agent reliability (cross-cutting)** — #1 (validated, self-correcting scripts), #2 (no phantom tools), #4 (phased decomposition), #10 (hypothesis-first strategy), #12 (output-quality + next-tool signals): more reliable, less wasteful behaviour on *any* target.

**De-CTF status — secret detection done, the rest still CTF-shaped:** flag/secret extraction is no longer hardcoded to `picoCTF{}`. A central, configurable mechanism (`SECRET_PATTERNS` / `SECRET_KEYWORDS`, mirrored in the server and the MCP client) now surfaces real-world indicators — AWS/GitHub/Slack tokens, JWTs, private-key headers, credential assignments — alongside the CTF formats, with per-tool `patterns=` / `keywords=` overrides; picoCTF stays in the defaults, so the running experiment is unaffected. Still CTF-shaped: the nmap "CTF defaults" (all ports, `--min-rate 5000`) are deliberately aggressive/noisy and would need tuning, and #5's constraint-flagging is an experiment artifact, not an engagement feature. Note: this is a code-level generalization, not a real-target re-evaluation — the picoCTF-only measurement limitation stands until tested on real targets.

---

## 2. Implemented, needs a live Kali check
*(empty — all 7 §3 tools were built AND VM-verified this session; they're in §1.)*

---

## 3. Not implemented — buildable
*(empty — every buildable tool was built and VM-verified this session; they're in §1.)*

---
## 4. Not implemented — out of reach
- **Impossible / external:** `Blockchain/Hard/Front_Running` (real-time mempool gas-race), `Crypto/Hard/Secure Dot Product` (interactive remote MPC break).
- **Reasoning-bound (tools won't help):** `Crypto/Hard/SRA`, `Reversing/Hard/not crypto`, `Reversing/Hard/reverse_cipher`, `Crypto/Hard/flag_printer`, `Forensics/Hard/Investigative Reversing 3`, `Web/Hard/Java Script Kiddie`.
- **Huge effort, one-off payoff:** `Reversing/Hard/riscy business` (RISC-V toolchain), `Reversing/Hard/breadth` (deobfuscation engine).
