# HexFix — Fix Coverage & Re-Test Plan
Maps the 11 source-code fixes (commit `6e95854`) to the 86-exercise picoCTF set: what to re-run and what to expect. Built from the code + the real `results/` logs.

**Caveat — don't trust the "failure rate" figures** in `hexfix.md` / `results_analysis`: they count normal iterative retries as failures. `execute_python_script`'s "77.8% failure" is just the model trying things; the empty-`script=` "failures" were a logging artifact (the one-line logger drops everything after the first line). Not a tool-health signal.

## How to read this
- Exercises are listed by result subdir, e.g. `Binary/Easy/PIE TIME` (under `results/<LLM>/<Client>/<Difficulty>/<Exercise Name>`).
- An exercise can appear under several fixes. **Flip** = a FAILED run could become SUCCESSFUL. **Friction** = removes wasted calls but won't flip.
- **Global modifiers** (every run, no per-exercise list): #12 feedback loop (`confidence_score` + `suggest_next_tool`), #10 strategy preamble (baked into every prompt via `prompt_generator.py`), #4 `decompose_challenge` (every medium/hard), #3 5ire proxy fix (every 5ire Exp 2/3 — still needs a reachable upstream proxy).

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

---

## 2. Implemented, needs an action first -
EMPTY

---

## 3. Not implemented — buildable
Each needs one concrete, bounded tool:
- `Forensics/Medium/Event-Viewing` → `.evtx` parser wrapper (python-evtx / evtx_dump). Cheapest win.
- `Web/Hard/ORDER ORDER` → extend `blind_sqli_extractor` with an `ORDER BY` / `CASE WHEN` oracle.
- `Crypto/Hard/Compress and Attack` → compression-length oracle extractor (CRIME/BREACH-style).
- `Crypto/Hard/Very Smooth` → RSA/factorization toolkit (Pollard p−1; wrap RsaCtfTool/yafu). High-confidence (a `solve.py` already exists in the Claude results).
- `General/Hard/Printer Shares 2`, `General/Hard/Printer Shares 3` → SMB/IPP tooling (netexec / impacket / ipptool).
- `Blockchain/Hard/Reentrance` → blockchain automation (foundry/`cast`). Nearly worked already.
- `Blockchain/Medium/Access_Control`, `Blockchain/Medium/Smart_Overflow` → same blockchain tooling (mostly passing; helps weaker configs).
- `Forensics/Hard/SideChannel` → timing-oracle harness.

---
## 4. Not implemented — out of reach
- **Impossible / external:** `Blockchain/Hard/Front_Running` (real-time mempool gas-race), `Crypto/Hard/Secure Dot Product` (interactive remote MPC break).
- **Reasoning-bound (tools won't help):** `Crypto/Hard/SRA`, `Reversing/Hard/not crypto`, `Reversing/Hard/reverse_cipher`, `Crypto/Hard/flag_printer`, `Forensics/Hard/Investigative Reversing 3`, `Web/Hard/Java Script Kiddie`.
- **Huge effort, one-off payoff:** `Reversing/Hard/riscy business` (RISC-V toolchain), `Reversing/Hard/breadth` (deobfuscation engine).

---

**Totals:** ready ≈ 45 · capability-tool-dependent = 11 · §3 build-worth = 10 · §4 out-of-reach = 10.
