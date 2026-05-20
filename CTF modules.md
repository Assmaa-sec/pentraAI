# CTF Modules — hexstrike_server.py


## Classes

### `CTFChallenge` : line 2906
Dataclass representing a single CTF challenge.

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Challenge name |
| `category` | `str` | One of: `web`, `crypto`, `pwn`, `forensics`, `rev`, `general_skills`, `blockchain` |
| `description` | `str` | Challenge description text |
| `points` | `int` | Point value (default 0) |
| `difficulty` | `str` | `easy`, `medium`, `hard`|
| `files` | `List[str]` | Attached challenge files |
| `url` | `str` | Challenge URL if applicable |
| `hints` | `List[str]` | Available hints |

---

### `CTFWorkflowManager` : line 2917
Core workflow engine for CTF challenges. Generates solving plans, tool selections, time estimates, success probabilities, and team strategies per picoCTF category.

Key methods:
- `create_ctf_challenge_workflow(challenge)` : full workflow with tools, strategies, estimated time, success probability, parallel tasks, validation steps
- `create_ctf_team_strategy(challenges, team_size)` : allocates challenges across team members by points-per-hour efficiency
- `_create_advanced_category_workflow(challenge)` :step-by-step workflow with parallel execution flags per category
- `_generate_fallback_strategies(category)` : fallback approaches when primary methods fail
- `_identify_parallel_tasks(category)` : task groups safe to run concurrently
- `_calculate_resource_requirements(challenge)` : CPU/RAM/disk/GPU estimates
- `_predict_expected_artifacts(challenge)` : expected output files/data per category
- `_create_validation_steps(category)` : steps to verify the solution is correct

Supports all 7 picoCTF categories: `web`, `crypto`, `pwn`, `forensics`, `rev`, `general_skills`, `blockchain`

---

### `CTFToolManager` : line 3664
Comprehensive tool registry for CTF challenge solving. Maps tool names to their optimised CLI commands and groups tools by category.

Key methods:
- `get_tool_command(tool, target, additional_args)` : returns the full optimised CLI command for a tool
- `get_category_tools(category)` : returns all tools for a category group
- `suggest_tools_for_challenge(description, category)` : keyword-based tool suggestion from challenge description

Tool categories covered:
- `web_recon`, `web_vuln`, `web_discovery`, `web_params`
- `crypto_hash`, `crypto_cipher`, `crypto_rsa`, `crypto_modern`
- `pwn_analysis`, `pwn_exploit`, `pwn_debug`, `pwn_advanced`
- `forensics_file`, `forensics_image`, `forensics_memory`, `forensics_network`
- `rev_static`, `rev_dynamic`, `rev_unpack`
- `general_skills_encoding`, `general_skills_cli`, `general_skills_networking`
- `blockchain_analysis`, `blockchain_interaction`, `blockchain_decompile`

---

### `CTFChallengeAutomator` : line 4042
Automated challenge solving system. Executes workflow steps, extracts flag candidates from tool output, and generates manual guidance when automation is insufficient.

Key methods:
- `auto_solve_challenge(challenge)` : runs the full automated solve pipeline
- `_execute_parallel_step(step, challenge)` : runs tools concurrently for a workflow step
- `_execute_sequential_step(step, challenge)` : runs tools one at a time
- `_extract_flag_candidates(output)` : regex extraction of `picoCTF{}` and other flag patterns from tool output
- `_validate_flag_format(flag)` : validates a string against known flag formats including `picoCTF{}`
- `_generate_manual_guidance(challenge, result)` : category-specific manual hints when automation fails

---

### `CTFTeamCoordinator` : line 4273
Optimises challenge assignments across CTF team members based on individual skill sets.

Key methods:
- `optimize_team_strategy(challenges, team_skills)` : assigns challenges using a greedy skill-weighted scoring model, produces priority queue and collaboration opportunities
- `_estimate_solve_time(challenge, member_skills)` : estimates solve time with skill bonus
- `_assign_challenges_optimally(member_challenge_scores)` : greedy approximation of optimal assignment

---

## Global Instances (line 5764–5767)

```python
ctf_manager    = CTFWorkflowManager()
ctf_tools      = CTFToolManager()
ctf_automator  = CTFChallengeAutomator()
ctf_coordinator = CTFTeamCoordinator()
```

---

## picoCTF Categories

| Category | Description |
|---|---|
| `web` | Web Exploitation |
| `crypto` | Cryptography |
| `pwn` | Binary Exploitation |
| `forensics` | Forensics |
| `rev` | Reverse Engineering |
| `general_skills` | General Skills |
| `blockchain` | Blockchain / Smart Contract Exploitation |

## Flag Format

All flag extraction and validation targets `picoCTF{...}` as the primary format.
