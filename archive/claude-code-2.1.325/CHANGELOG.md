> [!NOTE]
> **Archived benchmark.** This is the benchmark as it was published for Claude Code 2.1.325 (benchmark version 0.3.0), archived on 2026-11-17 and kept unchanged. See the [current benchmark](../../README.md) or [all archived benchmarks](../README.md).

# Changelog

[README](README.md) · [Benchmark Guide](BENCHMARK_GUIDE.md) · [Code Mode Overview](CODE_MODE_OVERVIEW.md) · [Predictions](PREDICTIONS.md) · [Results](results/README.md) · [Changelog](CHANGELOG.md)

What changed in this benchmark, newest first. A change to a task, a prompt, the scoring or the way runs are measured makes earlier results not comparable with later ones, so those changes are always listed here and marked.

## Unreleased

No change to any task, prompt, data or launch setting.

### Added

- **A prediction for Claude Code 2.1.326,** in `PREDICTIONS.md`, written after the update and before any run on it, with the rule for comparing two Claude Code versions.
- **A procedure for replacing the current benchmark with a new one,** in `ARCHIVING.md`, with a diagram. A new run is saved in `new_run/`, validated, and promoted only after the current benchmark has been archived whole and the archive verified.
- **`bin/archive.py`:** copies the published benchmark into `archive/`, with every top-level document, its results and its charts; verifies an archive against the commit it came from; and puts a validated new run in place.
- **`bin/validate.py`:** checks that a set of runs is complete and consistent before its results are published.
- **`bin/measure.py --claude-code VERSION` and `--versions`:** report one Claude Code version at a time, so runs on two versions are never added together.
- **`archive/README.md`:** the index of archived benchmarks, linked from the top of the README. None has been archived yet.
- **`bin/publish.py`:** builds the published copy of the benchmark from the last commit, checks it, and commits it to a clone of the public repository as one commit for each publication. The checks cover private files, local links, images and anchors, private details and whether the scripts parse. The working repository now also holds the maintainer's own files, so it is never pushed to a public remote; `ARCHIVING.md` gains "Two Repositories" and "Publishing".
- **`bin/private-files.txt` and `bin/privatelist.py`:** the one list of files that are never archived and never published, and the code that reads it. `bin/archive.py` now skips every file on the list.
- **A pre-push hook, `.githooks/pre-push`,** which refuses every push to a remote other than the private one.
- **A rehearsal for the archive step,** `bin/archive.py create --out`, which builds and verifies an archive in a throwaway folder. `ARCHIVING.md` asks for it, and for a backup of the transcripts, before each new run.

### Documentation

- **The benchmark is not open to changes, and the documents say so.** The licence allows running it as published and publishing results; it no longer allows private changes. Ideas for tests and extensions go through an issue, and the Benchmark Guide gains "Suggesting a Test or an Extension", with what we look for in a test, in place of "Trying Your Own Task". Using the repository to test anything other than Code Mode needs permission, which may be granted in writing. The licence also says that the general method is free to anyone. Two issue forms are added.
- **The guide says how to keep Claude Code versions apart** when measuring, and lists Remote Control among the reasons Code Mode may not start.

## 0.3.0, 2026-11-16

The version behind the published results: four models, 96 runs, on Claude Code 2.1.325. No change to any task, prompt, data or launch setting, so the results of rounds 1 and 2 stay comparable with rounds 3 and 4. The scripts changed only in what they report and save.

### Results

- **Round 4 published:** a second pair of M3 runs on Opus 5.5, typed by `TASKS=M3 bin/run-all.py opus`. Both passed. Every model now has two runs of every test in each mode: 96 runs, of which 94 passed. On Opus 5.5 the M3 prediction of well over 12,500 tokens with Code Mode on held in one run of two: the new run took 16,744, the first 9,747.
- **Round 3 published:** Sonnet 5.5, Haiku 5.5 and Fable 5.2, twice each on all six tasks, 72 runs typed by `bin/run-all.py`. 70 passed. With Opus 5.5 that makes four models and 94 runs, all on Claude Code 2.1.325 at medium effort.
- **M1's saving held on all four models:** 84% to 94% less task context in all eight pairs of runs. Every Code Mode session started about 13,000 tokens smaller on every model.
- **On the file tasks, task context was higher with Code Mode on in all 16 pairs,** mostly within the noise.
- **Two triage runs with Code Mode on failed their checks,** on different models and for different reasons. One was a keyword filter that hid two tickets from the model. The other was a model's reading of an ambiguous ticket, which points at our answer key.
- **Round 2 published:** Opus 5.5 again, twelve runs typed by `bin/run-all.py`, including the first runs of M3. All passed. See the [results page](results/README.md).
- **The script behaves like a person typing.** Fixed context matched round 1 within 29 tokens in every cell.
- **Task context on the file tasks T1 and E1 is reported as too noisy to judge.** Two runs of the same task and mode differed by up to 74%. Round 1's finding that Code Mode doubled T1's task context did not repeat.
- **M3 did not test what it was built to test.** Its varied wording comes from details filled into 31 sentence patterns, and Claude masked the details to find the rare sentences. A triage task with no shared patterns is still needed and is not built.

### Added

- `results/compare.txt`, the output of `bin/measure.py --compare` for rounds 1 and 2.
- `results/context/`, the saved context reports of the scripted runs.
- **A `total_in` column in `bin/measure.py`:** the input tokens the model processed over a whole session, every request's context added up. It is read from the saved transcripts, so rounds 1 and 2 have it too.
- **A `processed` column in `bin/measure.py`:** `total_in` plus every output token, all the tokens the model read or wrote over a session. It is read from the saved transcripts, so every run has it, and `results/measure.txt` and `results/compare.txt` were written again with it.

### Changed

- **Saved context reports leave out the tester's account.** `bin/run.py` now drops the per-item lists of skills and custom agents from the copy it saves in `results/context/`. The totals stay. The twelve reports already saved were rewritten the same way. Nothing about the session changes: the report is saved after the final answer.
- **Saved context reports keep every MCP row.** An earlier change in this section dropped the row for a charting server on the belief that it came from the tester's account. It is built into Claude Code. All 84 saved reports were written again from their transcripts.
- The help text of `bin/run-all.py` said ten runs; it says twelve.
- **The noise rule is applied task by task,** and the README now says so, with the date and the reason. The reading was settled after round 2.

### Documentation

- **The timing of the predictions is stated plainly.** This repository's history begins after the runs, so the documents no longer point to it as evidence of when a prediction was written.
- **Results are reported in tokens processed first.** The README's summary gives tokens processed by model, as totals in tokens with no percentage, and by kind of work, in plain words, followed by the qualifications that go with them. Task context and requests, the measures the rule for a real difference is written in, follow as the detail by test. The results page leads with tokens processed by model, by kind of work and by test; its total input tables and columns were replaced with tokens processed, so it has one such measure. The Benchmark Guide says the same. No run and no figure of task context changed.
- **The Benchmark Guide now offers the twelve runs as two options,** A by hand and B by script, wherever it says how to do them. The script section moved into Part 3 as "Option B: By Script", with a table of its variants, and Part 5 offers both.
- **Results page corrected after review.** M2 with Code Mode on is steadier than first written: one broad tool search accounts for nearly all of the gap between its two runs. The smaller start is traced to built-in tool definitions. The page now says what the git history does and does not prove about when the predictions were written, and that part of every session's start comes from the tester's account.

- **Findings at the top of the README:** what the Opus 5.5 results show, an overall assessment and provisional recommendations, each linked to the evidence. The README's Results section keeps its table and points to them.
- Stale statements corrected: the README's task count and its notes that our results were still to come, its statement that Code Mode does not change the cost of tool definitions, and the Benchmark Guide's cost summary and run count.

## 0.2.0, 2026-11-16

After the first round of runs. **Nothing here changes how a session runs for tasks C0, T1, E1, M1 or M2:** their prompts, settings and data are as they were, so the Opus 5.5 results from the first round stay comparable with later rounds.

### Results

- First results published: Opus 5.5, ten runs, one per task and mode. See the [results page](results/README.md).

### Added

- **Task M3,** the M2 question on tickets reworded so that no sentence repeats. Added because the M2 result depended on repetition in the test data. M2 is kept unchanged. M3's prediction was written before it was run.
- **`bin/run-all.py`,** which runs every task for a model back to back and does the typing. Each run is still an interactive session. For the work folders the benchmark builds, it records the answer to Claude Code's folder-trust question in the benchmark's own configuration.
- **`bin/measure.py --compare`,** which sets repeated runs of the same task, mode and model side by side, and a `typed` column saying whether a run was typed by hand or by the script.
- **A saved context report for each scripted run,** in `results/context/`. The script asks for it after the final answer, so it does not affect the measurements.
- **A guard** that refuses to start a run from inside a Claude Code session, where a run would inherit the outer session's settings.
- **`bin/run.py signin` and `bin/run.py check`,** two setup sessions that send no prompt and record nothing.
- **`bin/clean.py`,** which removes everything the benchmark built.

### Changed

- The run order is Code Mode off first, then on, for every task. The first round was already run that way.
- Work folders moved outside the home folder, and connectors tied to a Claude account are kept out of sessions. Both changes were made before the first recorded run.

### Fixed

- **`bin/measure.py` over-counted requests for Code Mode sessions.** Claude Code saves each tool call a script makes as its own record, and the script counted each as a request to the model. It reported 400 requests for a run that made 5. The script now skips those records and checks its count against the transcript's own record of API requests. All first-round runs were read again from their saved transcripts; none had to be repeated.
- `bin/new-round.py` failed when the repository and the logs were on different disks.

## 0.1.0, 2026-11-16

The first public version. The method and the predictions are published; the runs have not been done, so there are no results yet.

### Benchmark

- Five tasks, each run with Code Mode off and on: C0 (a control), T1 (find broken links in the Fastify docs), E1 (change an API across 36 call sites in a generated Python project), M1 (aggregate 120 support tickets through an MCP server) and M2 (triage those tickets, which needs reading each one).
- Sessions run in work folders outside the repository and outside the home folder, rebuilt before every run, with a clean Claude Code configuration, medium effort, fast mode off, auto permission mode and no memory carried between runs.
- Scoring gives one pass or fail per run. The MCP tasks count only if every ticket was fetched through the tools.
- Measurements come from Claude Code's saved transcripts, a log of every tool run, and the MCP server's own call log. Fixed context is reported apart from task context, and subagents are counted.

### Scripts

- `bin/setup.py` builds the test files, `bin/run.py` does one run and scores it, `bin/measure.py` prints the numbers, `bin/new-round.py` starts a clean set of runs, and `bin/clean.py` removes everything the benchmark built.
- A small MCP server that uses only the Python standard library, in `mcp/`.

### Documentation

- README, Benchmark Guide, Code Mode Overview, Predictions and a results page with empty tables.
- License: all rights reserved, with permission to run the benchmark for your own evaluation.

---

© 2026 Bicameral, LLC. All rights reserved. See [LICENSE](LICENSE).
