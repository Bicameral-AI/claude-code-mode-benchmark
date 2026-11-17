> [!NOTE]
> **Archived benchmark.** This is the benchmark as it was published for Claude Code 2.1.325 (benchmark version 0.3.0), archived on 2026-11-17 and kept unchanged. See the [current benchmark](../../../README.md) or [all archived benchmarks](../../README.md).

# Results

[README](../README.md) · [Benchmark Guide](../BENCHMARK_GUIDE.md) · [Code Mode Overview](../CODE_MODE_OVERVIEW.md) · [Predictions](../PREDICTIONS.md) · [Results](README.md) · [Changelog](../CHANGELOG.md)

> [!IMPORTANT]
> **Status: four models done, two runs per task and mode.** Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.2 have each been run twice on all six tasks. Of 96 runs, 94 passed their checks. Each figure rests on two runs, so read it as a pair of samples, not a settled value.

How the numbers are produced is in the [Benchmark Guide](../BENCHMARK_GUIDE.md). What we expected, written before the runs, is in [PREDICTIONS.md](../PREDICTIONS.md).

## In Short

Across four models, with two runs of each task in each mode:

- **Tokens processed fell with Code Mode on for every model, most where the work was many MCP calls.** Added up by kind of work: 60% to 79% fewer on totalling 120 tickets (M1), 36% to 65% on reading and judging them (M2 and M3), 11% to 43% on file work (T1 and E1), and 28% to 29% on the one-question control (C0), which is the smaller start alone. Most of these tokens are read from the prompt cache at a lower rate, so this is not cost. See [Tokens Processed by Model](#tokens-processed-by-model).
- **The bullets below use task context, the detail behind that figure.** Task context is how much the conversation grew during the task. It leaves out the start that every request repeats, so its percentages differ from those in tokens processed, and it is what our rule for a real difference is written in.
- **Where the work is many MCP calls and the answer is small, Code Mode cut task context by 84% to 94% on every model.** Adding up 120 tickets fetched through an MCP server (M1) took about 54,000 tokens of conversation with Code Mode off on all four models, and 3,400 to 8,800 with it on. All 16 runs gave the same correct answer. This is the one task-level difference that meets our rule for calling it real without a caveat.
- **Every Code Mode session started about 13,000 tokens smaller, on every model.** That is 29% to 30% of the first request; over a whole C0 run it comes to the 28% to 29% of tokens processed given above, because the task's own tokens do not shrink. The saving was between 12,965 and 13,015 tokens on each of the four.
- **On the two file tasks, Code Mode used more task context, not less, in all 16 pairs of runs.** Most of those differences are within the noise. Two are not: on Fable 5.2, T1 took about three times the task context with Code Mode on, in both runs, and on Sonnet 5.5, E1 took about half as much again. Tokens processed was still lower with Code Mode on in 15 of the 16 pairs, because of the smaller start.
- **Triage through MCP used 52% to 90% less task context with Code Mode on, and twice it cost two tickets.** Of 16 triage runs with Code Mode on, two failed their check, on different models. All 16 with Code Mode off passed. See [The Two Failed Checks](#the-two-failed-checks).
- **The triage savings rest on patterns in our generated tickets.** All four models found them. They do not show that Code Mode triages free text cheaply.
- **On M1, Code Mode cost about a quarter as much and took a fifth to a third of the time,** on the three models whose recorded costs are large enough to compare.
- **94 of 96 runs passed their checks.** No run started a subagent.

## Setup

| Item                         | Value                                                                            |
| ---------------------------- | -------------------------------------------------------------------------------- |
| Date                         | 2026-11-16 Pacific time, all four rounds; `measure.txt` gives times in UTC       |
| Claude Code version          | 2.1.325, every run                                                               |
| Models                       | `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-fable-5-2`   |
| Effort                       | medium, every model                                                              |
| Fast mode                    | off                                                                              |
| Configuration                | clean                                                                            |
| Permission mode              | auto                                                                             |
| Machine                      | macOS                                                                            |
| Runs per task and mode       | 2 on every model                                                                 |
| How the sessions were driven | Round 1 by hand: prompt pasted, `/exit` typed. Rounds 2 to 4 by `bin/run-all.py` |

## How to Read the Tables

- **Result** is the checker's verdict. A saving only means something if both runs passed.
- **Fixed context** is the tokens sent in the session's first request. **Task context** is the tokens in the last request plus its reply, minus the fixed context. The README [defines both](../README.md#what-is-measured).
- **Tools run** counts every tool Claude Code ran, including those run from Code Mode scripts. **Scripts** is the number of pieces of Code Mode JavaScript.
- **Tokens processed** is every token the model read or wrote over the session: each request's input, whether or not it was read from the prompt cache, plus the output. It grows with the size of the context and with the number of requests, so it carries the smaller start of a Code Mode session into every request. It is the headline measure; task context, requests and fixed context explain it. Most of it is read from the cache at a lower rate, so it is not cost.
- **Total input** (`total_in`), which earlier versions of this page reported, is the same sum without the output. It has been dropped here so that the page has one such measure; [`measure.txt`](measure.txt) still has it.
- **Round** 1 was typed by hand and rounds 2 to 4 by the script. For Opus 5.5 the two runs of a cell are rounds 1 and 2, except on M3, where they are rounds 2 and 4. For the other models both runs are from round 3, one pass after the other.
- **Where a cell shows two figures,** the first run comes first.
- The four models are set side by side first. After that each model has its own tables with every run.

## Across the Four Models

Tokens processed comes first, by model, by kind of work and by test. Task context and requests follow as the detail behind it. The two measures give different percentages for the same runs: on M1, tokens processed fell by 60% to 79% and task context by 84% to 94%, because task context leaves out the start that every request repeats.

### Tokens Processed by Model

All runs of a model in one mode, added up. No percentage is given for these totals: they reflect this mix of tasks, three of which make 120 MCP calls each.

| Model      | Tokens processed, off | Tokens processed, on |
| ---------- | --------------------- | -------------------- |
| Opus 5.5   | 6,043,540             | 2,239,005            |
| Sonnet 5.5 | 4,792,511             | 2,382,048            |
| Haiku 5.5  | 5,098,089             | 2,914,924            |
| Fable 5.2  | 4,290,446             | 1,996,681            |

### Tokens Processed by Kind of Work

All runs of the tasks in each group, added up.

| Kind of work                                           | Tasks     | Model      | Tokens processed, off | Tokens processed, on | Change |
| ------------------------------------------------------ | --------- | ---------- | --------------------- | -------------------- | ------ |
| Totalling 120 records fetched through a tool           | M1        | Opus 5.5   | 1,550,517             | 318,201              | -79%   |
| Totalling 120 records fetched through a tool           | M1        | Sonnet 5.5 | 1,032,881             | 412,851              | -60%   |
| Totalling 120 records fetched through a tool           | M1        | Haiku 5.5  | 1,052,531             | 403,917              | -62%   |
| Totalling 120 records fetched through a tool           | M1        | Fable 5.2  | 1,054,932             | 267,195              | -75%   |
| Reading and judging 120 records fetched through a tool | M2 and M3 | Opus 5.5   | 2,979,399             | 1,034,434            | -65%   |
| Reading and judging 120 records fetched through a tool | M2 and M3 | Sonnet 5.5 | 2,531,304             | 1,150,995            | -55%   |
| Reading and judging 120 records fetched through a tool | M2 and M3 | Haiku 5.5  | 2,444,779             | 1,569,135            | -36%   |
| Reading and judging 120 records fetched through a tool | M2 and M3 | Fable 5.2  | 2,149,266             | 792,689              | -63%   |
| Finding and changing things in files                   | T1 and E1 | Opus 5.5   | 1,337,964             | 762,303              | -43%   |
| Finding and changing things in files                   | T1 and E1 | Sonnet 5.5 | 1,052,931             | 694,502              | -34%   |
| Finding and changing things in files                   | T1 and E1 | Haiku 5.5  | 1,422,355             | 814,639              | -43%   |
| Finding and changing things in files                   | T1 and E1 | Fable 5.2  | 905,139               | 807,198              | -11%   |
| One question about one file (the control)              | C0        | Opus 5.5   | 175,660               | 124,067              | -29%   |
| One question about one file (the control)              | C0        | Sonnet 5.5 | 175,395               | 123,700              | -29%   |
| One question about one file (the control)              | C0        | Haiku 5.5  | 178,424               | 127,233              | -29%   |
| One question about one file (the control)              | C0        | Fable 5.2  | 181,109               | 129,599              | -28%   |

### Tokens Processed by Test

Every pair of runs, the first pair and then the second.

| Task | Model      | Tokens processed, off | Tokens processed, on | Change     |
| ---- | ---------- | --------------------- | -------------------- | ---------- |
| C0   | Opus 5.5   | 87,731 / 87,929       | 62,052 / 62,015      | -29%, -29% |
| C0   | Sonnet 5.5 | 87,699 / 87,696       | 61,846 / 61,854      | -29%, -29% |
| C0   | Haiku 5.5  | 89,180 / 89,244       | 63,697 / 63,536      | -29%, -29% |
| C0   | Fable 5.2  | 90,554 / 90,555       | 64,805 / 64,794      | -28%, -28% |
| T1   | Opus 5.5   | 391,702 / 373,820     | 219,901 / 169,736    | -44%, -55% |
| T1   | Sonnet 5.5 | 137,308 / 133,583     | 98,803 / 98,326      | -28%, -26% |
| T1   | Haiku 5.5  | 288,342 / 294,301     | 210,133 / 223,867    | -27%, -24% |
| T1   | Fable 5.2  | 144,845 / 195,284     | 183,131 / 188,474    | +26%, -3%  |
| E1   | Opus 5.5   | 335,862 / 236,580     | 140,567 / 232,099    | -58%, -2%  |
| E1   | Sonnet 5.5 | 459,575 / 322,465     | 283,588 / 213,785    | -38%, -34% |
| E1   | Haiku 5.5  | 530,107 / 309,605     | 193,827 / 186,812    | -63%, -40% |
| E1   | Fable 5.2  | 250,278 / 314,732     | 195,598 / 239,995    | -22%, -24% |
| M1   | Opus 5.5   | 775,668 / 774,849     | 158,795 / 159,406    | -80%, -79% |
| M1   | Sonnet 5.5 | 516,429 / 516,452     | 223,605 / 189,246    | -57%, -63% |
| M1   | Haiku 5.5  | 525,159 / 527,372     | 220,016 / 183,901    | -58%, -65% |
| M1   | Fable 5.2  | 527,522 / 527,410     | 133,842 / 133,353    | -75%, -75% |
| M2   | Opus 5.5   | 729,708 / 730,559     | 263,665 / 233,655    | -64%, -68% |
| M2   | Sonnet 5.5 | 728,574 / 729,061     | 299,879 / 343,301    | -59%, -53% |
| M2   | Haiku 5.5  | 527,143 / 745,657     | 360,719 / 383,023    | -32%, -49% |
| M2   | Fable 5.2  | 527,136 / 527,191     | 170,776 / 170,653    | -68%, -68% |
| M3   | Opus 5.5   | 759,635 / 759,497     | 238,663 / 298,451    | -69%, -61% |
| M3   | Sonnet 5.5 | 536,936 / 536,733     | 221,456 / 286,359    | -59%, -47% |
| M3   | Haiku 5.5  | 548,043 / 623,936     | 455,564 / 369,829    | -17%, -41% |
| M3   | Fable 5.2  | 547,403 / 547,536     | 253,814 / 197,446    | -54%, -64% |

Tokens processed was lower with Code Mode on in 47 of the 48 pairs. The exception is Fable 5.2 on T1, where it was 26% higher in the first pair. On C0 it is 28% to 29% lower on every model: that is the smaller start alone, sent with each of the run's two requests.

### Task Context and Requests

Task context is in tokens. "Change" is the change in task context from Code Mode off to on, for the first pair of runs and then the second.

| Task | Model      | Task context, off | Task context, on | Change       | Requests, off | Requests, on |
| ---- | ---------- | ----------------- | ---------------- | ------------ | ------------- | ------------ |
| C0   | Opus 5.5   | 1,951 / 2,149     | 2,332 / 2,291    | +20%, +7%    | 2 / 2         | 2 / 2        |
| C0   | Sonnet 5.5 | 2,149 / 2,148     | 2,266 / 2,270    | +5%, +6%     | 2 / 2         | 2 / 2        |
| C0   | Haiku 5.5  | 2,148 / 2,214     | 2,504 / 2,379    | +17%, +7%    | 2 / 2         | 2 / 2        |
| C0   | Fable 5.2  | 2,152 / 2,155     | 2,327 / 2,324    | +8%, +8%     | 2 / 2         | 2 / 2        |
| T1   | Opus 5.5   | 9,443 / 6,065     | 18,388 / 6,573   | +95%, +8%    | 8 / 8         | 5 / 5        |
| T1   | Sonnet 5.5 | 4,415 / 2,665     | 4,781 / 4,499    | +8%, +69%    | 3 / 3         | 3 / 3        |
| T1   | Haiku 5.5  | 6,158 / 7,878     | 18,406 / 11,005  | +199%, +40%  | 6 / 6         | 5 / 6        |
| T1   | Fable 5.2  | 6,312 / 6,741     | 20,250 / 22,502  | +221%, +234% | 3 / 4         | 4 / 4        |
| E1   | Opus 5.5   | 8,995 / 10,299    | 9,998 / 17,347   | +11%, +68%   | 7 / 5         | 4 / 6        |
| E1   | Sonnet 5.5 | 6,184 / 5,825     | 9,459 / 9,631    | +53%, +65%   | 10 / 7        | 8 / 6        |
| E1   | Haiku 5.5  | 15,958 / 13,813   | 17,234 / 14,559  | +8%, +5%     | 10 / 6        | 5 / 5        |
| E1   | Fable 5.2  | 9,871 / 13,604    | 14,689 / 14,453  | +49%, +6%    | 5 / 6         | 5 / 6        |
| M1   | Opus 5.5   | 53,985 / 53,867   | 3,553 / 3,782    | -93%, -93%   | 12 / 12       | 5 / 5        |
| M1   | Sonnet 5.5 | 53,892 / 53,872   | 4,173 / 3,431    | -92%, -94%   | 8 / 8         | 7 / 6        |
| M1   | Haiku 5.5  | 54,909 / 55,800   | 8,670 / 8,819    | -84%, -84%   | 8 / 8         | 6 / 5        |
| M1   | Fable 5.2  | 53,745 / 53,736   | 3,703 / 3,407    | -93%, -94%   | 8 / 8         | 4 / 4        |
| M2   | Opus 5.5   | 54,053 / 54,300   | 12,522 / 7,483   | -77%, -86%   | 11 / 11       | 7 / 7        |
| M2   | Sonnet 5.5 | 53,962 / 54,050   | 7,843 / 10,331   | -85%, -81%   | 11 / 11       | 9 / 10       |
| M2   | Haiku 5.5  | 55,379 / 56,126   | 18,870 / 18,393  | -66%, -67%   | 8 / 11        | 9 / 10       |
| M2   | Fable 5.2  | 53,732 / 53,796   | 5,143 / 5,307    | -90%, -90%   | 8 / 8         | 5 / 5        |
| M3   | Opus 5.5   | 60,861 / 60,859   | 9,747 / 16,744   | -84%, -72%   | 11 / 11       | 7 / 8        |
| M3   | Sonnet 5.5 | 60,908 / 60,698   | 14,025 / 15,586  | -77%, -74%   | 8 / 8         | 6 / 8        |
| M3   | Haiku 5.5  | 62,322 / 62,591   | 29,364 / 30,141  | -53%, -52%   | 8 / 9         | 10 / 8       |
| M3   | Fable 5.2  | 60,557 / 60,480   | 18,098 / 14,154  | -70%, -77%   | 8 / 8         | 6 / 5        |

- **M1 fell by 84% to 94% in all eight pairs.** With Code Mode off the four models are within 4% of each other, because the same 120 tickets enter the conversation. With it on, three models kept the task to about 3,400 to 4,200 tokens and Haiku 5.5 to about 8,700.
- **M2 and M3 fell by 52% to 90% in all sixteen pairs.** The saving was smallest on Haiku 5.5, whose scripts returned more text.
- **T1 and E1 rose in all sixteen pairs.** The rise ranges from 5% to 234%.
- **Requests fell on M1 in all eight pairs,** by 12% to 58%. On the other tasks they moved both ways.

### Fixed Context

The tokens in each session's first request. "Share" is the part of that first request Code Mode removes. Over a whole C0 run the same start comes to 28% to 29% of tokens processed, because the task's own tokens do not shrink.

| Model      | Fixed context, off | Fixed context, on | Smaller by, on average | Share |
| ---------- | ------------------ | ----------------- | ---------------------- | ----- |
| Opus 5.5   | 42,846 to 43,132   | 29,828 to 30,122  | 13,015                 | 30%   |
| Sonnet 5.5 | 42,730 to 43,016   | 29,758 to 30,044  | 12,969                 | 30%   |
| Haiku 5.5  | 43,471 to 43,765   | 30,504 to 30,795  | 12,966                 | 30%   |
| Fable 5.2  | 44,156 to 44,443   | 31,188 to 31,479  | 12,965                 | 29%   |

The four models start at slightly different sizes, and Code Mode takes the same 13,000 tokens off each. The saved context reports show where it comes from: built-in tool definitions take 16.3k tokens with Code Mode off and 3.6k with it on.

### Models, Cost and Time

| Model      | Exact model         | Runs | Passed | Recorded cost | M1 cost, off  | M1 cost, on   | M1 seconds, off | M1 seconds, on |
| ---------- | ------------------- | ---- | ------ | ------------- | ------------- | ------------- | --------------- | -------------- |
| Opus 5.5   | `claude-opus-5-5`   | 24   | 24     | $10.30        | $0.85 / $0.87 | $0.20 / $0.20 | 69 / 67         | 14 / 17        |
| Sonnet 5.5 | `claude-sonnet-5-5` | 24   | 23     | $4.76         | $0.41 / $0.41 | $0.11 / $0.10 | 44 / 43         | 15 / 13        |
| Haiku 5.5  | `claude-haiku-5-5`  | 24   | 23     | $0.39         | $0.02 / $0.02 | $0.01 / $0.01 | 36 / 39         | 15 / 15        |
| Fable 5.2  | `claude-fable-5-2`  | 24   | 24     | $18.66        | $1.52 / $1.52 | $0.37 / $0.37 | 60 / 61         | 14 / 16        |

- **Cost is what Claude Code recorded for each session.** Haiku 5.5's recorded costs are a cent or two a run, too small and too coarse to compare the modes. We have not checked any model's recorded cost against a price list.
- **Cost depends on run order,** because the first session of each mode fills the prompt cache. Compare tokens processed, context and requests before cost; tokens processed counts cached and uncached tokens alike, so run order does not move it.
- **The four rounds cost $34.11 as recorded:** $3.97, $4.92, $23.81 and $1.41.

### What Meets Our Rule

The [rule](../README.md#how-a-difference-is-judged): both runs pass, the models differ in the same direction, and task context or requests differ by more than 35%. A measure is too noisy to judge, on a task and model, when two identical runs differ by more than 35%. The rule was written before the runs and is judged on task context and requests only; tokens processed, above, is reported beside it and not judged by it.

| Task | What the four models show                                                                                                                                                                   | Meets the rule?                                                                             |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| C0   | No difference in the task. The session starts 13,000 tokens smaller on all four                                                                                                             | The start is outside the rule's two measures. It repeated on every model                    |
| T1   | Task context higher with Code Mode on in all eight pairs. Too noisy to judge on Opus 5.5, Sonnet 5.5 and Haiku 5.5. On Fable 5.2 the repeats were within 11% and the rise was 221% and 234% | No. One model is clear, and the rule needs two                                              |
| E1   | Task context higher in all eight pairs. Too noisy on Opus 5.5 and Fable 5.2. Sonnet 5.5 rose 53% and 65%; Haiku 5.5 rose 8% and 5%                                                          | No. The two models that can be judged disagree on size                                      |
| M1   | Task context 84% to 94% lower in all eight pairs, all passing, repeats within 18%                                                                                                           | **Yes, on all four models**                                                                 |
| M2   | Task context 66% to 90% lower in all eight pairs. One Haiku 5.5 run with Code Mode on failed its check                                                                                      | Yes on Opus 5.5, Sonnet 5.5 and Fable 5.2, with the caveat that the data flatters Code Mode |
| M3   | Task context 52% to 84% lower in all eight pairs. One Sonnet 5.5 run with Code Mode on failed its check                                                                                     | Yes on Opus 5.5, Haiku 5.5 and Fable 5.2, with the same caveat                              |

## Opus 5.5

### Outcome

| Task                                      | Code Mode | Round | Result | Requests | Tools run | Scripts | Seconds | Cost (USD) |
| ----------------------------------------- | --------- | ----- | ------ | -------- | --------- | ------- | ------- | ---------- |
| C0 Control                                | off       | 1     | PASS   | 2        | 1         | 0       | 3       | 0.16       |
| C0 Control                                | off       | 2     | PASS   | 2        | 1         | 0       | 3       | 0.16       |
| C0 Control                                | on        | 1     | PASS   | 2        | 1         | 1       | 5       | 0.28       |
| C0 Control                                | on        | 2     | PASS   | 2        | 1         | 1       | 4       | 0.15       |
| T1 Find broken links                      | off       | 1     | PASS   | 8        | 7         | 0       | 47      | 0.37       |
| T1 Find broken links                      | off       | 2     | PASS   | 8        | 7         | 0       | 41      | 0.31       |
| T1 Find broken links                      | on        | 1     | PASS   | 5        | 396       | 4       | 42      | 0.36       |
| T1 Find broken links                      | on        | 2     | PASS   | 5        | 1,091     | 4       | 69      | 0.27       |
| E1 Change an API across 36 call sites     | off       | 1     | PASS   | 7        | 6         | 0       | 33      | 0.32       |
| E1 Change an API across 36 call sites     | off       | 2     | PASS   | 5        | 4         | 0       | 27      | 0.31       |
| E1 Change an API across 36 call sites     | on        | 1     | PASS   | 4        | 31        | 3       | 25      | 0.27       |
| E1 Change an API across 36 call sites     | on        | 2     | PASS   | 6        | 47        | 5       | 35      | 0.36       |
| M1 Aggregate 120 tickets through MCP      | off       | 1     | PASS   | 12       | 125       | 0       | 69      | 0.85       |
| M1 Aggregate 120 tickets through MCP      | off       | 2     | PASS   | 12       | 125       | 0       | 67      | 0.87       |
| M1 Aggregate 120 tickets through MCP      | on        | 1     | PASS   | 5        | 128       | 4       | 14      | 0.20       |
| M1 Aggregate 120 tickets through MCP      | on        | 2     | PASS   | 5        | 127       | 4       | 17      | 0.20       |
| M2 Triage 120 tickets through MCP         | off       | 1     | PASS   | 11       | 125       | 0       | 71      | 0.86       |
| M2 Triage 120 tickets through MCP         | off       | 2     | PASS   | 11       | 125       | 0       | 73      | 0.84       |
| M2 Triage 120 tickets through MCP         | on        | 1     | PASS   | 7        | 130       | 6       | 29      | 0.30       |
| M2 Triage 120 tickets through MCP         | on        | 2     | PASS   | 7        | 131       | 6       | 28      | 0.26       |
| M3 Triage 120 tickets with varied wording | off       | 2     | PASS   | 11       | 125       | 0       | 70      | 0.90       |
| M3 Triage 120 tickets with varied wording | off       | 4     | PASS   | 11       | 125       | 0       | 66      | 0.94       |
| M3 Triage 120 tickets with varied wording | on        | 2     | PASS   | 7        | 131       | 6       | 31      | 0.29       |
| M3 Triage 120 tickets with varied wording | on        | 4     | PASS   | 8        | 131       | 7       | 32      | 0.47       |

No run started a subagent. Round 1's ten runs cost $3.97, round 2's twelve cost $4.92 and round 4's two cost $1.41, $10.30 in all.

### Context

| Task                                      | Code Mode | Round | Fixed context (tokens) | Task context (tokens) | Largest context reached (tokens) |
| ----------------------------------------- | --------- | ----- | ---------------------- | --------------------- | -------------------------------- |
| C0 Control                                | off       | 1     | 42,846                 | 1,951                 | 44,702                           |
| C0 Control                                | off       | 2     | 42,846                 | 2,149                 | 44,892                           |
| C0 Control                                | on        | 1     | 29,828                 | 2,332                 | 32,013                           |
| C0 Control                                | on        | 2     | 29,830                 | 2,291                 | 32,008                           |
| T1 Find broken links                      | off       | 1     | 43,132                 | 9,443                 | 51,875                           |
| T1 Find broken links                      | off       | 2     | 43,129                 | 6,065                 | 48,643                           |
| T1 Find broken links                      | on        | 1     | 30,120                 | 18,388                | 48,132                           |
| T1 Find broken links                      | on        | 2     | 30,122                 | 6,573                 | 36,203                           |
| E1 Change an API across 36 call sites     | off       | 1     | 42,947                 | 8,995                 | 51,353                           |
| E1 Change an API across 36 call sites     | off       | 2     | 42,918                 | 10,299                | 52,650                           |
| E1 Change an API across 36 call sites     | on        | 1     | 29,929                 | 9,998                 | 39,385                           |
| E1 Change an API across 36 call sites     | on        | 2     | 29,906                 | 17,347                | 46,765                           |
| M1 Aggregate 120 tickets through MCP      | off       | 1     | 43,023                 | 53,985                | 96,788                           |
| M1 Aggregate 120 tickets through MCP      | off       | 2     | 43,020                 | 53,867                | 96,671                           |
| M1 Aggregate 120 tickets through MCP      | on        | 1     | 30,002                 | 3,553                 | 33,382                           |
| M1 Aggregate 120 tickets through MCP      | on        | 2     | 30,008                 | 3,782                 | 33,577                           |
| M2 Triage 120 tickets through MCP         | off       | 1     | 43,013                 | 54,053                | 96,644                           |
| M2 Triage 120 tickets through MCP         | off       | 2     | 43,014                 | 54,300                | 96,764                           |
| M2 Triage 120 tickets through MCP         | on        | 1     | 29,995                 | 12,522                | 42,068                           |
| M2 Triage 120 tickets through MCP         | on        | 2     | 29,993                 | 7,483                 | 36,866                           |
| M3 Triage 120 tickets with varied wording | off       | 2     | 43,013                 | 60,861                | 103,278                          |
| M3 Triage 120 tickets with varied wording | off       | 4     | 43,006                 | 60,859                | 103,275                          |
| M3 Triage 120 tickets with varied wording | on        | 2     | 29,992                 | 9,747                 | 39,126                           |
| M3 Triage 120 tickets with varied wording | on        | 4     | 29,997                 | 16,744                | 46,295                           |

In all three MCP tasks, in every run, the server received the same calls in both modes: 3 to list the tickets and 120 to fetch them. Code Mode did the same work, not less.

### Tokens Processed

| Task                                      | Off, first run | Off, second run | On, first run | On, second run |
| ----------------------------------------- | -------------- | --------------- | ------------- | -------------- |
| C0 Control                                | 87,731         | 87,929          | 62,052        | 62,015         |
| T1 Find broken links                      | 391,702        | 373,820         | 219,901       | 169,736        |
| E1 Change an API across 36 call sites     | 335,862        | 236,580         | 140,567       | 232,099        |
| M1 Aggregate 120 tickets through MCP      | 775,668        | 774,849         | 158,795       | 159,406        |
| M2 Triage 120 tickets through MCP         | 729,708        | 730,559         | 263,665       | 233,655        |
| M3 Triage 120 tickets with varied wording | 759,635        | 759,497         | 238,663       | 298,451        |

Task context says how large the conversation became. Tokens processed says how many tokens the model read and wrote to get there. Most of them are read from the prompt cache at a lower price, so this is not a measure of cost.

- **M1:** 80% and 79% lower with Code Mode on.
- **M2 and M3:** 61% to 69% lower.
- **T1:** 44% and 55% lower. The repeats differed by 5% with Code Mode off and 23% with it on, so on this measure T1 shows a difference that task context could not. It comes from the smaller start and from 5 requests against 8.
- **E1:** 58% lower in round 1 and 2% lower in round 2. Too noisy to judge.
- **C0:** 29% lower in both rounds, which is the smaller start alone, sent with each of the two requests.

## How Much Two Identical Runs Differ

Round 2 repeated every round 1 run with nothing changed but who did the typing, and round 4 repeated round 2's M3 runs with nothing changed at all. The change from the first run to the second in each cell is the yardstick for every difference between modes on this page.

| Task | Code Mode | Fixed context | Task context | Requests |
| ---- | --------- | ------------- | ------------ | -------- |
| C0   | off       | same          | +10%         | same     |
| C0   | on        | +2 tokens     | -2%          | same     |
| T1   | off       | -3 tokens     | -36%         | same     |
| T1   | on        | +2 tokens     | -64%         | same     |
| E1   | off       | -29 tokens    | +14%         | 7 to 5   |
| E1   | on        | -23 tokens    | +74%         | 4 to 6   |
| M1   | off       | -3 tokens     | -0%          | same     |
| M1   | on        | +6 tokens     | +6%          | same     |
| M2   | off       | +1 token      | +0%          | same     |
| M2   | on        | -2 tokens     | -40%         | same     |
| M3   | off       | -7 tokens     | -0%          | same     |
| M3   | on        | +5 tokens     | +72%         | 7 to 8   |

What this shows:

- **Scripted runs gave the same results as hand-typed ones.** Every scripted run passed, and request counts matched in eight of the ten cells that set round 1 beside round 2. Fixed context matched within 29 tokens in every cell, which shows the sessions were started alike; it is set before anything is typed.
- **Fixed context and the MCP tasks with Code Mode off barely move.** Those runs fetch the same 120 tickets into the conversation each time.
- **Task context swings widely wherever Claude writes a program,** which is every Code Mode run and both modes of the file tasks. The size depends on how much the program prints back, and in each cell that swung, one result explains most of the gap:
  - **T1 with Code Mode on:** round 1's first script returned the text of every file and added about 14,500 tokens. Round 2's first script added about 1,400.
  - **E1 with Code Mode on:** one round 2 script returned the whole `git diff` and added about 8,100 tokens.
  - **M2 with Code Mode on:** round 1's first tool search was broader, `tickets records` against `tickets`, and its result included the definitions of tools that have nothing to do with the task. It added about 5,400 tokens against about 430. Set that one result aside and the two runs are within 1% of each other.
  - **M3 with Code Mode on:** round 4's script that grouped the masked sentences printed every group, not only the rare ones, and added about 9,500 tokens. Round 2's added about 3,300.
- **Request counts are steadier than task context.** Nine of twelve cells repeated exactly.

The README's [rule](../README.md#how-a-difference-is-judged) says a measure is too noisy to judge when repeats of a Code Mode off run differ by more than 35%. T1 off differed by 36% on task context. We apply the rule per task: task context is reported as too noisy to judge on T1, and on E1, where the Code Mode on repeat differed by 74%. On M3 the Code Mode on repeat differed by 72%, but both runs were at least 72% below Code Mode off, so the difference between modes is far larger than the spread.

## Sonnet 5.5

Every run, from round 3. Fixed context, task context and tokens processed are in tokens.

| Task                                      | Code Mode | Run | Result | Requests | Tools run | Scripts | Seconds | Fixed context | Task context | Tokens processed | Cost (USD) |
| ----------------------------------------- | --------- | --- | ------ | -------- | --------- | ------- | ------- | ------------- | ------------ | ---------------- | ---------- |
| C0 Control                                | off       | 1   | PASS   | 2        | 1         | 0       | 3       | 42,731        | 2,149        | 87,699           | 0.09       |
| C0 Control                                | off       | 2   | PASS   | 2        | 1         | 0       | 3       | 42,730        | 2,148        | 87,696           | 0.08       |
| C0 Control                                | on        | 1   | PASS   | 2        | 1         | 1       | 4       | 29,758        | 2,266        | 61,846           | 0.14       |
| C0 Control                                | on        | 2   | PASS   | 2        | 1         | 1       | 4       | 29,760        | 2,270        | 61,854           | 0.08       |
| T1 Find broken links                      | off       | 1   | PASS   | 3        | 2         | 0       | 19      | 43,016        | 4,415        | 137,308          | 0.11       |
| T1 Find broken links                      | off       | 2   | PASS   | 3        | 2         | 0       | 13      | 43,013        | 2,665        | 133,583          | 0.10       |
| T1 Find broken links                      | on        | 1   | PASS   | 3        | 3         | 2       | 17      | 30,043        | 4,781        | 98,803           | 0.11       |
| T1 Find broken links                      | on        | 2   | PASS   | 3        | 3         | 2       | 15      | 30,044        | 4,499        | 98,326           | 0.10       |
| E1 Change an API across 36 call sites     | off       | 1   | PASS   | 10       | 9         | 0       | 26      | 42,803        | 6,184        | 459,575          | 0.16       |
| E1 Change an API across 36 call sites     | off       | 2   | PASS   | 7        | 6         | 0       | 21      | 42,800        | 5,825        | 322,465          | 0.14       |
| E1 Change an API across 36 call sites     | on        | 1   | PASS   | 8        | 85        | 7       | 34      | 29,831        | 9,459        | 283,588          | 0.15       |
| E1 Change an API across 36 call sites     | on        | 2   | PASS   | 6        | 75        | 5       | 26      | 29,829        | 9,631        | 213,785          | 0.13       |
| M1 Aggregate 120 tickets through MCP      | off       | 1   | PASS   | 8        | 125       | 0       | 44      | 42,904        | 53,892       | 516,429          | 0.41       |
| M1 Aggregate 120 tickets through MCP      | off       | 2   | PASS   | 8        | 125       | 0       | 43      | 42,899        | 53,872       | 516,452          | 0.41       |
| M1 Aggregate 120 tickets through MCP      | on        | 1   | PASS   | 7        | 128       | 6       | 15      | 29,934        | 4,173        | 223,605          | 0.11       |
| M1 Aggregate 120 tickets through MCP      | on        | 2   | PASS   | 6        | 128       | 5       | 13      | 29,937        | 3,431        | 189,246          | 0.10       |
| M2 Triage 120 tickets through MCP         | off       | 1   | PASS   | 11       | 125       | 0       | 54      | 42,889        | 53,962       | 728,574          | 0.43       |
| M2 Triage 120 tickets through MCP         | off       | 2   | PASS   | 11       | 125       | 0       | 55      | 42,894        | 54,050       | 729,061          | 0.43       |
| M2 Triage 120 tickets through MCP         | on        | 1   | PASS   | 9        | 131       | 8       | 23      | 29,922        | 7,843        | 299,879          | 0.14       |
| M2 Triage 120 tickets through MCP         | on        | 2   | PASS   | 10       | 133       | 9       | 29      | 29,928        | 10,331       | 343,301          | 0.16       |
| M3 Triage 120 tickets with varied wording | off       | 1   | PASS   | 8        | 125       | 0       | 45      | 42,888        | 60,908       | 536,936          | 0.44       |
| M3 Triage 120 tickets with varied wording | off       | 2   | PASS   | 8        | 125       | 0       | 46      | 42,898        | 60,698       | 536,733          | 0.42       |
| M3 Triage 120 tickets with varied wording | on        | 1   | FAIL   | 6        | 128       | 5       | 20      | 29,925        | 14,025       | 221,456          | 0.15       |
| M3 Triage 120 tickets with varied wording | on        | 2   | PASS   | 8        | 130       | 7       | 23      | 29,926        | 15,586       | 286,359          | 0.17       |

One run failed: M3 with Code Mode on, first run, which found 7 of the 9 tickets.

## Haiku 5.5

| Task                                      | Code Mode | Run | Result | Requests | Tools run | Scripts | Seconds | Fixed context | Task context | Tokens processed | Cost (USD) |
| ----------------------------------------- | --------- | --- | ------ | -------- | --------- | ------- | ------- | ------------- | ------------ | ---------------- | ---------- |
| C0 Control                                | off       | 1   | PASS   | 2        | 1         | 0       | 3       | 43,472        | 2,148        | 89,180           | 0.01       |
| C0 Control                                | off       | 2   | PASS   | 2        | 1         | 0       | 2       | 43,471        | 2,214        | 89,244           | 0.00       |
| C0 Control                                | on        | 1   | PASS   | 2        | 1         | 2       | 5       | 30,506        | 2,504        | 63,697           | 0.01       |
| C0 Control                                | on        | 2   | PASS   | 2        | 1         | 1       | 4       | 30,504        | 2,379        | 63,536           | 0.00       |
| T1 Find broken links                      | off       | 1   | PASS   | 6        | 5         | 0       | 23      | 43,765        | 6,158        | 288,342          | 0.01       |
| T1 Find broken links                      | off       | 2   | PASS   | 6        | 5         | 0       | 23      | 43,764        | 7,878        | 294,301          | 0.01       |
| T1 Find broken links                      | on        | 1   | PASS   | 5        | 54        | 4       | 25      | 30,794        | 18,406       | 210,133          | 0.01       |
| T1 Find broken links                      | on        | 2   | PASS   | 6        | 935       | 5       | 66      | 30,795        | 11,005       | 223,867          | 0.01       |
| E1 Change an API across 36 call sites     | off       | 1   | PASS   | 10       | 9         | 0       | 45      | 43,548        | 15,958       | 530,107          | 0.02       |
| E1 Change an API across 36 call sites     | off       | 2   | PASS   | 6        | 5         | 0       | 33      | 43,543        | 13,813       | 309,605          | 0.01       |
| E1 Change an API across 36 call sites     | on        | 1   | PASS   | 5        | 94        | 4       | 45      | 30,584        | 17,234       | 193,827          | 0.01       |
| E1 Change an API across 36 call sites     | on        | 2   | PASS   | 5        | 41        | 4       | 39      | 30,582        | 14,559       | 186,812          | 0.01       |
| M1 Aggregate 120 tickets through MCP      | off       | 1   | PASS   | 8        | 125       | 0       | 36      | 43,647        | 54,909       | 525,159          | 0.02       |
| M1 Aggregate 120 tickets through MCP      | off       | 2   | PASS   | 8        | 125       | 0       | 39      | 43,650        | 55,800       | 527,372          | 0.02       |
| M1 Aggregate 120 tickets through MCP      | on        | 1   | PASS   | 6        | 128       | 5       | 15      | 30,686        | 8,670        | 220,016          | 0.01       |
| M1 Aggregate 120 tickets through MCP      | on        | 2   | PASS   | 5        | 127       | 4       | 15      | 30,691        | 8,819        | 183,901          | 0.01       |
| M2 Triage 120 tickets through MCP         | off       | 1   | PASS   | 8        | 125       | 0       | 38      | 43,639        | 55,379       | 527,143          | 0.02       |
| M2 Triage 120 tickets through MCP         | off       | 2   | PASS   | 11       | 125       | 0       | 43      | 43,644        | 56,126       | 745,657          | 0.03       |
| M2 Triage 120 tickets through MCP         | on        | 1   | PASS   | 9        | 131       | 8       | 32      | 30,672        | 18,870       | 360,719          | 0.01       |
| M2 Triage 120 tickets through MCP         | on        | 2   | FAIL   | 10       | 134       | 9       | 31      | 30,666        | 18,393       | 383,023          | 0.01       |
| M3 Triage 120 tickets with varied wording | off       | 1   | PASS   | 8        | 125       | 0       | 39      | 43,634        | 62,322       | 548,043          | 0.06       |
| M3 Triage 120 tickets with varied wording | off       | 2   | PASS   | 9        | 125       | 0       | 41      | 43,641        | 62,591       | 623,936          | 0.06       |
| M3 Triage 120 tickets with varied wording | on        | 1   | PASS   | 10       | 131       | 9       | 33      | 30,673        | 29,364       | 455,564          | 0.02       |
| M3 Triage 120 tickets with varied wording | on        | 2   | PASS   | 8        | 130       | 7       | 25      | 30,673        | 30,141       | 369,829          | 0.01       |

One run failed: M2 with Code Mode on, second run, which reported 7 of the 9 tickets.

## Fable 5.2

| Task                                      | Code Mode | Run | Result | Requests | Tools run | Scripts | Seconds | Fixed context | Task context | Tokens processed | Cost (USD) |
| ----------------------------------------- | --------- | --- | ------ | -------- | --------- | ------- | ------- | ------------- | ------------ | ---------------- | ---------- |
| C0 Control                                | off       | 1   | PASS   | 2        | 1         | 0       | 3       | 44,157        | 2,152        | 90,554           | 0.34       |
| C0 Control                                | off       | 2   | PASS   | 2        | 1         | 0       | 3       | 44,156        | 2,155        | 90,555           | 0.30       |
| C0 Control                                | on        | 1   | PASS   | 2        | 1         | 1       | 4       | 31,191        | 2,327        | 64,805           | 0.56       |
| C0 Control                                | on        | 2   | PASS   | 2        | 1         | 1       | 4       | 31,188        | 2,324        | 64,794           | 0.29       |
| T1 Find broken links                      | off       | 1   | PASS   | 3        | 2         | 0       | 32      | 44,442        | 6,312        | 144,845          | 0.51       |
| T1 Find broken links                      | off       | 2   | PASS   | 4        | 3         | 0       | 39      | 44,443        | 6,741        | 195,284          | 0.55       |
| T1 Find broken links                      | on        | 1   | PASS   | 4        | 9         | 3       | 53      | 31,476        | 20,250       | 183,131          | 0.81       |
| T1 Find broken links                      | on        | 2   | PASS   | 4        | 6         | 3       | 46      | 31,479        | 22,502       | 188,474          | 0.80       |
| E1 Change an API across 36 call sites     | off       | 1   | PASS   | 5        | 4         | 0       | 22      | 44,228        | 9,871        | 250,278          | 0.53       |
| E1 Change an API across 36 call sites     | off       | 2   | PASS   | 6        | 5         | 0       | 25      | 44,225        | 13,604       | 314,732          | 0.61       |
| E1 Change an API across 36 call sites     | on        | 1   | PASS   | 5        | 48        | 4       | 28      | 31,260        | 14,689       | 195,598          | 0.58       |
| E1 Change an API across 36 call sites     | on        | 2   | PASS   | 6        | 45        | 5       | 31      | 31,265        | 14,453       | 239,995          | 0.61       |
| M1 Aggregate 120 tickets through MCP      | off       | 1   | PASS   | 8        | 125       | 0       | 60      | 44,334        | 53,745       | 527,522          | 1.52       |
| M1 Aggregate 120 tickets through MCP      | off       | 2   | PASS   | 8        | 125       | 0       | 61      | 44,333        | 53,736       | 527,410          | 1.52       |
| M1 Aggregate 120 tickets through MCP      | on        | 1   | PASS   | 4        | 127       | 3       | 14      | 31,364        | 3,703        | 133,842          | 0.37       |
| M1 Aggregate 120 tickets through MCP      | on        | 2   | PASS   | 4        | 127       | 3       | 16      | 31,367        | 3,407        | 133,353          | 0.37       |
| M2 Triage 120 tickets through MCP         | off       | 1   | PASS   | 8        | 125       | 0       | 60      | 44,318        | 53,732       | 527,136          | 1.52       |
| M2 Triage 120 tickets through MCP         | off       | 2   | PASS   | 8        | 125       | 0       | 61      | 44,312        | 53,796       | 527,191          | 1.52       |
| M2 Triage 120 tickets through MCP         | on        | 1   | PASS   | 5        | 128       | 4       | 20      | 31,358        | 5,143        | 170,776          | 0.42       |
| M2 Triage 120 tickets through MCP         | on        | 2   | PASS   | 5        | 127       | 4       | 18      | 31,350        | 5,307        | 170,653          | 0.42       |
| M3 Triage 120 tickets with varied wording | off       | 1   | PASS   | 8        | 125       | 0       | 62      | 44,315        | 60,557       | 547,403          | 1.63       |
| M3 Triage 120 tickets with varied wording | off       | 2   | PASS   | 8        | 125       | 0       | 61      | 44,320        | 60,480       | 547,536          | 1.63       |
| M3 Triage 120 tickets with varied wording | on        | 1   | PASS   | 6        | 130       | 5       | 26      | 31,351        | 18,098       | 253,814          | 0.67       |
| M3 Triage 120 tickets with varied wording | on        | 2   | PASS   | 5        | 128       | 4       | 19      | 31,356        | 14,154       | 197,446          | 0.58       |

All 24 runs passed.

## Against the Predictions

This repository's history begins after the runs, so it does not show when the predictions were written. For the record: the first five were written before round 1, M3's was written after round 1 and before any M3 run, and one line in PREDICTIONS.md, marked "Settled", was added after the runs. That is our statement, not proof. The prediction for any later test will be published before the test is run.

| Task | Predicted                                                                                                  | What happened across the four models                                                                                                                                                                                                                     | Prediction held?                                               |
| ---- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| C0   | None in the answer. A small fixed cost or saving in how large the session starts                           | Same answer in all 16 runs. The session started about 13,000 tokens smaller with Code Mode on, on every model, which is more than "small"                                                                                                                | Partly                                                         |
| T1   | No material difference in task context. Possibly fewer requests                                            | No saving on any model. Task context was higher with Code Mode on in all eight pairs, and about three times as high on Fable 5.2. Fewer requests on Opus 5.5 only                                                                                        | Partly. No saving, as predicted, but a clear rise on one model |
| E1   | A moderate reduction in requests and task context, or none                                                 | Task context higher in all eight pairs, by 5% to 68%. Requests fewer or equal in seven of the eight                                                                                                                                                      | Partly. "None" for requests; task context went the other way   |
| M1   | A large reduction in task context and requests. Same correct answer                                        | Task context 84% to 94% lower and requests fewer in all eight pairs. Same correct answer in all 16 runs                                                                                                                                                  | Yes                                                            |
| M2   | A small reduction at best. Accuracy may be lower                                                           | Task context 66% to 90% lower on all four models. One of the eight runs with Code Mode on left out two tickets                                                                                                                                           | No on the size. The warning about accuracy came true once      |
| M3   | A smaller reduction than M2 showed, or a missed ticket, or both. Well over 12,500 tokens with Code Mode on | On Sonnet 5.5, Haiku 5.5 and Fable 5.2 the reduction was smaller than on M2, and the Code Mode runs took 14,000 to 30,000 tokens. One Sonnet 5.5 run missed two tickets. On Opus 5.5 the two Code Mode runs took 9,747 and 16,744 tokens and missed none | Yes on three models. On Opus 5.5, in one run of two            |

How the reading changed with each round. After round 1, T1 and M2 looked wrong. After round 2, T1's doubled context had not repeated and M3 looked wrong too. Round 3 put M3's prediction right on three models out of four, and showed that T1's rise in context is real on at least one model. Round 4 repeated Opus 5.5's M3 pair: its Code Mode run took 16,744 tokens, so on Opus 5.5 the prediction held in one run of two.

One estimate behind a prediction was off. We expected M1 with Code Mode off to put about 30,000 tokens of tickets into the conversation; it put about 54,000, on every model.

## What Claude Did

Taken from the saved transcripts. The table is Opus 5.5, rounds 1 and 2, and rounds 2 and 4 for M3; where the two runs differed, both are given. The other models follow it.

| Task | Code Mode off                                                                                                                         | Code Mode on                                                                                                                                                                                                                                                                                                                                                       |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| C0   | One shell command to read the file                                                                                                    | One script that read the file                                                                                                                                                                                                                                                                                                                                      |
| T1   | Wrote a Python script to a scratch file and ran it. Seven shell commands in both rounds                                               | Four scripts in both rounds. One read every file, and the others ran a separate shell check for each link: 347 checks in round 1, 1,039 over three passes in round 2. Round 1's first script returned the text of every file; round 2's returned a summary                                                                                                         |
| E1   | Read the files with shell commands, then wrote and ran a script that rewrote the call sites. Six commands in round 1, four in round 2 | Round 1: three scripts, one to look around, one to read every file, one to run a rewrite that parses the Python. Round 2: five scripts, with the rewrite done by pattern matching, and one script returning the whole `git diff`                                                                                                                                   |
| M1   | Fetched the 120 tickets twenty at a time, so every ticket passed through the conversation                                             | One script fetched all 120 at once and returned a count and a sample                                                                                                                                                                                                                                                                                               |
| M2   | Fetched all 120 tickets and read them                                                                                                 | Kept the tickets in a variable between scripts, pulled out sentences that mention billing, then listed every distinct sentence across all tickets and read that list. The same in both rounds                                                                                                                                                                      |
| M3   | Fetched all 120 tickets and read them                                                                                                 | Kept the tickets in a variable. Pulled out sentences matching a list of billing words. Then replaced days, months, names and numbers with placeholders, grouped the sentences that became identical, and printed only the groups of six or fewer. Round 4 took the same steps but masked fewer details and printed every group, which made its task context larger |

In no task did Claude edit files one at a time or start a subagent, in either mode. On both file tasks it wrote a program to do the work, with Code Mode off as well as on.

### On the Other Models

We read 11 of round 3's 72 transcripts: the two runs that failed, their passing twins, and others where the numbers stood out.

- **File tasks:** every model wrote a program in both modes, as Opus 5.5 did. With Code Mode on the same kind of program arrives wrapped in a script. On T1, Fable 5.2 wrote a Python checker to a scratch file in both modes; with Code Mode on, its first script also returned file listings worth about 14,000 tokens, which is most of the rise in its task context.
- **MCP tasks:** every run fetched all 120 tickets through the server. Of the 48 MCP runs, 45 made the same 123 calls. Three Sonnet 5.5 runs with Code Mode on made one or two more.
- **Triage with Code Mode on:** all four models found the repeated sentences in M2 and the sentence patterns in M3. By a pattern search of the scripts, which is cruder than reading them, 13 of the 16 runs listed or grouped sentences across tickets, and all 13 passed. Three relied on keyword filters alone, and two of those three are the failed checks.
- **No run on any model started a subagent.**

## The Two Failed Checks

Both were triage runs with Code Mode on, and both left out the same two tickets, `TCK-1060` and `TCK-1071`. Those two share one wording: an add-on that appears on two consecutive receipts though it was bought once. The causes differ.

| Run                                     | Answer             | What happened                                                                                                                                                                                                                                       |
| --------------------------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sonnet 5.5, M3, Code Mode on, first run | 7 of 9, none wrong | Its scripts returned the first 600 characters of each ticket, then the sentences that matched a list of billing words. The receipts sentence matched none of them and never reached the conversation. The answer said all 120 tickets had been read |
| Haiku 5.5, M2, Code Mode on, second run | 7 of 9, none wrong | It printed both tickets in full and decided against them: "That describes a receipt, not a confirmed charge." It said so in its answer, and added that the count becomes 9 if receipt duplicates count as charges                                   |

- **The first is the failure our M3 prediction named.** A script that filters by keywords drops the tickets worded without them. Sonnet 5.5's second run added a step that grouped sentences by pattern, and found all nine.
- **The second is a judgement, openly stated, and it points at our answer key.** One of the six wordings we planted describes receipts, not charges. Every other run counted it, including Haiku 5.5's other three M2 runs, but the reading Haiku gave is a fair one.
- **Both happened with Code Mode on,** and all 16 triage runs with Code Mode off passed. Two failures in 16 runs is too few to state a rate, and only the first follows from how Code Mode works.

## What the M2 Result Does and Does Not Show

Claude's Code Mode runs on M2 found all nine tickets while reading a quarter as much or less. It did so by noticing that the tickets were assembled from a small set of repeated sentences: across 120 tickets there are only 31 distinct sentences, so listing each one once is far shorter than reading every ticket.

That is good work by the model, and a fault in our test data. Real support tickets do not repeat their sentences. So the M2 result shows that Code Mode lets a model exploit repetition in data; it does not show that Code Mode can triage free text cheaply.

Task M3 was added for that reason. It asks the same question of the same tickets, reworded so that sentences do not repeat: 875 distinct sentences in place of 31. M2 is kept as it was, with its result, and M3 has its own prediction, written before it was run.

Round 3 showed the same on the other three models: each listed the distinct sentences in at least one of its M2 runs.

## What the M3 Result Does and Does Not Show

M3 has the same fault in a weaker form. Its 875 distinct sentences were made by filling details into 31 sentence patterns: a day, a month, a number, a job title, a part of the product, a city. Two sentences from one pattern differ only in those details.

With Code Mode on, in round 2, Claude took two steps. A keyword filter found the telling sentence in five of the nine tickets. Then it masked the details that vary, grouped the sentences that became identical, and printed only the rare groups. The sentences that describe a real double charge are rare, so they appeared, and the other four tickets were found. Claude's answer said it had read all 120 tickets. Its scripts processed all 120; the conversation received the keyword matches and the rare groups.

Our prediction named two ways a script could go: return most of the text, or filter by keywords and miss tickets. The keyword filter alone would have missed four of nine, as predicted. We did not foresee the third way.

Opus 5.5's second Code Mode run, in round 4, took the same two steps and found all nine tickets. Its keyword filter was broader and matched 65 tickets, mostly on sentences such as "followed up twice by email". Its masking left more of the details in place, giving 174 groups, and it printed every group, not only the rare ones; that one result is most of why its task context was 16,744 tokens, against 9,747 in round 2.

The paragraphs above describe Opus 5.5. In round 3, Sonnet 5.5, Haiku 5.5 and Fable 5.2 each masked the details and grouped the sentences in at least one M3 run. The Sonnet 5.5 run that missed two tickets stopped at the keyword filter.

So M3 shows what M2 showed: Code Mode lets a model find and exploit structure in generated data. It still does not show whether Code Mode can triage free text cheaply. A task that tests that needs tickets written one by one, with no shared patterns. That task is not built.

## Screenshots

None yet. Files go in `screenshots/`, named by task, model and mode, such as `M1-opus-off-end.png`.

## Limits of This Result

- **Two runs behind each figure.** Two samples show that a figure can move; they do not measure how far it usually moves.
- **One effort level, one Claude Code version.** Every run used medium effort on 2.1.325. Version 2.1.326, released during round 3, changes how Code Mode handles shell commands and permissions; none of these runs used it.
- **Task context on the file tasks is too noisy to judge on most models,** as shown above.
- **The totals by model reflect this mix of tasks.** Three of the six make 120 MCP calls each, which is where Code Mode does best. For file work, read the file-work rows, not the totals.
- **Tokens processed is not cost.** Most of these tokens are read from the prompt cache, which is billed at a lower rate.
- **The answer key for M2 and M3 has one doubtful wording,** the add-on on two consecutive receipts. A model that reads it as a receipt and not a charge fails the check.
- **Recorded costs are Claude Code's own figures,** not checked against a price list, and Haiku 5.5's are too small to compare.
- **Cost depends on run order.** The first session of each mode has to fill Claude Code's prompt cache. C0 with Code Mode on cost $0.28 in round 1, when it was the first Code Mode session, and $0.15 in round 2, when it wrote half as much to the cache. Compare tokens processed, context and requests before cost.
- **Part of every session's start comes from the tester's Claude account.** Skills and custom agents take about 10,400 tokens of fixed context, in both modes alike. Some are built into Claude Code; the rest come from plugins synced to the account, which load even in the clean configuration. We cannot say how the 10,400 divides, so your fixed context may differ by up to that much. None of it reached a result that we can find: the unrelated tools the broad search in M2 returned are built into Claude Code.
- **Task context counts the main conversation only.** No run used a subagent, so nothing is hidden by that here.
- **M2 and M3 rest on generated data with structure a script can find,** as described above.
- **The first run of the day** was done with the measuring script counting requests wrongly for Code Mode sessions. The script was corrected and all runs were read again from their saved transcripts; no run was repeated. The [changelog](../CHANGELOG.md) has the detail.

## Run Log

What was run in each round, and what changed before the next. The [changelog](../CHANGELOG.md) records the same changes by version.

### Round 1: Opus 5.5, Typed by Hand, 2026-11-16

- Ten runs: C0, T1, E1, M1 and M2, each with Code Mode off and then on. A person started each session, pasted the prompt and typed `/exit`.
- All ten passed.
- Benchmark version 0.1.0.

What the round showed about the benchmark itself:

- **The request count was wrong for Code Mode sessions.** Fixed in the reading; no run repeated.
- **M2's data let a script skip the reading.** M3 was added.
- **Both control runs behaved,** which confirmed that test sessions no longer loaded the tester's own instruction files or account connectors.

### Changes Before Round 2

- Task M3 added to the set.
- Runs are typed by `bin/run-all.py` from here on. The sessions are otherwise started exactly as in round 1: same command, same settings, same prompts, same data.
- The scripts refuse to run from inside a Claude Code session.
- Benchmark version 0.2.0. Nothing in it changes how a session runs for the five round 1 tasks.

### Round 2: Opus 5.5 Again, Typed by the Script, 2026-11-16

- Twelve runs: all six tasks, each with Code Mode off and then on, typed by `bin/run-all.py opus`. The first run started 24 minutes after round 1's last.
- All twelve passed. The script needed no help and no fixes.
- Benchmark version 0.2.0, unchanged.

What the round showed about the benchmark itself:

- **The script can be trusted with the other models.** Fixed context matched round 1 within 29 tokens in every cell.
- **Task context on the file tasks is too noisy to judge from one run.** Round 1's finding that Code Mode doubled T1's context did not repeat.
- **M3 did not close the gap M2 left.** Its wording varies only by details filled into patterns, and Claude masked the details.
- **M3 was run before its prediction was published.** The prediction was written before any M3 run, but nothing had been published when M3 ran, so the order cannot be checked from outside.

### Changes Before Round 3

Nothing that changes how a session runs: the tasks, prompts, data and launch settings are as they were.

- `bin/measure.py` has a new column, `total_in`. Rounds 1 and 2 were read again from their saved transcripts to fill it.
- Saved context reports leave out the lists of skills and custom agents, some of which come from the tester's Claude account. The twelve reports from round 2 were rewritten the same way.
- The noise rule's per-task reading, used above, is written into the [README](../README.md#how-a-difference-is-judged).

### Round 3: Sonnet 5.5, Haiku 5.5 and Fable 5.2, 2026-11-16

- 72 runs: all six tasks, off then on, twice for each model, typed by `REPEAT=2 bin/run-all.py sonnet claude-haiku-5-5 fable`. Each model finished both passes before the next began.
- It took one hour: 18 minutes for Sonnet 5.5, 20 for Haiku 5.5 and 21 for Fable 5.2. The script needed no help and did not stall.
- 70 of the 72 passed. The two that failed are described under [The Two Failed Checks](#the-two-failed-checks).
- Every run used Claude Code 2.1.325 at medium effort.

What the round showed about the benchmark itself:

- **The script works on all four models** without a change.
- **A failed check does not stop the script.** It is a result, and the round carried on, as intended.
- **The answer key has a doubtful wording,** found when Haiku 5.5 argued against it.
- **Claude Code 2.1.326 came out during the round.** It was not installed, so the round is on one version. A later round on the new version needs at least one model repeated before the two are compared.

### After Round 3

- `bin/run.py` no longer drops any MCP row from a saved context report. The extra server it had been dropping is built into Claude Code, not part of the tester's account. All 84 saved reports were written again from their transcripts.
- The help text of `bin/run-all.py` said ten runs; it now says twelve.
- **Results are reported in tokens processed first.** `bin/measure.py` has a new column, `processed`: `total_in` plus every output token, read from the saved transcripts for all 94 runs. The README's summary and this page now lead with it, by model and by kind of work, with task context and requests as the detail behind it. The total input tables and columns on this page were replaced with tokens processed, so the page has one such measure; `total_in` stays in `measure.txt`. Nothing about any run changed.

### Round 4: Opus 5.5 M3 Again, 2026-11-16

- Two runs: M3 with Code Mode off and then on, typed by `TASKS=M3 bin/run-all.py opus`. They started at 04:12 and 04:13 UTC on 2026-11-17.
- Both passed.
- Made so that every model has two runs of every test in each mode. Until then Opus 5.5 had one pair of M3 runs.
- Claude Code 2.1.325 at medium effort, as in every other round. Nothing about the tasks, prompts, data or launch settings changed.
- Benchmark version 0.3.0, which covers rounds 3 and 4 and the change to reporting in tokens processed.

What the round showed:

- **The M3 prediction held on Opus 5.5 in one run of two.** The Code Mode run took 16,744 tokens of task context, against 9,747 in round 2, because one script printed every group of sentences and not only the rare ones.
- **The Code Mode off run repeated round 2's almost exactly:** task context within 2 tokens and the same 11 requests.

## Raw Output

- [`measure.txt`](measure.txt): the output of `bin/measure.py` for all 96 runs
- [`compare.txt`](compare.txt): the output of `bin/measure.py --compare`, the first run of each task, mode and model beside its latest
- [`checks.txt`](checks.txt): the checker's verdict and detail for each run
- [`context/`](context/): Claude Code's own context report for each scripted run, saved after the final answer, without the lists of skills and agents from the tester's account

---

© 2026 Bicameral, LLC. All rights reserved. See [LICENSE](../LICENSE).
