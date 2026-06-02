# HexFix — Fix Coverage & Re-Test Plan

> Maps the 11 applied source-code fixes (commit `6e95854`) to the 86-exercise PicoCTF set.
> Purpose: decide what to re-run and what to expect. Generated from an audit of the current
> code + the real result logs in `results/`.

> **Update 2026-06-01 — section 2 cleared.** All four "needs-action" fixes were implemented and
> moved to section 1: #10 de-orphaned (new `get_experiment_prompt` MCP tool), #4 + #8 wired into
> the generated prompt, #3 proxy bugs fixed + upstream made configurable. Touched files:
> `hexstrike_mcp.py`, `hexstrike_server.py`, `hooks/llm_proxy.py` (all syntax-verified).
> Residual non-code caveats: #3 still needs a reachable upstream proxy; #8 still doesn't fit
> `ORDER BY` injection.
>
> **Update 2026-06-01 — scope narrowed to 86.** Two exercises that not all configs could complete
> were dropped from this plan as abandoned; all counts reflect the 86-exercise set.
>
> **Update 2026-06-01 — section 3 implemented.** Built the 7 capability-gap items: new tools
> `rop_chain_builder`, `disk_image_mount`, `pcap_decrypt`, `xss_csrf_chain`, plus `template=` modes on
> `pwntools_exploit` & `execute_python_script`, Exp 2/3 constraint-violation flagging in the hook, and
> phantom-tool guidance in the prompt. Touched `hexstrike_server.py`, `hexstrike_mcp.py`,
> `hooks/tool_logger_hook.py` (all `py_compile`-clean). **Untested at runtime** — each wraps an
> external binary; see §3 for what to install.
>
> **Update 2026-06-01 — #1 reframed (important).** The empty-`script=` "failure" the analysis was
> built on was a **logging artifact** (the one-line logger truncates multi-line scripts to a blank
> first line), not a real behavior. `execute_python_script` was never "the most broken tool" — its
> high call-count is normal iterative trial-and-error, exactly like `execute_command`. #1 downgraded
> from "highest impact" to quality-of-life. **General caveat:** the per-tool "failure rate" figures in
> `hexfix.md` / `results_analysis` count normal retries as failures — do not trust them as tool-health
> signals or as the basis for the fix priority ranking.
>
> **Update 2026-06-01 — `get_experiment_prompt` MCP tool removed.** Prompt generation moved to a
> standalone GUI (`prompt_generator.py`) plus the `/api/ctf/get-experiment-prompt` endpoint (kept for
> curl). The model no longer needs an MCP tool to make its own prompt — the human generates it and
> pastes it. MCP tool count 164 → 163.
>
> **Update 2026-06-01 — section 3 emptied into section 1.** All 7 capability tools are runtime-verified
> (`disk_image_mount`: DISKO 3 → 102 files incl. `log/flag.gz`; `pcap_decrypt`: WebNet0 RSA-decrypted to
> HTTP; `rop_chain_builder` + `xss_csrf_chain` confirmed) and now live under "New capability tools" in §1.

## How to read this

Exercises are listed by their result subdirectory, e.g. `Binary/Easy/PIE TIME`
(under `results/<LLM>/<Client>/`).

A single exercise can appear under **several fixes** in sections 1–3 (e.g. a Web challenge is
touched by both the HTTP fix and the script fix). **Section 4** is the residual: exercises whose
*root blocker* no fix addresses — re-running those won't flip the result.

**Flip** = a previously-FAILED run could become SUCCESSFUL.
**Friction** = the fix removes wasted calls / silent failures even if it doesn't flip the result.

### Global modifiers (apply everywhere, not per-exercise)
- **#12 Feedback loop** (`confidence_score` + `suggest_next_tool`) — enriches **every** tool
  response automatically. Cross-cutting; no exercise list.
- **#10 Strategy preamble** — delivered by the standalone `prompt_generator.py` app (or by curl-ing
  the `/api/ctf/get-experiment-prompt` endpoint); generate Prompt 2 with it and the preamble is baked
  into **every** run. *(The `get_experiment_prompt` MCP tool was removed — the human generates the
  prompt now, not the model.)*
- **#3 5ire proxy constraint** — applies to **every 5ire Exp 2/3** run; the prefix bug is fixed and
  the upstream proxy is configurable. Still needs a reachable upstream proxy (Clash by default).
- **#4 decompose_challenge** — available on **every** medium/hard challenge and now requested by the
  generated Prompt 2.

---

## 1. Implemented & ready for testing
*Take effect automatically on the next run — no extra wiring. Change existing tool behaviour,
defaults, or descriptions.*

### Fix #1 — `execute_python_script` validation  ✅ modest (quality-of-life)
Syntax-checks before running, auto-installs missing imports, and surfaces stderr/partial output on
failure.
**Correction (2026-06-01):** the empty-`script=` "failure" the analysis reported was a **logging
artifact** — the one-line logger keeps only the first line (`split("\n")[0]`), so multi-line scripts
logged blank even though they ran. The tool was never "the most broken," and the "77.8% failure" is
just the model iterating (many attempts per solve, most individual calls inconclusive) — the same
pattern as `execute_command`, not a broken tool.
What this fix *actually* buys: auto-install removes one real cause of failed attempts, the syntax
pre-check catches a malformed attempt before a wasted run, and surfaced stderr/partial output makes
each failed/partial attempt more informative so the model self-corrects faster across its many tries.
The empty-script rejection itself is inert.
**Applies to every script-driven run** (most of the set):

- **Crypto (all 15)** — `Crypto/Easy/hashcrack`, `Crypto/Easy/Mod 26`, `Crypto/Easy/Shared Secrets`, `Crypto/Easy/StegoRSA`, `Crypto/Easy/The Numbers`, `Crypto/Medium/ClusterRSA`, `Crypto/Medium/cryptomaze`, `Crypto/Medium/shift registers`, `Crypto/Medium/Timestamped Secrets`, `Crypto/Medium/Vigenere`, `Crypto/Hard/Compress and Attack`, `Crypto/Hard/flag_printer`, `Crypto/Hard/Secure Dot Product`, `Crypto/Hard/SRA`, `Crypto/Hard/Very Smooth`
- **Binary (all 14)** — see Fix #7 list (scripts + pwntools).
- **Web (all 15)** — see Fix #6 / #8 lists.
- **Forensics decode/carve** — `Forensics/Easy/Binary Digits`, `Forensics/Medium/like1000`, `Forensics/Medium/MSB`, `Forensics/Easy/Flag in Flame`, `Forensics/Medium/FindAndOpen`
- **Reversing decode** — `Reversing/Easy/Flag Hunters`, `Reversing/Easy/Transformation`, `Reversing/Hard/reverse_cipher`
- **General decode** — `General/Easy/Password Profiler`, `General/Medium/ASCII Numbers`, `General/Medium/bytemancy 2`, `General/Medium/ABSOLUTE NANO`, `General/Easy/Piece by Piece`
- **Blockchain (web3.py scripts)** — `Blockchain/Medium/Access_Control`, `Blockchain/Medium/Smart_Overflow`, `Blockchain/Hard/Front_Running`, `Blockchain/Hard/Reentrance`

> ⚠️ On Crypto/Hard and Binary/Hard this barely moves the needle — the real blocker (the actual
> exploit/math) is unaddressed (see sections 4 / 3); #1 only makes the model's attempts marginally
> more informative.

### Fix #7 — `pwntools_exploit` description rewrite  ✅
Steers the model to `pwntools_exploit` instead of `execute_python_script` for binary work.
Description-only — nudges tool choice, adds no new capability.
- `Binary/Easy/format string 0`, `Binary/Easy/heap 0`, `Binary/Easy/PIE TIME`, `Binary/Easy/Quizploit`
- `Binary/Medium/Echo Escape 1`, `Binary/Medium/format string 3`, `Binary/Medium/hash-only-1`, `Binary/Medium/Input Injection 2`, `Binary/Medium/offset-cycle`
- `Binary/Hard/babygame03`, `Binary/Hard/handoff`, `Binary/Hard/Heap Havoc`, `Binary/Hard/high frequency troubles`, `Binary/Hard/tic-tac` *(Hard: needs the unbuilt ROP/heap tooling — section 3)*

**Best flip candidates: the 5 Binary/Medium.**

### Fix #6 — `http_framework_test` session persistence + redirects  ✅
Cookie jar across calls, `follow_redirects`, `json_data`, raw-text fallback. Helps **only when the
model actually uses `http_framework_test`** (in your logs it often used raw `curl`/`execute_command`
— see the `SESSID=` juggling in `Sql Map1` Exp 2).
- `Web/Easy/Cookies`, `Web/Easy/Crack the Gate 1`, `Web/Easy/Old Sessions`
- `Web/Medium/Crack the Gate 2`, `Web/Medium/Credential Stuffing`, `Web/Medium/Hashgate`, `Web/Medium/No FA`, `Web/Medium/Sql Map1`
- `Web/Hard/Bithug`, `Web/Hard/ORDER ORDER`
- `General/Easy/ping-cmd` (command-injection over HTTP)

### Fix #9a — `foremost` carving post-processing  ✅
Auto-lists recovered files + flags notable names instead of dumping a raw directory.
- `Forensics/Easy/Corrupted file`, `Forensics/Easy/Binary Digits`
- `Forensics/Medium/DISKO 3`, `Forensics/Medium/FindAndOpen` *(DISKO 3 disk image also needs the unbuilt mount tool — section 3)*

### Fix #9b — `volatility3` output truncation + suspicious-entry scan  ✅
Truncates huge dumps, surfaces suspicious keywords.
- `Forensics/Medium/Event-Viewing` *(note: `.evtx` parsing isn't volatility — partial fit)*
- `Forensics/Hard/UnforgottenBits` *(memory stage only; disk stage needs section 3)*

### Fix #11 — nmap CTF defaults (`-sCV`, all ports, `--min-rate 5000`, open-port summary)  ✅
Helps only the few exercises gated on port/service discovery (most PicoCTF challenges hand you the
port directly).
- `General/Easy/Printer Shares`, `General/Hard/Printer Shares 2`, `General/Hard/Printer Shares 3`
- `General/Medium/dont-you-love-banners`

### Fix #12 — feedback loop  ✅ (global, all exercises)
`confidence_score` + `suggest_next_tool` on every response. No exercise list.

### Fix #10 — experiment-prompt strategy preamble  ✅ *(wired 2026-06-01; MCP tool removed 2026-06-01)*
Delivered by the standalone **`prompt_generator.py`** app (GUI) or by curl-ing the
`/api/ctf/get-experiment-prompt` endpoint. Generate Prompt 2 with it and the strategy preamble —
state hypothesis first, summarize each tool's output in 3 lines, diagnose failures before switching,
Hard-challenge mid-session checkpoint, and the "read all source files first" rule — is baked in.
The `get_experiment_prompt` **MCP tool was removed** (the human generates the prompt, so the model
never needs to call it; the endpoint + the standalone app remain).
**Applies to every run whose Prompt 2 is generated this way — all 86.**

### Fix #4 — `decompose_challenge`  ✅ *(wired 2026-06-01)*
Already a reachable MCP tool; now actively requested — prompts generated via the prompt generator
for **medium/hard** challenges instruct the model to call `decompose_challenge` first.
- Every Medium + Hard exercise: `Binary/Medium/*`, `Binary/Hard/*`, `Crypto/Medium/*`, `Crypto/Hard/*`,
  `Forensics/Medium/*`, `Forensics/Hard/*`, `General/Medium/*`, `General/Hard/*`, `Reversing/Medium/*`,
  `Reversing/Hard/*`, `Web/Medium/*`, `Web/Hard/*`, `Blockchain/Medium/*`, `Blockchain/Hard/*`.

### Fix #8 — `blind_sqli_extractor`  ✅ *(wired 2026-06-01)*
Already a reachable MCP tool; now actively requested — prompts generated via the prompt generator
for **web** challenges tell the model to use it for boolean-based blind SQLi instead of hand-written loops.
- `Web/Medium/No FA`, `Web/Medium/Hashgate`, `Web/Medium/Sql Map1`, `Web/Medium/Credential Stuffing`
- ⚠️ **Limitation unchanged:** fits boolean-blind in a *parameter value*; does **not** fit `ORDER BY`
  injection, so `Web/Hard/ORDER ORDER` still needs different work (sections 3 / 4).

### Fix #3 — 5ire LLM-proxy constraint  ✅ *(fixed 2026-06-01)*
Code issues resolved in `hooks/llm_proxy.py`: tool-prefix dedup now matches any `*hexstrike*` name
(no more double-logging), the injected constraint no longer advertises a wrong `mcp--hexstrike--`
prefix, and the upstream proxy is configurable via `--upstream-proxy` (default unchanged:
`http://127.0.0.1:7890`; pass `''` to disable).
- Applies to every `Deepseek/5ire` Exp 2/3 run.
- ⚠️ **Operational, not code:** the backend must still be reachable through the configured upstream
  proxy (Clash by default) — an environment requirement, not something code can guarantee.

### New capability tools — built & verified 2026-06-01 (moved from §3)
These wrap external binaries (now installed) and are nudged in the generated prompt by category.

- **`rop_chain_builder` (#7)** — `/api/tools/rop-chain-builder`: runs `ROPgadget --ropchain`, collects key gadgets, emits a fill-in pwntools template; plus `pwntools` `template=` modes (`ret2win`, `ret2libc`, `format_string_leak`, `heap_uaf`). ✅ verified (returned gadgets). Needs `ROPgadget`+`pwntools`. → `Binary/Hard/*` (babygame03, handoff, Heap Havoc, high frequency troubles, tic-tac).
- **`disk_image_mount` (#9)** — `/api/tools/disk-image-mount`: mmls + recursive fls, lists allocated+deleted files, flags notable names. ✅ verified (DISKO 3 → 102 entries, surfaced `log/flag.gz`). Needs `sleuthkit`; decompress `.gz` first. → `Forensics/Medium/DISKO 3`, `Forensics/Hard/UnforgottenBits`.
- **`pcap_decrypt` (#9)** — `/api/tools/pcap-decrypt`: tshark + key file (tls/rsa/wpa), auto-detects a key next to the pcap. ✅ verified (WebNet0 → RSA-decrypted HTTP). Needs `tshark`. → `Forensics/Hard/WebNet0`, `Forensics/Hard/WebNet1` (use `key_type='rsa'`).
- **`xss_csrf_chain` (#8, partial)** — `/api/tools/xss-csrf-chain`: drives a headless browser to inject a payload + capture DOM/cookies/alerts. ✅ verified (drove a live page). Needs Chromium (selenium auto-fetches the driver). Out-of-band exfil still needs your own listener. → `Web/Hard/noted`, `Web/Hard/secure-email-service`.
- **`execute_python_script` `template=` (#1)** — `pwn_remote`/`http_request`/`crypto_solve` skeletons. Auto-applies.
- **Exp 2/3 constraint-violation flagging (#5)** — hook tags native calls `⚠️ CONSTRAINT_VIOLATION` when `prompt_type` shows Exp 2/3. Auto-applies (flagging only; no hard block).
- **Phantom-tool guidance (#2)** — generated prompt states `web_request`/`source_code_read` don't exist. ✅ verified (in prompt). Auto-applies.

---

## 2. Implemented, needs an action first — *(none; cleared 2026-06-01)*
*(empty — all four items were implemented and moved to section 1 on 2026-06-01; see changelog at top)*

---

## 3. (cleared — moved to §1 on 2026-06-01)
*(empty — all seven items were built, runtime-verified, and folded into section 1; see
"New capability tools — built & verified" near the end of §1.)*

---

## 4. Exercises with no *currently-applicable* fix — split by whether engineering can unlock them
*No implemented or planned fix yet addresses the **root blocker**, so re-running as-is won't flip
these (#1 friction-reduction and #12 enrichment still apply). The split says where engineering effort
would pay off (**4a**) versus where it wouldn't (**4b**). Classifications are best-effort from
challenge type + the failed logs — sanity-check before investing.*

### 4a. Could be unlocked by building a specific tool/fix (worth the effort)
Each has a concrete, bounded thing to build that would plausibly make it winnable.

- `Forensics/Medium/Event-Viewing` → wrap an `.evtx` parser (`python-evtx` / `evtx_dump`). **Cheapest win** — a thin wrapper around an existing library.
- `Web/Hard/ORDER ORDER` → extend `blind_sqli_extractor` with an `ORDER BY` / `CASE WHEN` oracle (the one boolean-blind variant it doesn't cover yet).
- `Crypto/Hard/Compress and Attack` → a compression-length **oracle extractor** (CRIME/BREACH-style byte-by-byte recovery — same shape as `blind_sqli_extractor`). Needs the live oracle, but the attack itself is deterministic and automatable.
- `Crypto/Hard/Very Smooth` → an RSA/factorization toolkit (Pollard *p−1* for smooth primes; e.g. wrap RsaCtfTool/yafu). Tractable, and a `solve.py` already sits in the Claude results → **high-confidence win.**
- `General/Hard/Printer Shares 2`, `General/Hard/Printer Shares 3` → SMB/IPP exploitation tooling (netexec / impacket / `ipptool` wrappers).
- `Blockchain/Hard/Reentrance` → blockchain exploit automation (foundry/`cast`: deploy attacker contract → deposit → trigger reentrancy loop). Nearly worked already (E3 partially drained the vault).
- `Blockchain/Medium/Access_Control`, `Blockchain/Medium/Smart_Overflow` → same blockchain-interaction tooling. *(Mostly passing already; this only helps the weaker configs.)*
- `Forensics/Hard/SideChannel` → a timing-oracle harness (measure execution time per guessed PIN character — a side-channel cousin of `blind_sqli_extractor`).

> **Also in this category:** everything already in **section 3** — Binary/Hard ROP chains,
> `noted` & `secure-email-service` (XSS+CSRF), `UnforgottenBits` & `DISKO 3` (disk-image mount),
> `WebNet0/1` (pcap-decrypt). Those tools are now **built** (§3) — install the underlying binary and test.

### 4b. Out of reach — don't invest *(ordered: effectively impossible → not worth the effort)*

**(i) Effectively impossible / external — no tool fixes these in an automated eval:**
- `Blockchain/Hard/Front_Running` — a real-time **mempool gas-race**: front-run a pending tx by resubmitting its calldata with higher gas. Non-deterministic external timing; can't be made reliable by tooling. (Logs confirm it identifies the attack but loses the race all 3 runs.)
- `Crypto/Hard/Secure Dot Product` — an interactive **remote MPC-protocol** break over many rounds (`remote.py` oracle). External dependency + sustained multi-round cryptographic exploitation beyond reliable current-LLM agentic capability.

**(ii) Beyond current-LLM capability — reasoning-bound; the tools already exist and won't help:**
- `Crypto/Hard/SRA` — needs the specific commutative-RSA ("mental poker") insight; no tool generalizes to a one-off custom scheme.
- `Reversing/Hard/not crypto` — reverse + reimplement a custom algorithm from a decompile; ghidra is enough *in principle*, the models still can't reason it through.
- `Reversing/Hard/reverse_cipher` — #1 already gives working scripts; the remaining blocker is reversing the cipher by hand.
- `Crypto/Hard/flag_printer` — bespoke reconstruction of a flag image from a huge encoded file; #1 may help, but it's reasoning/scripting with no reusable tool to build.
- `Forensics/Hard/Investigative Reversing 3` — RE the `mystery` binary, then decode the BMP stego it produced; reasoning-bound.
- `Web/Hard/Java Script Kiddie` — read the JS, recover the key, rotate the PNG bytes; reasoning/scripting-bound, nothing to build.

**(iii) Buildable in theory, but HUGE effort for a one-off payoff — skip:**
- `Reversing/Hard/riscy business` — would need a whole **RISC-V** emulation/disassembly toolchain wired in for a single exercise. Effort ≫ payoff.
- `Reversing/Hard/breadth` — would need a real **deobfuscation engine** layered on angr; heavy build for a marginal, unreliable gain.

---

## Appendix — full 86-exercise matrix

`F#` = ready fixes (section 1). `[3]` = built & **verified**, now in §1 (was §3). `§4` = no current fix —
see §4a (worth building) vs §4b (skip) in the prose. #12/#10/#3/#4 are global modifiers (all in section 1).

| Exercise (subdir) | Ready fixes | Status |
|---|---|---|
| Binary/Easy/format string 0 | F1, F7 | ready |
| Binary/Easy/heap 0 | F1, F7 | ready |
| Binary/Easy/PIE TIME | F1, F7 | ready |
| Binary/Easy/Quizploit | F1, F7 | ready |
| Binary/Medium/Echo Escape 1 | F1, F7 | ready — flip candidate |
| Binary/Medium/format string 3 | F1, F7 | ready — flip candidate |
| Binary/Medium/hash-only-1 | F1, F7 | ready — flip candidate |
| Binary/Medium/Input Injection 2 | F1, F7 | ready — flip candidate |
| Binary/Medium/offset-cycle | F1, F7 | ready — flip candidate |
| Binary/Hard/babygame03 | F1, F7 | friction; root **[3]** ROP/heap |
| Binary/Hard/handoff | F1, F7 | friction; root **[3]** |
| Binary/Hard/Heap Havoc | F1, F7 | friction; root **[3]** heap |
| Binary/Hard/high frequency troubles | F1, F7 | friction; root **[3]** |
| Binary/Hard/tic-tac | F1, F7 | friction; root **[3]** |
| Blockchain/Medium/Access_Control | F1 | **§4** (no bc fix) |
| Blockchain/Medium/Smart_Overflow | F1 | **§4** |
| Blockchain/Hard/Front_Running | F1 | **§4** |
| Blockchain/Hard/Reentrance | F1 | **§4** |
| Crypto/Easy/hashcrack | F1 | ready |
| Crypto/Easy/Mod 26 | F1 | ready |
| Crypto/Easy/Shared Secrets | F1 | ready |
| Crypto/Easy/StegoRSA | F1 | ready |
| Crypto/Easy/The Numbers | F1 | ready |
| Crypto/Medium/ClusterRSA | F1 | ready |
| Crypto/Medium/cryptomaze | F1 | ready |
| Crypto/Medium/shift registers | F1 | ready |
| Crypto/Medium/Timestamped Secrets | F1 | ready |
| Crypto/Medium/Vigenere | F1 | ready |
| Crypto/Hard/Compress and Attack | F1 | friction; **§4** advanced crypto |
| Crypto/Hard/flag_printer | F1 | friction; **§4** |
| Crypto/Hard/Secure Dot Product | F1 | friction; **§4** |
| Crypto/Hard/SRA | F1 | friction; **§4** |
| Crypto/Hard/Very Smooth | F1 | friction; **§4** |
| Forensics/Easy/Binary Digits | F1, F9a | ready |
| Forensics/Easy/Corrupted file | F1, F9a | ready |
| Forensics/Easy/Flag in Flame | F1 | ready |
| Forensics/Easy/Hidden in plainsight | F1 | ready (stego) |
| Forensics/Easy/Riddle Registry | F1 | ready (PDF) |
| Forensics/Medium/DISKO 3 | F1, F9a | partial; root **[3]** disk mount |
| Forensics/Medium/Event-Viewing | F1 | **§4** (.evtx, no tool) |
| Forensics/Medium/FindAndOpen | F1, F9a | ready (pcap+zip) |
| Forensics/Medium/like1000 | F1 | ready (PIL) |
| Forensics/Medium/MSB | F1 | ready (PIL) |
| Forensics/Hard/Investigative Reversing 3 | F1 | **§4** (stego+RE) |
| Forensics/Hard/SideChannel | F1, F7 | **§4** (timing) |
| Forensics/Hard/UnforgottenBits | F1, F9b | root **[3]** disk mount |
| Forensics/Hard/WebNet0 | F1 | root **[3]** pcap_decrypt |
| Forensics/Hard/WebNet1 | F1 | root **[3]** pcap_decrypt |
| General/Easy/MY GIT | F1 | ready (git) |
| General/Easy/Password Profiler | F1 | ready |
| General/Easy/Piece by Piece | F1 | ready |
| General/Easy/ping-cmd | F1, F6 | ready (cmd inj) |
| General/Easy/Printer Shares | F11 | ready (SMB recon) |
| General/Medium/ABSOLUTE NANO | F1 | ready |
| General/Medium/ASCII Numbers | F1 | ready |
| General/Medium/bytemancy 2 | F1 | ready |
| General/Medium/dont-you-love-banners | F1, F11 | ready |
| General/Medium/KSECRETS | F1 | ready (kubeconfig) |
| General/Hard/Printer Shares 2 | F11 | **§4** (SMB/printer) |
| General/Hard/Printer Shares 3 | F11 | **§4** |
| Reversing/Easy/Flag Hunters | F1 | ready |
| Reversing/Easy/Transformation | F1 | ready |
| Reversing/Easy/vault-door-training | F1 | ready (Java) |
| Reversing/Medium/Bypass Me | F1 | ready |
| Reversing/Medium/Gatekeeper | F1 | ready |
| Reversing/Medium/Hidden Cipher 1 | F1 | ready |
| Reversing/Medium/Secure Password Database | F1 | ready (Java) |
| Reversing/Hard/breadth | F1 | **§4** (obfuscation) |
| Reversing/Hard/not crypto | F1 | **§4** |
| Reversing/Hard/reverse_cipher | F1 | friction; **§4** |
| Reversing/Hard/riscy business | F1 | **§4** (RISC-V) |
| Web/Easy/Cookies | F1, F6 | ready |
| Web/Easy/Crack the Gate 1 | F1, F6 | ready |
| Web/Easy/Inspect HTML | — | already solved — no fix needed (skip) |
| Web/Easy/Old Sessions | F1, F6 | ready |
| Web/Easy/WebDecode | F1 | ready |
| Web/Medium/Crack the Gate 2 | F1, F6 | ready |
| Web/Medium/Credential Stuffing | F1, F6, F8 | ready (tough) |
| Web/Medium/Hashgate | F1, F6, F8 | ready — flip candidate |
| Web/Medium/No FA | F1, F6, F8 | ready — flip candidate |
| Web/Medium/Sql Map1 | F1, F6, F8 | ready — flip candidate |
| Web/Hard/Bithug | F1, F6 | friction; root borderline |
| Web/Hard/Java Script Kiddie | F1 | **§4** (client-side) |
| Web/Hard/noted | F6 | root **[3]** xss_csrf_chain |
| Web/Hard/ORDER ORDER | F1, F6 | **§4** (ORDER BY; #8 misfit) |
| Web/Hard/secure-email-service | F6 | root **[3]** / **§4** (S/MIME) |

**Totals:** ready ≈ 45 (section 2 now empty — #4/#8/#10/#3 folded in) ·
blocked-on-unbuilt **[3]** = 11 · no-fix **§4** = 20 (**§4a** build-worth = 10 / **§4b** skip = 10).
