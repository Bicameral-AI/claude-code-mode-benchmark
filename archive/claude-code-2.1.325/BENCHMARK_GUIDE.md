> [!NOTE]
> **Archived benchmark.** This is the benchmark as it was published for Claude Code 2.1.325 (benchmark version 0.3.0), archived on 2026-11-17 and kept unchanged. See the [current benchmark](../../README.md) or [all archived benchmarks](../README.md).

# Benchmark Guide: Run It Yourself

[README](README.md) · [Benchmark Guide](BENCHMARK_GUIDE.md) · [Code Mode Overview](CODE_MODE_OVERVIEW.md) · [Predictions](PREDICTIONS.md) · [Results](results/README.md) · [Changelog](CHANGELOG.md)

A step-by-step walkthrough. Every command is shown exactly as you type it.

- **Time:** about half an hour per model by hand, or a few minutes of your attention if you let the script do the typing. On Opus 5.5 the first ten sessions took under six minutes of running time in all.
- **Cost:** our twelve runs on Opus 5.5 in round 2 cost $4.92. See [What It Costs](#what-it-costs) below.
- **Terminals:** one terminal window is enough. Every command in this guide is typed in the repository's top folder. A session runs inside that same window, and you are back at the prompt when it ends.

<details open>
<summary><strong>Contents</strong></summary>

- [What It Costs](#what-it-costs)
- [At a Glance](#at-a-glance)
- [What You Need](#what-you-need)
- [Part 1: Set Up Once](#part-1-set-up-once)
- [Part 2: One Run, Step by Step](#part-2-one-run-step-by-step)
  - [Code Mode Off and On Look Different](#code-mode-off-and-on-look-different)
- [Part 3: All Twelve Runs](#part-3-all-twelve-runs)
  - [Option A: By Hand](#option-a-by-hand)
  - [Option B: By Script](#option-b-by-script)
- [Part 4: Collect the Numbers](#part-4-collect-the-numbers)
- [Part 5: Test Another Model](#part-5-test-another-model)
- [The Six Tasks](#the-six-tasks)
  - [What an MCP Run Prints](#what-an-mcp-run-prints)
- [How Runs Are Kept Comparable](#how-runs-are-kept-comparable)
- [Suggesting a Test or an Extension](#suggesting-a-test-or-an-extension)
- [Reference](#reference)
  - [Models and Effort](#models-and-effort)
  - [Settings](#settings)
  - [Start Over](#start-over)
  - [What You Might See](#what-you-might-see)
  - [If Code Mode Does Not Start](#if-code-mode-does-not-start)
  - [Screenshots for a Post](#screenshots-for-a-post)
  - [After the Test](#after-the-test)

</details>

## What It Costs

Measured on Opus 5.5 in our second round, one run each, from the figure Claude Code records for each session. The totals for the other models follow, and `bin/measure.py` gives you the same figures for your own runs.

| Task                                      | Code Mode off | Code Mode on |
| ----------------------------------------- | ------------- | ------------ |
| C0 Control                                | $0.16         | $0.15        |
| T1 Find broken links                      | $0.31         | $0.27        |
| E1 Change an API across 36 call sites     | $0.31         | $0.36        |
| M1 Aggregate 120 tickets through MCP      | $0.87         | $0.20        |
| M2 Triage 120 tickets through MCP         | $0.84         | $0.26        |
| M3 Triage 120 tickets with varied wording | $0.90         | $0.29        |
| **The twelve runs above, Opus 5.5**       | **$4.92**     |              |
| **Sonnet 5.5, twelve runs**               | **$2.38**     |              |
| **Haiku 5.5, twelve runs**                | **$0.20**     |              |
| **Fable 5.2, twelve runs**                | **$9.33**     |              |

The figures for Sonnet 5.5, Haiku 5.5 and Fable 5.2 are half of what their 24 runs cost in our third round. Our first round, the Opus 5.5 runs without M3, cost $3.97. Haiku 5.5's recorded costs are a cent or two a run, and we have not checked any of these figures against a price list.

What to expect:

- **Twelve sessions per model.** Each session pays for its starting context once, then for the task.
- **The MCP tasks with Code Mode off should cost the most,** because all 120 tickets pass through the conversation. That is the cost the benchmark is built to measure.
- **The model matters more than anything else.** Opus costs more per token than Sonnet, so a second model does not double the bill.
- **On a subscription,** the runs draw on your plan's usage like any other session. The dollar figure is the one Claude Code records for the session, which is a guide to size, not an invoice.
- **The first session of each kind costs more.** Claude Code caches the start of a conversation, and the first `off` session and the first `on` session each have to fill that cache. A later run of the same kind is cheaper. So the cost of a single run depends partly on what you ran just before it.

To keep spending in check, do the first pair of Part 3 first, the control task C0 off and then on, and look at what it cost before doing the rest. It is the cheapest pair, so it shows the routine and the cost of a session's starting context. The MCP tasks cost more, as above.

```bash
bin/run.py C0 off opus
bin/run.py C0 on opus
bin/measure.py
```

By script, the same pair is `TASKS=C0 bin/run-all.py opus`.

`bin/measure.py` shows `cost_usd` for each run and a total at the end.

## At a Glance

The whole benchmark, for one model. Each step is explained below.

**1. Set up once.** Both options below need this first.

```bash
git clone https://github.com/Bicameral-AI/claude-code-mode-benchmark.git
cd claude-code-mode-benchmark
bin/setup.py                 # build the test files
bin/run.py signin            # sign in to the clean configuration, then /exit
bin/run.py check             # see the Code Mode banner, type /mcp, then /exit
```

**2. Do the twelve runs, by hand or by script.** Twelve runs is six tasks (C0, T1, E1, M1, M2, M3) times two modes (Code Mode off, then on). Pick one option. The two give the same records and can be mixed: `bin/measure.py` reads both, and its `typed` column says which run was which.

|             | Option A: by hand                                                       | Option B: by script                                                                   |
| ----------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Command     | Twelve commands, `bin/run.py <task> <off or on> opus`, one session each | One command, `bin/run-all.py opus`, which does the same twelve runs in the same order |
| What you do | In each session, paste the prompt, wait for the answer and type `/exit` | Nothing: leave the terminal alone                                                     |
| Best for    | A first look, screenshots, seeing what a session does                   | A whole model, several models, repeats                                                |
| Details     | [Option A: By Hand](#option-a-by-hand) lists all twelve commands        | [Option B: By Script](#option-b-by-script) covers models, tasks, repeats and effort   |

**3. Collect the numbers.**

```bash
bin/measure.py | tee results/measure.txt
```

Every task runs with Code Mode off first, then on. Each run is scored and recorded automatically when the session ends. The method behind the benchmark is summarised in the [README](README.md#methodology).

## What You Need

- Claude Code v2.1.323 or later, installed with the native installer.
- A Claude subscription or Console account. Code Mode does not work through Amazon Bedrock, Google Cloud, Microsoft Foundry or a gateway.
- A terminal. Code Mode does not work in the VS Code panel, the Desktop app or with `claude -p`.
- `git` and `python3`.

Tested on macOS. The scripts should work on Linux and WSL; they have not been tried there.

The full list of requirements is in the [Code Mode docs](https://code.claude.com/docs/en/code-mode#requirements).

## Part 1: Set Up Once

1. Open a terminal and check your Claude Code version:

   ```bash
   claude --version
   ```

   It must show `2.1.323` or higher. If it is lower, type `claude update` and check again.

2. Download this repository, which holds the benchmark's scripts and prompts, and move into it:

   ```bash
   git clone https://github.com/Bicameral-AI/claude-code-mode-benchmark.git
   cd claude-code-mode-benchmark
   ```

   Stay in this folder for everything that follows. This is the only thing you download by hand.

3. Build the test files:

   ```bash
   bin/setup.py
   ```

   It downloads Fastify, so allow up to a minute. You should see:

   ```text
   fetching fastify/fastify at 467972380963
   fastify: 392 files, 11 broken links
   invoice: 36 call sites, 39 tests; starting files fail 3, a correct change passes all: yes
   empty: a folder with one README, for the MCP tasks
   work folders ready under ...
   ```

   The first time, it also prints a reminder to sign in, which is the next step. Any other numbers mean the files do not match the published test. What it builds goes outside this repository: the starting files under `~/.cache/claude-code-mode-benchmark`, and the folders sessions run in under `/var/tmp`, so that a test session can see neither the checker and the answers nor your own `CLAUDE.md`.

4. Sign in to the benchmark's clean configuration. The benchmark does not use your everyday Claude Code setup, so it needs its own sign-in, once:

   ```bash
   bin/run.py signin
   ```

   Claude Code opens as if newly installed, because this configuration is new. The first screen asks you to choose a colour theme; pick any. It then asks you to sign in and may show a few notes to accept. If it goes straight to the prompt without asking you to sign in, your computer has remembered an earlier sign-in, which is fine; type `/login` only if it says you are not signed in. When you reach the prompt, type:

   ```text
   /exit
   ```

   No task prompt was sent, so nothing is recorded.

5. Check that Code Mode starts:

   ```bash
   bin/run.py check
   ```

   Answer what it asks:
   - If it asks whether you trust the folder, choose yes.
   - When it asks about Code Mode, choose **Yes, turn on Code Mode**. Claude Code restarts.
   - It may ask a second question about using Code Mode with auto permission mode. Accept that too.
   - You are asked only the first time. Later Code Mode sessions start without the question.

   Near the top of the session you should see:

   ```text
   Code Mode (experimental) is on · this session can be resumed only with Code Mode on
   ```

   If you are not sure, type `/status`: it says whether Code Mode is on, and the reason if it is not.

   Then type `/mcp` and check that `records` is listed as connected. You may also see `easel`, which is built into Claude Code; nothing else should be listed. Type `/exit`. If you see `Code Mode (experimental) isn't available` instead, go to [If Code Mode Does Not Start](#if-code-mode-does-not-start).

Setup is done.

## Part 2: One Run, Step by Step

One run is one command and three things to do inside the session. This walkthrough is the first run you will do for real: task C0, the control, on Opus, with Code Mode off. It is run 1 of the twelve in Part 3. C0 is the shortest task, so it is a cheap way to see the whole routine once.

> [!WARNING]
> Do not fix or change anything Claude reports, and do not ask Claude to. The broken links in T1 and the failing tests in E1 are there on purpose, and every run starts again from the same files.

1. Start the run:

   ```bash
   bin/run.py C0 off opus
   ```

   It rebuilds the task's work folder, puts the task prompt on your clipboard, and opens Claude Code. You should see, before the session opens:

   ```text
   C0: Control: one question, one file
   Code Mode off, opus, effort medium, fast mode off, clean configuration
     claude --mcp-config <path> --strict-mcp-config --model opus --effort medium --permission-mode auto
   work folder rebuilt: <path>
   the task prompt is on your clipboard: paste it, wait for the answer, then type /exit
   ```

   The `<path>` parts are folders on your machine, and the `claude` line is the command the script is about to run.

2. In the session, paste the prompt (Cmd+V, or Ctrl+Shift+V on Linux) and press Enter. The prompt for C0 is one line:

   ```text
   Read docs/Reference/LTS.md and tell me in two sentences how long a Fastify major version is supported. Change no files.
   ```

3. Wait until Claude finishes. If Claude asks permission to run something, approve it. Type nothing else: any extra message changes the numbers. C0 is over in seconds, and Claude's answer is two sentences about how long a Fastify major version is supported.

4. Type `/exit` and press Enter.

The run is then scored and recorded automatically. You should see this for a passing run:

```text
C0 [opus off]  PASS
   the answer mentions the six-month support period
   files changed: 0 []

recorded. See all runs so far with: bin/measure.py
```

The first line is the verdict. The two lines under it say what the checker looked at: that Claude's answer states the six-month support period, and that no file in the work folder changed. A FAIL prints the same lines with the failing one saying what was missing.

That is one run done. If you leave a session without sending the prompt, nothing is recorded and you can simply run the command again.

If a run fails or is interrupted, run the same command again. Both attempts stay in the `bin/measure.py` table as separate rows, in the order you ran them, so note which one you mean to report.

### Code Mode Off and On Look Different

Code Mode is set fresh for every session by `bin/run.py`. Having confirmed it once does not turn it on.

- **In an `off` run** there is no Code Mode line near the top, and you see Claude's tool calls one at a time.
- **In an `on` run** the line `Code Mode (experimental) is on` appears near the top. You still see the tool calls, not the code; press Ctrl+O and expand a row marked **Code** to read the JavaScript.

## Part 3: All Twelve Runs

Six tasks, each with Code Mode off and then on, make twelve runs. You can do them by hand or let a script do them; both produce the same records, and you can mix them. Every task runs with Code Mode off first, then on, so each pair looks the same and it is hard to lose your place.

|             | Option A: by hand                                     | Option B: by script                    |
| ----------- | ----------------------------------------------------- | -------------------------------------- |
| Command     | `bin/run.py <task> <off or on> <model>`, twelve times | `bin/run-all.py <model>`, once         |
| What you do | Steps 2 to 4 of Part 2 in each session                | Nothing                                |
| Best for    | A first look, screenshots, seeing what a session does | A whole model, several models, repeats |

### Option A: By Hand

Do these in this order, one command at a time, and do steps 2 to 4 of Part 2 inside each session.

```bash
bin/run.py C0 off opus
bin/run.py C0 on opus

bin/run.py T1 off opus
bin/run.py T1 on opus

bin/run.py E1 off opus
bin/run.py E1 on opus

bin/run.py M1 off opus
bin/run.py M1 on opus

bin/run.py M2 off opus
bin/run.py M2 on opus

bin/run.py M3 off opus
bin/run.py M3 on opus
```

To see how much two runs of the same thing differ, repeat two of them once more. This is optional, and it is what lets you say whether a difference is real:

```bash
bin/run.py C0 off opus
bin/run.py T1 off opus
```

How each task ends, so you know when to stop waiting:

| Task | Claude's last message                          | Running time on Opus 5.5, off then on |
| ---- | ---------------------------------------------- | ------------------------------------- |
| C0   | Two sentences about Fastify's support policy   | 3 and 5 seconds                       |
| T1   | The number of broken links it found            | 47 and 42 seconds                     |
| E1   | The number of call sites it changed            | 33 and 25 seconds                     |
| M1   | The number of matching tickets and their total | 69 and 14 seconds                     |
| M2   | The number of matching tickets                 | 71 and 29 seconds                     |
| M3   | The number of matching tickets                 | 70 and 31 seconds                     |

These are single runs, from our first round for C0 to M2 and our second for M3; yours will differ.

### Option B: By Script

`bin/run-all.py <model>` does the same twelve runs in the same order, with nobody typing. It opens each session in turn, pastes the prompt, waits until the saved transcript shows that Claude has finished, types `/exit`, scores the run and moves on. Each run is still an ordinary interactive Claude Code session, which Code Mode requires; the script only does the typing. Every run rebuilds its work folder and starts a new session, so nothing carries over between runs or between models.

```bash
bin/run-all.py opus
```

Put settings in front of the command. They can be combined, for example `REPEAT=2 TASKS=T1,E1 bin/run-all.py sonnet`.

| Command                                        | What it does                                                                                                                                                                                         |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bin/run-all.py opus`                          | All six tasks, off then on: twelve runs                                                                                                                                                              |
| `bin/run-all.py sonnet claude-haiku-5-5 fable` | One model after another, in the order typed                                                                                                                                                          |
| `TASKS=M3 bin/run-all.py opus`                 | Only task M3, off then on                                                                                                                                                                            |
| `TASKS=M1,M2 bin/run-all.py opus`              | Only the tasks listed                                                                                                                                                                                |
| `REPEAT=2 bin/run-all.py sonnet`               | The whole set twice. The order is model, then repeat, then task, then mode, so each model finishes all its repeats before the next model starts                                                      |
| `EFFORT=high bin/run-all.py fable`             | Another effort level. `EFFORT` applies to the whole command, so models at different effort levels need separate commands, which can be joined with `&&`. Compare off with on at the same effort only |

What to know:

- **Run it from an ordinary terminal window,** not from inside a Claude Code session. A session started from inside another one inherits its settings, so the scripts refuse to run there.
- **Leave the terminal alone while it works.** You will see each session on screen. If one asks a question, you can still answer it.
- **It stops at the first run that does not finish properly,** and prints the command to repeat that run by hand.
- **A run is given 30 minutes** before the script gives up on it. Change that with `BENCH_TIMEOUT_MINUTES=60`.
- **Do the setup first,** as Option A needs too: `bin/setup.py`, `bin/run.py signin` and `bin/run.py check`. The script cannot answer the first-time questions for you.
- **It answers one question for you.** Claude Code asks whether you trust a folder the first time it opens one. For the work folders the benchmark builds, the script records a yes in the benchmark's own configuration, never in yours. A run typed by hand still shows you the question.
- **It saves the context report for every run.** After Claude's final answer the script types `/context` and keeps what it prints as a text file in `results/context/`, named by task, model and mode. It asks after the last request to the model, so the report does not change any measured number.

To check that a scripted run behaves like one typed by hand, or to see how much two runs of the same thing differ, run a model a second time and compare:

```bash
bin/run-all.py opus
bin/measure.py --compare
```

`--compare` lists every task, mode and model that has been run more than once, with the first run beside the latest and the change in each number. The `typed` column in the main table says whether a run was typed by hand or by the script.

Our first round, on Opus 5.5, was typed by hand. The script was then tested against a stand-in for Claude Code, and our second round repeated the Opus 5.5 runs with the script typing: twelve runs took about thirteen minutes and all passed. Every session started at the same size as its hand-typed twin, within 29 tokens. Our third round used it for Sonnet 5.5, Haiku 5.5 and Fable 5.2: 72 runs in one hour, with no stall and no change to the script. The [results page](results/README.md#run-log) says which rounds were typed by whom.

## Part 4: Collect the Numbers

When the runs are done, type:

```bash
bin/measure.py | tee results/measure.txt
```

It prints a table with one row per run, then a block of detail for each.

If you update Claude Code between runs, keep the versions apart. `bin/measure.py` reports every run on your machine in one table, and Code Mode changes from release to release. `bin/measure.py --versions` lists the versions you have runs for, and `bin/measure.py --claude-code 2.1.325` reports one of them.

| Column      | Meaning                                                                                                                           |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `result`    | PASS or FAIL from the checker                                                                                                     |
| `requests`  | Calls to the model, including any subagents                                                                                       |
| `tools_run` | Tools Claude Code actually ran, including those run from Code Mode scripts                                                        |
| `scripts`   | Pieces of Code Mode JavaScript run. Always 0 with Code Mode off                                                                   |
| `subagents` | Subagents the session started                                                                                                     |
| `seconds`   | From your prompt to the last reply                                                                                                |
| `fixed_ctx` | Tokens sent in the first request: the system prompt, tool definitions and your prompt                                             |
| `task_ctx`  | Tokens in the last request plus its reply, minus `fixed_ctx`. Main conversation only: subagent work shows in `requests`, not here |
| `peak_ctx`  | The largest context of any request, in tokens                                                                                     |
| `total_in`  | Input tokens the model processed over the whole session: every request's context added up, cached or not, subagents included      |
| `processed` | `total_in` plus every output token: all the tokens the model read or wrote over the session. The headline measure in our results  |
| `cost_usd`  | What Claude Code recorded as the session's cost                                                                                   |

Start with `processed`, compared between the two modes of the same task: it is the figure our results lead with, and it already includes the smaller start of a Code Mode session, because the start is sent with every request. Then look at the detail that explains it: `task_ctx` says whether the conversation itself grew, `requests` how many times the start was sent, and `result` whether the answer was right. A lower `processed` counts only if both runs passed. `fixed_ctx` shows how much smaller or larger the session started. The README says [how a difference is judged](README.md#how-a-difference-is-judged); that rule is written in `task_ctx` and `requests`.

`processed` depends on your own setup as well as on Code Mode: your session's start can differ from ours, and the difference is repeated in every request. Compare your two modes with each other. To set a task beside ours, use `task_ctx`. Most of `processed` is read from the prompt cache at a lower rate, so it is not cost.

Things that look odd and are not:

- **`fixed_ctx` differs between the two modes.** With Code Mode on, Claude is given a script-running tool and far fewer built-in tool definitions, so the session starts smaller. In our runs the built-in definitions took 16.3k tokens with Code Mode off and 3.6k with it on. The benchmark's MCP tools are not part of the difference: Claude Code already holds them back until they are needed, in both modes.
- **`tools_run` can be far higher with Code Mode on.** A script can make hundreds of small tool calls, such as one check per link, where a person or a shell script would make a handful. Those calls do not pass through the conversation, so the numbers to compare are `processed` and `task_ctx`, not `tools_run`.
- **A Code Mode run is not always smaller.** What a script returns goes into the conversation. A script that returns a lot can add more than the same task done with one shell command, so `task_ctx` can be higher with Code Mode on.
- **`cost_usd` can be higher for the run with the smaller context.** See the note on caching under [What It Costs](#what-it-costs). Judge on `processed`, context and requests first.
- **`tools_run` counts tools run from inside scripts,** so an `on` run shows the tools its scripts used, and `scripts` shows how many scripts there were.

## Part 5: Test Another Model

Do Part 3 again with the other model's name in place of `opus`, by either option. The names are in [Models and Effort](#models-and-effort).

```bash
# Option A: by hand, for example Sonnet
bin/run.py C0 off sonnet
bin/run.py C0 on sonnet
# ...and so on through T1, E1, M1, M2 and M3

# Option B: by script, one or several models
bin/run-all.py sonnet
bin/run-all.py sonnet claude-haiku-5-5 fable
```

`bin/measure.py` lists every run so far, grouped by task and model.

## The Six Tasks

| Task   | What Claude is asked to do                                                                      | What a pass needs                                                                       |
| ------ | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **C0** | Answer one question about one file in Fastify                                                   | The answer states the six-month support period, and no file changes                     |
| **T1** | Find the broken local links across Fastify's 47 Markdown files                                  | Exactly the 11 known broken links in `answer.tsv`, and no other file changed            |
| **E1** | Rename `format_amount` to `format_money` and make `currency` keyword-only, across 36 call sites | All 39 original tests pass, no use of the old name is left, and the tests are untouched |
| **M1** | Find the open Atlas tickets among 120 held by the `records` MCP server                          | The 7 known tickets and their total, and all 120 tickets fetched through the tools      |
| **M2** | Find the tickets where the customer was really charged more than once                           | The 9 known tickets, and all 120 tickets fetched through the tools                      |
| **M3** | The same question as M2, on tickets reworded so that no sentence repeats                        | The same 9 tickets, and all 120 tickets fetched through the tools                       |

What each one is for:

- **C0** is the control. With nothing to save, it shows what Code Mode costs.
- **T1** is work the shell can already script. We expect little difference.
- **E1** is a change repeated across many files, using Claude Code's built-in tools. The call sites are written eight different ways, so one search-and-replace does not do it.
- **M1** is many calls to a tool the shell cannot reach, where only a total is needed. It is built to favour Code Mode.
- **M2** makes the same calls, but each ticket has to be read and judged. The tickets that count are worded without the obvious keywords, and other tickets use those keywords about something else, so filtering in code should miss some.
- **M3** asks M2's question of the same tickets with wording that does not repeat. It was added after the first results, when Claude solved M2 by listing each distinct sentence once: the original tickets are built from 31 sentences, the reworded ones from 875. Those 875 come from 31 patterns with details filled in, and Claude found the patterns: see [what the M3 result shows](results/README.md#what-the-m3-result-does-and-does-not-show).

The prompts are in `tasks/`. They say what to produce, never how.

### What an MCP Run Prints

M1, M2 and M3 print more than C0, because the checker also confirms that Claude fetched every ticket through the tools. This is what a passing M1 run prints. The ticket numbers will match; the call counts are the least a valid run can make, and yours depend on what Claude chose to do:

```text
M1 [opus off]  PASS
   expected 7 tickets totalling 1325, answered 7 totalling 1325
   missed []  wrong extra []
   MCP calls the server received: {'list_tickets': 3, 'get_ticket': 120}
   tickets fetched through the tools: 120 of 120, from 1 server process(es)
   other files changed: 0 []

recorded. See all runs so far with: bin/measure.py
```

If the line about tickets fetched says `NOT A VALID RUN`, the answer may be right but the tickets were not all read through the tools, so the run counts as a fail.

## How Runs Are Kept Comparable

`bin/run.py` sets these for every session, in both modes:

| Setting                                                                               | Why                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A clean Claude Code configuration                                                     | Your local plugins, hooks, settings and memory files would otherwise decide most of the context a session starts with. Skills and plugins synced to your Claude account still load           |
| A work folder outside this repository and outside your home folder, rebuilt every run | Each run starts from identical files, a session cannot find the checker or the answers, and Claude Code does not load your own `CLAUDE.md`, which it reads from every folder above a session |
| Only the benchmark's MCP server                                                       | Connectors tied to your Claude account are left out, so both modes and all readers have the same tools                                                                                       |
| Medium effort and the model you name                                                  | So that runs differ only in Code Mode                                                                                                                                                        |
| Fast mode off                                                                         | It changes speed and cost                                                                                                                                                                    |
| Auto memory off                                                                       | So that nothing learned in one run reaches the next                                                                                                                                          |
| The `records` MCP server connected, for every task                                    | Both modes start from the same tools                                                                                                                                                         |
| A logger called before every tool                                                     | It counts tools the same way in both modes, including tools run from Code Mode scripts                                                                                                       |
| Auto permission mode                                                                  | So that you are not approving every step. See [Settings](#settings) if auto mode is not available to you                                                                                     |

## Suggesting a Test or an Extension

The benchmark is published to be run and checked as it stands. It is not open to changes. The [licence](LICENSE) lets you run it as published and publish the results you get; it does not let you alter it or add to it. That is what keeps one person's results comparable with another's.

**If you have an idea, open an issue:** https://github.com/Bicameral-AI/claude-code-mode-benchmark/issues. That covers another test, a kind of work the six tests miss, a model or setting we should include, a measure we do not report, or a fault in a test or its answer key. We read every one and decide what goes into a later version of the benchmark.

A request we can act on says:

- **What you want measured,** and why the current six tests do not show it.
- **For a new test:** what Claude would be asked, what the right answer is, and how a script could check it.
- **What you expect it to show** with Code Mode off and with it on.
- **Anything you have already seen** that prompted the idea, such as a result from your own run.

What we look for in a test, most of it learned from tests of ours that went wrong:

- **The right answer is known exactly and a script can check it.** Each planted answer is read for a second meaning; one of ours was fairly read two ways, and a run failed its check for it.
- **The prompt says what to produce and where, and nothing about how.** A prompt that says how to do the job measures obedience.
- **The work is something the shell cannot do in one script.** Where it can, Claude writes that script with Code Mode off, and there is nothing left to compare.
- **Test data has no pattern a script can exploit.** Generated text repeats itself in ways a model finds. Masking names, dates and numbers must not reduce the number of distinct sentences.
- **It fits the smallest context window among the models it will run on.**
- **What it should show is written down before it is first run.**

**To use this repository to test something else,** such as another feature, another tool or one model against another, ask first in the same way. The licence covers the scripts, tasks, prompts, data and documents here; say in the issue what you want to test and how you would use them. Permission may be granted in writing; opening an issue is a request, not permission. The general idea of running a task with a feature off and then on is nobody's property, and you are free to build your own from nothing.

What needs no request, because it is running the benchmark as published: any of the four models, another effort level, repeated runs, by hand or by script, and the settings listed under [Settings](#settings).

## Reference

Look-ups you need only some of the time.

### Models and Effort

Code Mode works with four models.

| Model      | Name to type       |
| ---------- | ------------------ |
| Opus 5.5   | `opus`             |
| Sonnet 5.5 | `sonnet`           |
| Fable 5.2  | `fable`            |
| Haiku 5.5  | `claude-haiku-5-5` |

`opus`, `sonnet` and `fable` are aliases for the latest model in that family, so the model behind a name can change over time. A full model name such as `claude-sonnet-5-5` also works. `bin/measure.py` prints the exact model each run used; report that, not the alias.

Compare off with on for the same model and the same effort level. Never set one model's "off" against another model's "on".

### Settings

Put these in front of the command to change how a run is done. Use the same settings for both runs of a pair.

| Setting                                          | Effect                                                                                                                                                                         |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `EFFORT=high bin/run.py M1 off opus`             | Another effort level. The default is medium                                                                                                                                    |
| `PERMISSION_MODE=default bin/run.py M1 off opus` | Ask before each action, for accounts without auto mode. Answer prompts promptly, because waiting time counts                                                                   |
| `BENCH_CONFIG=own bin/run.py M1 off opus`        | Use your everyday Claude Code configuration. Only for when the clean one will not start; your numbers will then depend on your own setup                                       |
| `DRY_RUN=1 bin/run.py M1 off opus`               | Show the command that would run, without starting anything                                                                                                                     |
| `BENCH_WORK=/some/folder bin/setup.py`           | Put the work folders somewhere else. The folder must have no `CLAUDE.md` in any folder above it; the scripts stop and say so if it has. Use the same setting for every command |

Anything typed after the model name is passed on to `claude`.

### Start Over

To set aside the runs so far and begin a clean set, type:

```bash
bin/new-round.py
```

From then on `bin/measure.py` reports only the runs you do after it. Do this whenever the scripts or tasks have changed, so that old and new runs are not mixed.

To go all the way back to a fresh download, including the test files and the benchmark's sign-in, use `bin/clean.py --yes` and then start again from `bin/setup.py`.

### What You Might See

| You see                                                  | What it means                                                                                                                                |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| A theme picker and first-run screens                     | The benchmark's clean configuration is being used for the first time. Go through them once                                                   |
| No request to sign in                                    | Your computer remembered an earlier sign-in for this configuration. Nothing to do                                                            |
| `/mcp` lists `records` and `easel`                       | Correct. `records` is the benchmark's server and `easel` is built into Claude Code                                                           |
| `/mcp` lists all your usual servers                      | You are in your everyday Claude Code, not a benchmark session. Type `/exit` and start the run with `bin/run.py`                              |
| No Code Mode line in an `off` run                        | Correct. Code Mode is off for that session                                                                                                   |
| No Code Mode question in a later `on` run                | Correct. You are asked only once                                                                                                             |
| "No task prompt was sent in that session" after you exit | The session ended without the task prompt, so nothing was scored or recorded. Run the command again                                          |
| A run finishes in seconds                                | Normal for the control task, and for any task Claude solves with one script                                                                  |
| FAIL on a run where Claude seemed to do the work         | Read the lines under the verdict: they say what was missing or changed. A run also fails if Claude changed a file it was told to leave alone |

Do not use `claude --continue`, `claude --resume` or plain `claude` for a benchmark run. Only `bin/run.py` sets the clean configuration, the model, Code Mode and the task's files, and every run must be a new session.

### If Code Mode Does Not Start

`Code Mode (experimental) isn't available` near the top of the session means Claude Code started without it. The reason is on the same line.

| Cause                                                         | What to do                                                               |
| ------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `DISABLE_TELEMETRY` or `DO_NOT_TRACK` is set in your shell    | Unset it for the test, in that terminal window                           |
| Remote Control is on | Nothing, normally: the benchmark turns it off in each work folder's settings. If the line still names it, a managed setting or a `--settings` flag of your own is turning it back on; remove that for the test |
| An API key helper, a gateway or a custom `ANTHROPIC_BASE_URL` | Sign in directly, or set `ANTHROPIC_API_KEY`                             |
| Agent teams or OpenTelemetry export is on                     | Unset the variable for the test                                          |
| The model is not one of the four above                        | Name a supported model                                                   |
| The version is older than v2.1.323                            | Type `claude update`                                                     |
| It says it is not open to your account yet                    | Check your connection and try again; if it stays, try `BENCH_CONFIG=own` |

The [troubleshooting table in the docs](https://code.claude.com/docs/en/code-mode#code-mode-doesnt-start) covers the rest.

If Claude reports that a tool call was refused because of a hook, that is the benchmark's tool logger failing. Run `bin/setup.py` again to rebuild it.

### Screenshots for a Post

The numbers do not need screenshots, and runs typed by the script already save the `/context` report for each run as text in `results/context/`.

If you want pictures, take them in a run typed by hand: type `/context` after the answer and take a screenshot. Do not type `/context` before pasting the prompt, because its output becomes part of the conversation and makes the session start larger. To see the JavaScript Claude wrote in a Code Mode run, press Ctrl+O and expand a row marked **Code**.

Save pictures in `results/screenshots/`, named by task, model and mode, such as `M1-opus-off-end.png`. With the clean configuration there is little of your own setup on screen, but check each picture before posting.

### After the Test

- Put back anything you unset for the test, such as `DISABLE_TELEMETRY`.
- To remove everything the benchmark built and recorded, type `bin/clean.py` to see the list and `bin/clean.py --yes` to remove it. It keeps your screenshots. Your sign-in for the benchmark may stay in your system's keychain; type `/logout` in a benchmark session first if you want that gone too.
- A session started with Code Mode on can be resumed only with Code Mode on.

---

© 2026 Bicameral, LLC. All rights reserved. See [LICENSE](LICENSE).
