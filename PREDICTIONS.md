# Predictions

[README](README.md) · [Benchmark Guide](BENCHMARK_GUIDE.md) · [Code Mode Overview](CODE_MODE_OVERVIEW.md) · [Predictions](PREDICTIONS.md) · [Results](results/README.md) · [Changelog](CHANGELOG.md)

Written on 2026-11-16, before any run with Code Mode on. One early trial, with Code Mode off, informed them and is described below. It is not part of the results.

Writing predictions down first keeps us honest: the results page reports what happened against what we said would happen, including where we were wrong.

## What We Expect

| Task                                      | Expected difference with Code Mode on                                            | Why                                                                                                                                                                                                       |
| ----------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **C0**, one question about one file       | None in the answer. A small fixed cost or saving in how large the session starts | There is one file to read and nothing to batch                                                                                                                                                            |
| **T1**, broken links                      | No material difference in task context. Possibly fewer requests                  | In the early trial with Code Mode off, Claude solved this with a single shell script and the tool output was small. There is almost nothing left for Code Mode to remove                                  |
| **E1**, API change across 36 call sites   | A moderate reduction in requests and task context, or none                       | It depends on whether Claude edits file by file with Code Mode off, or writes a rewrite script                                                                                                            |
| **M1**, aggregate 120 tickets through MCP | A large reduction in task context and requests. Same correct answer              | With Code Mode off, every ticket fetched lands in the conversation, about 30,000 tokens in all, estimated from the ticket data. With it on, a script can fetch and filter them and return only the answer |
| **M2**, triage 120 tickets through MCP    | A small reduction at best. Accuracy may be lower                                 | The tickets have to be read and judged. Returning them all saves little; filtering them in code misses the ones worded without the obvious keywords                                                       |

## M3, Added After the First Opus Runs

Written on 2026-11-16, after the Opus 5.5 runs of the five tasks above and before any run of M3. The table above is left as it was written.

M2 went against its prediction: with Code Mode on, Claude found all nine tickets using about a quarter of the context. It did so by listing every distinct sentence across the tickets, which works only because our tickets were assembled from 31 repeated sentences. M3 asks the same question of the same tickets, reworded so that sentences do not repeat.

| Task                                           | Expected difference with Code Mode on                                                                                                             | Why                                                                                                                                                                          |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **M3**, triage 120 tickets with varied wording | A smaller reduction in task context than M2 showed, or a missed ticket, or both. We expect the Code Mode run to need well over M2's 12,500 tokens | Without repeats to remove, a script has two choices: return most of the ticket text, which saves little, or filter by keywords, which misses the tickets worded without them |

## Things We Do Not Know Yet

- Whether Code Mode scripts can call MCP tools. The text Claude Code shows the model says they can; no run has confirmed it. If they cannot, M1 and M2 show no difference and that becomes the main finding. **Settled on Opus 5.5: they can.** Both MCP tasks ran with Code Mode on, and the server logged all 120 tickets fetched.
- Whether Code Mode makes a session start larger or smaller. C0 measures it.
- Whether Claude starts subagents in any task, and whether that differs between the modes. The numbers include them either way.

## How We Will Call a Difference Real

The rule is stated once, in the README under [How a Difference Is Judged](README.md#how-a-difference-is-judged). In short: both runs must pass, both models must differ in the same direction, and task context or requests must differ by more than 35%. To see how much runs vary by themselves, we repeat C0 and T1 with Code Mode off once each.

## The Early Trial

Before the benchmark took its present form, one trial ran T1 with Code Mode off in the author's everyday Claude Code configuration. Two things from it shaped the design. Claude solved the task with a single shell script. And most of the session's starting context came from the author's own plugins and skills, not from the task. That is why the benchmark now runs in a clean configuration and reports the task's share separately. The trial is not part of the results, and none of its figures are used.

## Claude Code 2.1.326, Added Before Its Round

Written on 2026-11-17, after Claude Code was updated to 2.1.326 and before any run on it. Everything above was written for 2.1.325 and is left as it was. The round repeats the 2.1.325 benchmark unchanged: the same six tasks, four models, two runs of each task in each mode, at medium effort.

According to its changelog, 2.1.326 changes three things a Code Mode session does. The `$` shell helper refuses some values with an error. Permission checks are stricter, so more commands ask or are refused. Auto mode, which every run uses, stops some shell commands that ran before. It also fixes a fault in parallel MCP calls and one in tool search. Nothing else in the benchmark changes.

| What                               | 2.1.325, median of eight runs                                                            | Expected on 2.1.326                                                                                                                                                                                | Why                                                                                                                             |
| ---------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Fixed context**                  | 43,302 tokens with Code Mode off, 30,313 with it on                                      | Code Mode sessions still start about 13,000 tokens smaller. Each mode within 10% of its 2.1.325 figure                                                                                             | None of the listed changes is to the instructions a session starts with                                                         |
| **Runs with Code Mode off**        | Every task within its 2.1.325 range                                                      | No difference beyond the run-to-run noise already seen                                                                                                                                             | The changes are to Code Mode, apart from auto mode, and the tasks with it off use only ordinary reads, edits and shell commands |
| **T1 with Code Mode on**           | 14,697 tokens of task context, 4.5 requests, all eight passed                            | All eight pass. If the `$` helper refuses a value, the transcript shows the error and a second attempt, and requests rise. Task context stays too noisy to call either way                         | This task makes many `$` shell checks inside its scripts, which is where the refusals would land                                |
| **E1 with Code Mode on**           | 14,506 tokens of task context, 5.5 requests, all eight passed                            | All eight pass, with no difference beyond noise                                                                                                                                                    | It edits files through scripts, but the scripts it wrote on 2.1.325 used ordinary file operations                               |
| **M1, totalling through a tool**   | 3,743 tokens with Code Mode on against 53,882 off; all passed                            | The saving holds on every model: at least 80% less task context with Code Mode on in all eight pairs                                                                                               | The parallel-call fix does not change what a script returns, and the fault it fixes did not show on 2.1.325                     |
| **M2 and M3, reading and judging** | M2 9,087 on against 54,052 off; M3 16,165 against 60,860; 14 of 16 Code Mode runs passed | The same pattern: a large reduction with Code Mode on, and failed checks, if any, for the same reasons as before (a keyword filter, or a reading of an ambiguous ticket), not for a missing ticket | The fixed fault mixed up two results arriving in the same millisecond. No 2.1.325 run missed a ticket for that reason           |
| **Stalled runs**                   | None                                                                                     | None. No run stops at a permission question                                                                                                                                                        | The benchmark's launch settings already allow what the tasks need. A stall would be the main finding of this round              |

**How the two versions will be compared.** By model, task and mode, using the same two runs on each version. A difference between versions counts only if it is larger than the gap between the two runs on either version and points the same way on at least three of the four models. Anything smaller is reported as noise. Results from the two versions are never added together.

---

© 2026 Bicameral, LLC. All rights reserved. See [LICENSE](LICENSE).
