# Results

[README](../README.md) · [Benchmark Guide](../BENCHMARK_GUIDE.md) · [Code Mode Overview](../CODE_MODE_OVERVIEW.md) · [Predictions](../PREDICTIONS.md) · [Results](README.md) · [Changelog](../CHANGELOG.md)

> [!IMPORTANT]
> **Status: four models done, two runs per task and mode, on Claude Code 2.1.326.** Opus 5.5, Sonnet 5.5, Haiku 5.5 and Fable 5.2 have each been run twice on all six tasks. Of 96 runs, 93 passed their checks. Each figure rests on two runs, so read it as a pair of samples, not a settled value. The same benchmark on Claude Code 2.1.325 is [archived](../archive/claude-code-2.1.325/results/README.md).

How the numbers are produced is in the [Benchmark Guide](../BENCHMARK_GUIDE.md). What we expected, written before the runs, is in [PREDICTIONS.md](../PREDICTIONS.md).

## In Short

Across four models, with two runs of each task in each mode, on Claude Code 2.1.326:

- **Tokens processed fell with Code Mode on for every model on the MCP tasks and the control, most where the work was many MCP calls.** Added up by kind of work: 62% to 77% fewer on totalling 120 tickets (M1), 40% to 68% on reading and judging them (M2 and M3), and 29% to 30% on the one-question control (C0), which is the smaller start alone. On file work (T1 and E1) it was 15% to 54% fewer on three models and 9% more on Haiku 5.5, because of one run. Most of these tokens are read from the prompt cache at a lower rate, so this is not cost. See [Tokens Processed by Model](#tokens-processed-by-model).
- **The bullets below use task context, the detail behind that figure.** Task context is how much the conversation grew during the task. It leaves out the start that every request repeats, so its percentages differ from those in tokens processed, and it is what our rule for a real difference is written in.
- **Where the work is many MCP calls and the answer is small, Code Mode cut task context by 84% to 94% on every model.** Adding up 120 tickets fetched through an MCP server (M1) took about 54,000 tokens of conversation with Code Mode off on all four models, and 3,500 to 8,800 with it on. All 16 runs gave the same correct answer. This is the one task-level difference that meets our rule for calling it real without a caveat.
- **Every Code Mode session started about 13,000 tokens smaller, on every model.** That is 29% to 30% of the first request; over a whole C0 run it comes to the 29% to 30% of tokens processed given above, because the task's own tokens do not shrink. The saving was between 13,055 and 13,106 tokens on each of the four.
- **On the two file tasks, Code Mode used more task context in 14 of the 16 pairs of runs, and none of the differences can be told from the noise.** Tokens processed was still lower with Code Mode on in 14 of the 16 pairs, because of the smaller start. The two exceptions are Haiku 5.5's second pairs; in one of them its script ran 344 shell commands that failed. See [How Much Two Identical Runs Differ](#how-much-two-identical-runs-differ).
- **Triage through MCP used 65% to 83% less task context with Code Mode on, and three runs left out tickets.** All three were Haiku 5.5: two of 16 triage runs with Code Mode on and one of 16 with it off. Two of the three turn on two tickets whose reading is open to argument. See [The Three Failed Checks](#the-three-failed-checks).
- **The triage savings rest on patterns in our generated tickets.** All four models found them. They do not show that Code Mode triages free text cheaply.
- **On M1, Code Mode cost 23% to 28% as much and took 20% to 41% of the time,** on the three models whose recorded costs are large enough to compare.
- **Nothing differs from Claude Code 2.1.325 by the rule written before this round.** See [Compared With Claude Code 2.1.325](#compared-with-claude-code-21325).
- **93 of 96 runs passed their checks.** No run started a subagent.

## Setup

| Item                         | Value                                                                                    |
| ---------------------------- | ---------------------------------------------------------------------------------------- |
| Date                         | 2026-11-17 Pacific time, one round from 01:03 to 02:33; `measure.txt` gives times in UTC |
| Claude Code version          | 2.1.326, every run                                                                       |
| Models                       | `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-fable-5-2`           |
| Effort                       | medium, every model                                                                      |
| Fast mode                    | off                                                                                      |
| Configuration                | clean                                                                                    |
| Permission mode              | auto                                                                                     |
| Machine                      | macOS                                                                                    |
| Runs per task and mode       | 2 on every model                                                                         |
| How the sessions were driven | By `bin/run-all.py`, all 96 runs in one round                                            |

## How to Read the Tables

- **Result** is the checker's verdict. A saving only means something if both runs passed.
- **Fixed context** is the tokens sent in the session's first request. **Task context** is the tokens in the last request plus its reply, minus the fixed context. The README [defines both](../README.md#what-is-measured).
- **Tools run** counts every tool Claude Code ran, including those run from Code Mode scripts. **Scripts** is the number of pieces of Code Mode JavaScript.
- **Tokens processed** is every token the model read or wrote over the session: each request's input, whether or not it was read from the prompt cache, plus the output. It grows with the size of the context and with the number of requests, so it carries the smaller start of a Code Mode session into every request. It is the headline measure; task context, requests and fixed context explain it. Most of it is read from the cache at a lower rate, so it is not cost.
- **Total input** (`total_in`), which earlier versions of this page reported, is the same sum without the output. It has been dropped here so that the page has one such measure; [`measure.txt`](measure.txt) still has it.
- **Run** 1 and run 2 are a model's first and second pass through the six tasks, one after the other in the same round.
- **Where a cell shows two figures,** the first run comes first.
- The four models are set side by side first. After that each model has its own table with every run.

## Across the Four Models

Tokens processed comes first, by model, by kind of work and by test. Task context and requests follow as the detail behind it. The two measures give different percentages for the same runs: on M1, tokens processed fell by 62% to 77% and task context by 84% to 94%, because task context leaves out the start that every request repeats.

### Tokens Processed by Model

All runs of a model in one mode, added up. No percentage is given for these totals: they reflect this mix of tasks, three of which make 120 MCP calls each.

| Model      | Tokens processed, off | Tokens processed, on |
| ---------- | --------------------- | -------------------- |
| Opus 5.5   | 5,997,529             | 2,287,014            |
| Sonnet 5.5 | 4,579,107             | 2,108,515            |
| Haiku 5.5  | 4,645,269             | 3,168,935            |
| Fable 5.2  | 4,365,012             | 2,127,454            |

### Tokens Processed by Kind of Work

All runs of the tasks in each group, added up.

| Kind of work                                           | Tasks     | Model      | Tokens processed, off | Tokens processed, on | Change |
| ------------------------------------------------------ | --------- | ---------- | --------------------- | -------------------- | ------ |
| Totalling 120 records fetched through a tool           | M1        | Opus 5.5   | 1,507,193             | 352,663              | -77%   |
| Totalling 120 records fetched through a tool           | M1        | Sonnet 5.5 | 1,158,585             | 379,758              | -67%   |
| Totalling 120 records fetched through a tool           | M1        | Haiku 5.5  | 1,050,522             | 403,613              | -62%   |
| Totalling 120 records fetched through a tool           | M1        | Fable 5.2  | 1,009,826             | 296,418              | -71%   |
| Reading and judging 120 records fetched through a tool | M2 and M3 | Opus 5.5   | 2,983,710             | 968,060              | -68%   |
| Reading and judging 120 records fetched through a tool | M2 and M3 | Sonnet 5.5 | 2,238,566             | 1,142,602            | -49%   |
| Reading and judging 120 records fetched through a tool | M2 and M3 | Haiku 5.5  | 2,223,822             | 1,339,506            | -40%   |
| Reading and judging 120 records fetched through a tool | M2 and M3 | Fable 5.2  | 2,152,993             | 834,743              | -61%   |
| Finding and changing things in files                   | T1 and E1 | Opus 5.5   | 1,330,800             | 842,183              | -37%   |
| Finding and changing things in files                   | T1 and E1 | Sonnet 5.5 | 1,006,208             | 462,461              | -54%   |
| Finding and changing things in files                   | T1 and E1 | Haiku 5.5  | 1,192,131             | 1,298,646            | +9%    |
| Finding and changing things in files                   | T1 and E1 | Fable 5.2  | 1,020,738             | 866,704              | -15%   |
| One question about one file (the control)              | C0        | Opus 5.5   | 175,826               | 124,108              | -29%   |
| One question about one file (the control)              | C0        | Sonnet 5.5 | 175,748               | 123,694              | -30%   |
| One question about one file (the control)              | C0        | Haiku 5.5  | 178,794               | 127,170              | -29%   |
| One question about one file (the control)              | C0        | Fable 5.2  | 181,455               | 129,589              | -29%   |

Haiku 5.5's file work is the one row that rose. Tokens processed was lower with Code Mode on in its first pair of each file task and higher in its second, and the second T1 pair alone, 295,496 off against 487,916 on, outweighs the rest. That run is described under [How Much Two Identical Runs Differ](#how-much-two-identical-runs-differ).

### Tokens Processed by Test

Every pair of runs, the first pair and then the second.

| Task | Model      | Tokens processed, off | Tokens processed, on | Change     |
| ---- | ---------- | --------------------- | -------------------- | ---------- |
| C0   | Opus 5.5   | 87,913 / 87,913       | 61,979 / 62,129      | -29%, -29% |
| C0   | Sonnet 5.5 | 87,883 / 87,865       | 61,847 / 61,847      | -30%, -30% |
| C0   | Haiku 5.5  | 89,423 / 89,371       | 63,718 / 63,452      | -29%, -29% |
| C0   | Fable 5.2  | 90,733 / 90,722       | 64,789 / 64,800      | -29%, -29% |
| T1   | Opus 5.5   | 329,412 / 327,497     | 221,041 / 251,714    | -33%, -23% |
| T1   | Sonnet 5.5 | 181,423 / 137,280     | 98,866 / 94,093      | -46%, -31% |
| T1   | Haiku 5.5  | 333,183 / 295,496     | 243,495 / 487,916    | -27%, +65% |
| T1   | Fable 5.2  | 252,054 / 258,075     | 250,492 / 212,825    | -1%, -18%  |
| E1   | Opus 5.5   | 392,893 / 280,998     | 139,390 / 230,038    | -65%, -18% |
| E1   | Sonnet 5.5 | 274,894 / 412,611     | 136,638 / 132,864    | -50%, -68% |
| E1   | Haiku 5.5  | 311,862 / 251,590     | 275,230 / 292,005    | -12%, +16% |
| E1   | Fable 5.2  | 251,409 / 259,200     | 203,335 / 200,052    | -19%, -23% |
| M1   | Opus 5.5   | 777,116 / 730,077     | 160,056 / 192,607    | -79%, -74% |
| M1   | Sonnet 5.5 | 517,029 / 641,556     | 190,310 / 189,448    | -63%, -70% |
| M1   | Haiku 5.5  | 525,500 / 525,022     | 182,713 / 220,900    | -65%, -58% |
| M1   | Fable 5.2  | 528,284 / 481,542     | 148,779 / 147,639    | -72%, -69% |
| M2   | Opus 5.5   | 730,911 / 730,834     | 218,350 / 217,043    | -70%, -70% |
| M2   | Sonnet 5.5 | 516,945 / 517,124     | 249,960 / 276,402    | -52%, -47% |
| M2   | Haiku 5.5  | 600,215 / 527,740     | 343,446 / 357,393    | -43%, -32% |
| M2   | Fable 5.2  | 528,177 / 528,111     | 194,019 / 206,011    | -63%, -61% |
| M3   | Opus 5.5   | 760,387 / 761,578     | 277,957 / 254,710    | -63%, -67% |
| M3   | Sonnet 5.5 | 537,569 / 666,928     | 286,109 / 330,131    | -47%, -50% |
| M3   | Haiku 5.5  | 549,103 / 546,764     | 350,369 / 288,298    | -36%, -47% |
| M3   | Fable 5.2  | 548,198 / 548,507     | 223,734 / 210,979    | -59%, -62% |

Tokens processed was lower with Code Mode on in 46 of the 48 pairs. The two exceptions are both Haiku 5.5's second pairs: 65% higher on T1 and 16% higher on E1. On C0 it is 29% to 30% lower on every model: that is the smaller start alone, sent with each of the run's two requests.

### Task Context and Requests

Task context is in tokens. "Change" is the change in task context from Code Mode off to on, for the first pair of runs and then the second.

| Task | Model      | Task context, off | Task context, on | Change       | Requests, off | Requests, on |
| ---- | ---------- | ----------------- | ---------------- | ------------ | ------------- | ------------ |
| C0   | Opus 5.5   | 1,961 / 1,961     | 2,257 / 2,386    | +15%, +22%   | 2 / 2         | 2 / 2        |
| C0   | Sonnet 5.5 | 2,153 / 2,153     | 2,267 / 2,277    | +5%, +6%     | 2 / 2         | 2 / 2        |
| C0   | Haiku 5.5  | 2,215 / 2,165     | 2,537 / 2,320    | +15%, +7%    | 2 / 2         | 2 / 2        |
| C0   | Fable 5.2  | 2,159 / 2,160     | 2,327 / 2,332    | +8%, +8%     | 2 / 2         | 2 / 2        |
| T1   | Opus 5.5   | 6,531 / 6,285     | 19,494 / 9,165   | +198%, +46%  | 7 / 7         | 5 / 7        |
| T1   | Sonnet 5.5 | 3,746 / 4,324     | 4,814 / 2,376    | +29%, -45%   | 4 / 3         | 3 / 3        |
| T1   | Haiku 5.5  | 5,808 / 7,598     | 14,194 / 44,839  | +144%, +490% | 7 / 6         | 6 / 9        |
| T1   | Fable 5.2  | 8,800 / 10,238    | 33,484 / 15,159  | +280%, +48%  | 5 / 5         | 5 / 5        |
| E1   | Opus 5.5   | 10,536 / 7,495    | 10,296 / 17,186  | -2%, +129%   | 8 / 6         | 4 / 6        |
| E1   | Sonnet 5.5 | 6,254 / 5,786     | 8,507 / 6,621    | +36%, +14%   | 6 / 9         | 4 / 4        |
| E1   | Haiku 5.5  | 15,702 / 12,637   | 16,969 / 17,947  | +8%, +42%    | 6 / 5         | 7 / 7        |
| E1   | Fable 5.2  | 10,329 / 14,019   | 17,971 / 18,011  | +74%, +28%   | 5 / 5         | 5 / 5        |
| M1   | Opus 5.5   | 54,218 / 53,788   | 3,967 / 4,113    | -93%, -92%   | 12 / 11       | 5 / 6        |
| M1   | Sonnet 5.5 | 53,750 / 54,022   | 3,751 / 3,498    | -93%, -94%   | 8 / 10        | 6 / 6        |
| M1   | Haiku 5.5  | 54,489 / 54,368   | 8,587 / 8,795    | -84%, -84%   | 8 / 8         | 5 / 6        |
| M1   | Fable 5.2  | 53,801 / 53,740   | 8,466 / 8,339    | -84%, -84%   | 8 / 7         | 4 / 4        |
| M2   | Opus 5.5   | 54,253 / 54,203   | 13,525 / 12,464  | -75%, -77%   | 11 / 11       | 6 / 6        |
| M2   | Sonnet 5.5 | 53,725 / 53,845   | 12,820 / 19,038  | -76%, -65%   | 8 / 8         | 7 / 7        |
| M2   | Haiku 5.5  | 55,544 / 55,384   | 17,214 / 17,963  | -69%, -68%   | 9 / 8         | 9 / 9        |
| M2   | Fable 5.2  | 53,869 / 53,856   | 12,858 / 13,835  | -76%, -74%   | 8 / 8         | 5 / 5        |
| M3   | Opus 5.5   | 60,884 / 61,068   | 10,318 / 14,525  | -83%, -76%   | 11 / 11       | 8 / 7        |
| M3   | Sonnet 5.5 | 60,763 / 60,815   | 14,747 / 20,770  | -76%, -66%   | 8 / 10        | 8 / 8        |
| M3   | Haiku 5.5  | 62,784 / 61,712   | 21,023 / 20,101  | -67%, -67%   | 8 / 8         | 9 / 7        |
| M3   | Fable 5.2  | 60,490 / 60,695   | 12,202 / 20,276  | -80%, -67%   | 8 / 8         | 6 / 5        |

- **M1 fell by 84% to 94% in all eight pairs.** With Code Mode off the four models are within 2% of each other, because the same 120 tickets enter the conversation. With it on, Opus 5.5 and Sonnet 5.5 kept the task to about 3,500 to 4,100 tokens, and Haiku 5.5 and Fable 5.2 to about 8,300 to 8,800.
- **M2 and M3 fell by 65% to 83% in all sixteen pairs.** The saving was smallest on Sonnet 5.5 and Haiku 5.5.
- **T1 and E1 rose in 14 of the 16 pairs.** The change ranges from 45% lower to 490% higher.
- **Requests fell on M1 in all eight pairs,** by 25% to 58%. On the other tasks they moved both ways.

### Fixed Context

The tokens in each session's first request. "Share" is the part of that first request Code Mode removes. Over a whole C0 run the same start comes to 29% to 30% of tokens processed, because the task's own tokens do not shrink.

| Model      | Fixed context, off | Fixed context, on | Smaller by, on average | Share |
| ---------- | ------------------ | ----------------- | ---------------------- | ----- |
| Opus 5.5   | 42,931 to 43,223   | 29,826 to 30,117  | 13,106                 | 30%   |
| Sonnet 5.5 | 42,812 to 43,102   | 29,753 to 30,046  | 13,059                 | 30%   |
| Haiku 5.5  | 43,559 to 43,850   | 30,501 to 30,797  | 13,055                 | 30%   |
| Fable 5.2  | 44,237 to 44,531   | 31,183 to 31,477  | 13,057                 | 29%   |

The four models start at slightly different sizes, and Code Mode takes the same 13,000 tokens off each. The saved context reports show where it comes from: built-in tool definitions take 16.3k tokens with Code Mode off and 3.6k with it on.

### Models, Cost and Time

| Model      | Exact model         | Runs | Passed | Recorded cost | M1 cost, off  | M1 cost, on   | M1 seconds, off | M1 seconds, on |
| ---------- | ------------------- | ---- | ------ | ------------- | ------------- | ------------- | --------------- | -------------- |
| Opus 5.5   | `claude-opus-5-5`   | 24   | 24     | $10.30        | $0.88 / $0.86 | $0.20 / $0.21 | 73 / 69         | 15 / 20        |
| Sonnet 5.5 | `claude-sonnet-5-5` | 24   | 24     | $4.77         | $0.41 / $0.42 | $0.10 / $0.10 | 51 / 58         | 21 / 20        |
| Haiku 5.5  | `claude-haiku-5-5`  | 24   | 21     | $0.38         | $0.02 / $0.02 | $0.01 / $0.01 | 35 / 35         | 16 / 13        |
| Fable 5.2  | `claude-fable-5-2`  | 24   | 24     | $19.24        | $1.49 / $1.48 | $0.42 / $0.42 | 76 / 64         | 19 / 13        |

- **Cost is what Claude Code recorded for each session.** Haiku 5.5's recorded costs are a cent or two a run, too small and too coarse to compare the modes. We have not checked any model's recorded cost against a price list.
- **Cost depends on run order,** because the first session of each mode fills the prompt cache. Compare tokens processed, context and requests before cost; tokens processed counts cached and uncached tokens alike, so run order does not move it.
- **The round cost $34.69 as recorded.**

### What Meets Our Rule

The [rule](../README.md#how-a-difference-is-judged): both runs pass, the models differ in the same direction, and task context or requests differ by more than 35%. A measure is too noisy to judge, on a task and model, when two identical runs differ by more than 35%. The rule was written before the runs and is judged on task context and requests only; tokens processed, above, is reported beside it and not judged by it.

| Task | What the four models show                                                                                                                                                                                                                       | Meets the rule?                                                                             |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| C0   | No difference in the task. The session starts about 13,000 tokens smaller on all four                                                                                                                                                           | The start is outside the rule's two measures. It repeated on every model                    |
| T1   | Task context higher with Code Mode on in seven of the eight pairs. Too noisy to judge on all four models: the two Code Mode runs differed by 51% to 216%                                                                                        | No                                                                                          |
| E1   | Task context higher in seven of the eight pairs. Too noisy on Opus 5.5 and Fable 5.2. Sonnet 5.5 rose 36% and 14%; Haiku 5.5 rose 8% and 42%                                                                                                    | No. Neither model that can be judged rose by more than 35% in both pairs                    |
| M1   | Task context 84% to 94% lower in all eight pairs, all passing, repeats within 7%                                                                                                                                                                | **Yes, on all four models**                                                                 |
| M2   | Task context 65% to 77% lower in all eight pairs. Two Haiku 5.5 runs failed their check, one in each mode. Sonnet 5.5's two Code Mode runs differed by 49%, but both were at least 65% below Code Mode off                                      | Yes on Opus 5.5, Sonnet 5.5 and Fable 5.2, with the caveat that the data flatters Code Mode |
| M3   | Task context 66% to 83% lower in all eight pairs. One Haiku 5.5 run with Code Mode on failed its check. The two Code Mode runs differed by 41% to 66% on Opus 5.5, Sonnet 5.5 and Fable 5.2, but every one was at least 66% below Code Mode off | Yes on Opus 5.5, Sonnet 5.5 and Fable 5.2, with the same caveat                             |

## Opus 5.5

Every run, from one round. Fixed context, task context and tokens processed are in tokens.

| Task                                      | Code Mode | Run | Result | Requests | Tools run | Scripts | Seconds | Fixed context | Task context | Tokens processed | Cost (USD) |
| ----------------------------------------- | --------- | --- | ------ | -------- | --------- | ------- | ------- | ------------- | ------------ | ---------------- | ---------- |
| C0 Control                                | off       | 1   | PASS   | 2        | 1         | 0       | 5       | 42,931        | 1,961        | 87,913           | 0.17       |
| C0 Control                                | off       | 2   | PASS   | 2        | 1         | 0       | 3       | 42,931        | 1,961        | 87,913           | 0.16       |
| C0 Control                                | on        | 1   | PASS   | 2        | 1         | 1       | 4       | 29,829        | 2,257        | 61,979           | 0.27       |
| C0 Control                                | on        | 2   | PASS   | 2        | 1         | 1       | 5       | 29,826        | 2,386        | 62,129           | 0.15       |
| T1 Find broken links                      | off       | 1   | PASS   | 7        | 6         | 0       | 44      | 43,221        | 6,531        | 329,412          | 0.33       |
| T1 Find broken links                      | off       | 2   | PASS   | 7        | 6         | 0       | 40      | 43,223        | 6,285        | 327,497          | 0.32       |
| T1 Find broken links                      | on        | 1   | PASS   | 5        | 749       | 4       | 61      | 30,117        | 19,494       | 221,041          | 0.39       |
| T1 Find broken links                      | on        | 2   | PASS   | 7        | 1,174     | 6       | 118     | 30,109        | 9,165        | 251,714          | 0.33       |
| E1 Change an API across 36 call sites     | off       | 1   | PASS   | 8        | 7         | 0       | 36      | 43,005        | 10,536       | 392,893          | 0.35       |
| E1 Change an API across 36 call sites     | off       | 2   | PASS   | 6        | 5         | 0       | 24      | 43,008        | 7,495        | 280,998          | 0.28       |
| E1 Change an API across 36 call sites     | on        | 1   | PASS   | 4        | 44        | 3       | 28      | 29,903        | 10,296       | 139,390          | 0.26       |
| E1 Change an API across 36 call sites     | on        | 2   | PASS   | 6        | 47        | 5       | 35      | 29,897        | 17,186       | 230,038          | 0.36       |
| M1 Aggregate 120 tickets through MCP      | off       | 1   | PASS   | 12       | 125       | 0       | 73      | 43,107        | 54,218       | 777,116          | 0.88       |
| M1 Aggregate 120 tickets through MCP      | off       | 2   | PASS   | 11       | 125       | 0       | 69      | 43,110        | 53,788       | 730,077          | 0.86       |
| M1 Aggregate 120 tickets through MCP      | on        | 1   | PASS   | 5        | 128       | 4       | 15      | 30,005        | 3,967        | 160,056          | 0.20       |
| M1 Aggregate 120 tickets through MCP      | on        | 2   | PASS   | 6        | 129       | 5       | 20      | 30,000        | 4,113        | 192,607          | 0.21       |
| M2 Triage 120 tickets through MCP         | off       | 1   | PASS   | 11       | 125       | 0       | 69      | 43,100        | 54,253       | 730,911          | 0.84       |
| M2 Triage 120 tickets through MCP         | off       | 2   | PASS   | 11       | 125       | 0       | 73      | 43,098        | 54,203       | 730,834          | 0.87       |
| M2 Triage 120 tickets through MCP         | on        | 1   | PASS   | 6        | 130       | 5       | 22      | 29,989        | 13,525       | 218,350          | 0.30       |
| M2 Triage 120 tickets through MCP         | on        | 2   | PASS   | 6        | 130       | 5       | 24      | 29,995        | 12,464       | 217,043          | 0.29       |
| M3 Triage 120 tickets with varied wording | off       | 1   | PASS   | 11       | 125       | 0       | 69      | 43,097        | 60,884       | 760,387          | 0.93       |
| M3 Triage 120 tickets with varied wording | off       | 2   | PASS   | 11       | 125       | 0       | 69      | 43,093        | 61,068       | 761,578          | 0.93       |
| M3 Triage 120 tickets with varied wording | on        | 1   | PASS   | 8        | 131       | 7       | 30      | 29,991        | 10,318       | 277,957          | 0.29       |
| M3 Triage 120 tickets with varied wording | on        | 2   | PASS   | 7        | 131       | 6       | 28      | 29,988        | 14,525       | 254,710          | 0.33       |

All 24 runs passed. No run started a subagent.

In all three MCP tasks, in every run, the server received the same calls in both modes: 3 to list the tickets and 120 to fetch them. Code Mode did the same work, not less.

## How Much Two Identical Runs Differ

Each model ran every task twice in each mode, the second pass straight after the first, with nothing changed. The change in task context from the first run to the second is the yardstick for every difference between modes on this page.

| Task | Code Mode | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 | Fable 5.2 |
| ---- | --------- | -------- | ---------- | --------- | --------- |
| C0   | off       | +0%      | +0%        | -2%       | +0%       |
| C0   | on        | +6%      | +0%        | -9%       | +0%       |
| T1   | off       | -4%      | +15%       | +31%      | +16%      |
| T1   | on        | -53%     | -51%       | +216%     | -55%      |
| E1   | off       | -29%     | -7%        | -20%      | +36%      |
| E1   | on        | +67%     | -22%       | +6%       | +0%       |
| M1   | off       | -1%      | +1%        | -0%       | -0%       |
| M1   | on        | +4%      | -7%        | +2%       | -2%       |
| M2   | off       | -0%      | +0%        | -0%       | -0%       |
| M2   | on        | -8%      | +49%       | +4%       | +8%       |
| M3   | off       | +0%      | +0%        | -2%       | +0%       |
| M3   | on        | +41%     | +41%       | -4%       | +66%      |

What this shows:

- **Fixed context barely moves.** It matched within 9 tokens in every cell, which shows the sessions were started alike; it is set before anything is typed. Requests repeated exactly in 30 of the 48 cells.
- **The MCP tasks with Code Mode off barely move,** within 2% on every model. Those runs fetch the same 120 tickets into the conversation each time.
- **Task context swings widely wherever Claude writes a program,** which is every Code Mode run and both modes of the file tasks. The size depends on how much the program prints back, and in each cell that swung, one result explains most of the gap:
  - **T1 with Code Mode on, Haiku 5.5:** the second run's script looked for files from the wrong folder, and 344 of its 349 shell commands failed with errors such as `ls: 'docs/Reference': No such file or directory`. The run still passed, with 44,839 tokens of task context against 14,194 in its twin. This was Haiku's own mistake in its script; Claude Code refused nothing in it. It also accounts for most of the tool errors in this round: 345 of the 380 in T1 with Code Mode on, against 12 in the same runs on 2.1.325.
  - **T1 with Code Mode on, Opus 5.5:** the first run's first script added about 13,700 tokens; the second run's added about 2,900.
  - **T1 with Code Mode on, Fable 5.2:** one script in the first run printed every link it had set aside as inside an indented block, about 18,400 tokens.
  - **E1 with Code Mode on, Opus 5.5:** one script in the second run returned a report on every file it changed, about 8,600 tokens.
  - **M2 with Code Mode on, Sonnet 5.5:** the second run made a tool search with no limit on its results, which returned the definitions of tools that have nothing to do with the task: about 5,400 tokens, against about 560 for the first run's search. Its second M3 run did the same.
  - **M3 with Code Mode on:** Opus 5.5's second run printed every sentence its keyword filter matched, about 9,400 tokens against about 2,900; Fable 5.2's second run printed every distinct sentence with its tickets, about 11,200 tokens.
- **Request counts are steadier than task context.**

The README's [rule](../README.md#how-a-difference-is-judged) says a measure is too noisy to judge when two identical runs differ by more than 35%. We apply it per task and model. Task context is too noisy to judge on T1 on every model, and on E1 on Opus 5.5 and Fable 5.2. On M2 and M3 several Code Mode repeats differed by 41% to 66%, but every one of those runs was at least 65% below Code Mode off, so the difference between modes is far larger than the spread.

## Sonnet 5.5

Every run, from one round. Fixed context, task context and tokens processed are in tokens.

| Task                                      | Code Mode | Run | Result | Requests | Tools run | Scripts | Seconds | Fixed context | Task context | Tokens processed | Cost (USD) |
| ----------------------------------------- | --------- | --- | ------ | -------- | --------- | ------- | ------- | ------------- | ------------ | ---------------- | ---------- |
| C0 Control                                | off       | 1   | PASS   | 2        | 1         | 0       | 5       | 42,821        | 2,153        | 87,883           | 0.09       |
| C0 Control                                | off       | 2   | PASS   | 2        | 1         | 0       | 4       | 42,812        | 2,153        | 87,865           | 0.08       |
| C0 Control                                | on        | 1   | PASS   | 2        | 1         | 1       | 4       | 29,758        | 2,267        | 61,847           | 0.14       |
| C0 Control                                | on        | 2   | PASS   | 2        | 1         | 1       | 6       | 29,753        | 2,277        | 61,847           | 0.08       |
| T1 Find broken links                      | off       | 1   | PASS   | 4        | 2         | 0       | 21      | 43,102        | 3,746        | 181,423          | 0.12       |
| T1 Find broken links                      | off       | 2   | PASS   | 3        | 2         | 0       | 16      | 43,099        | 4,324        | 137,280          | 0.11       |
| T1 Find broken links                      | on        | 1   | PASS   | 3        | 3         | 2       | 18      | 30,043        | 4,814        | 98,866           | 0.11       |
| T1 Find broken links                      | on        | 2   | PASS   | 3        | 393       | 2       | 27      | 30,046        | 2,376        | 94,093           | 0.09       |
| E1 Change an API across 36 call sites     | off       | 1   | PASS   | 6        | 5         | 0       | 20      | 42,885        | 6,254        | 274,894          | 0.13       |
| E1 Change an API across 36 call sites     | off       | 2   | PASS   | 9        | 8         | 0       | 33      | 42,886        | 5,786        | 412,611          | 0.15       |
| E1 Change an API across 36 call sites     | on        | 1   | PASS   | 4        | 39        | 3       | 27      | 29,834        | 8,507        | 136,638          | 0.13       |
| E1 Change an API across 36 call sites     | on        | 2   | PASS   | 4        | 38        | 3       | 27      | 29,834        | 6,621        | 132,864          | 0.12       |
| M1 Aggregate 120 tickets through MCP      | off       | 1   | PASS   | 8        | 125       | 0       | 51      | 42,992        | 53,750       | 517,029          | 0.41       |
| M1 Aggregate 120 tickets through MCP      | off       | 2   | PASS   | 10       | 125       | 0       | 58      | 42,988        | 54,022       | 641,556          | 0.42       |
| M1 Aggregate 120 tickets through MCP      | on        | 1   | PASS   | 6        | 127       | 5       | 21      | 29,930        | 3,751        | 190,310          | 0.10       |
| M1 Aggregate 120 tickets through MCP      | on        | 2   | PASS   | 6        | 128       | 5       | 20      | 29,929        | 3,498        | 189,448          | 0.10       |
| M2 Triage 120 tickets through MCP         | off       | 1   | PASS   | 8        | 125       | 0       | 52      | 42,986        | 53,725       | 516,945          | 0.41       |
| M2 Triage 120 tickets through MCP         | off       | 2   | PASS   | 8        | 125       | 0       | 52      | 42,978        | 53,845       | 517,124          | 0.41       |
| M2 Triage 120 tickets through MCP         | on        | 1   | PASS   | 7        | 127       | 6       | 29      | 29,920        | 12,820       | 249,960          | 0.15       |
| M2 Triage 120 tickets through MCP         | on        | 2   | PASS   | 7        | 128       | 6       | 23      | 29,921        | 19,038       | 276,402          | 0.18       |
| M3 Triage 120 tickets with varied wording | off       | 1   | PASS   | 8        | 125       | 0       | 57      | 42,980        | 60,763       | 537,569          | 0.44       |
| M3 Triage 120 tickets with varied wording | off       | 2   | PASS   | 10       | 125       | 0       | 55      | 42,983        | 60,815       | 666,928          | 0.45       |
| M3 Triage 120 tickets with varied wording | on        | 1   | PASS   | 8        | 131       | 7       | 30      | 29,919        | 14,747       | 286,109          | 0.16       |
| M3 Triage 120 tickets with varied wording | on        | 2   | PASS   | 8        | 130       | 7       | 32      | 29,923        | 20,770       | 330,131          | 0.19       |

All 24 runs passed.

## Haiku 5.5

| Task                                      | Code Mode | Run | Result | Requests | Tools run | Scripts | Seconds | Fixed context | Task context | Tokens processed | Cost (USD) |
| ----------------------------------------- | --------- | --- | ------ | -------- | --------- | ------- | ------- | ------------- | ------------ | ---------------- | ---------- |
| C0 Control                                | off       | 1   | PASS   | 2        | 1         | 0       | 2       | 43,560        | 2,215        | 89,423           | 0.01       |
| C0 Control                                | off       | 2   | PASS   | 2        | 1         | 0       | 2       | 43,559        | 2,165        | 89,371           | 0.00       |
| C0 Control                                | on        | 1   | PASS   | 2        | 1         | 2       | 4       | 30,501        | 2,537        | 63,718           | 0.01       |
| C0 Control                                | on        | 2   | PASS   | 2        | 1         | 1       | 3       | 30,509        | 2,320        | 63,452           | 0.00       |
| T1 Find broken links                      | off       | 1   | PASS   | 7        | 6         | 0       | 22      | 43,849        | 5,808        | 333,183          | 0.01       |
| T1 Find broken links                      | off       | 2   | PASS   | 6        | 5         | 0       | 25      | 43,850        | 7,598        | 295,496          | 0.01       |
| T1 Find broken links                      | on        | 1   | PASS   | 6        | 705       | 5       | 54      | 30,797        | 14,194       | 243,495          | 0.01       |
| T1 Find broken links                      | on        | 2   | PASS   | 9        | 451       | 8       | 63      | 30,795        | 44,839       | 487,916          | 0.02       |
| E1 Change an API across 36 call sites     | off       | 1   | PASS   | 6        | 21        | 0       | 34      | 43,631        | 15,702       | 311,862          | 0.01       |
| E1 Change an API across 36 call sites     | off       | 2   | PASS   | 5        | 5         | 0       | 29      | 43,631        | 12,637       | 251,590          | 0.01       |
| E1 Change an API across 36 call sites     | on        | 1   | PASS   | 7        | 14        | 6       | 39      | 30,583        | 16,969       | 275,230          | 0.01       |
| E1 Change an API across 36 call sites     | on        | 2   | PASS   | 7        | 79        | 6       | 48      | 30,579        | 17,947       | 292,005          | 0.01       |
| M1 Aggregate 120 tickets through MCP      | off       | 1   | PASS   | 8        | 125       | 0       | 35      | 43,735        | 54,489       | 525,500          | 0.02       |
| M1 Aggregate 120 tickets through MCP      | off       | 2   | PASS   | 8        | 125       | 0       | 35      | 43,740        | 54,368       | 525,022          | 0.02       |
| M1 Aggregate 120 tickets through MCP      | on        | 1   | PASS   | 5        | 126       | 4       | 16      | 30,679        | 8,587        | 182,713          | 0.01       |
| M1 Aggregate 120 tickets through MCP      | on        | 2   | PASS   | 6        | 128       | 5       | 13      | 30,680        | 8,795        | 220,900          | 0.01       |
| M2 Triage 120 tickets through MCP         | off       | 1   | PASS   | 9        | 125       | 0       | 39      | 43,723        | 55,544       | 600,215          | 0.03       |
| M2 Triage 120 tickets through MCP         | off       | 2   | FAIL   | 8        | 125       | 0       | 38      | 43,721        | 55,384       | 527,740          | 0.02       |
| M2 Triage 120 tickets through MCP         | on        | 1   | FAIL   | 9        | 131       | 8       | 27      | 30,669        | 17,214       | 343,446          | 0.01       |
| M2 Triage 120 tickets through MCP         | on        | 2   | PASS   | 9        | 131       | 8       | 29      | 30,669        | 17,963       | 357,393          | 0.01       |
| M3 Triage 120 tickets with varied wording | off       | 1   | PASS   | 8        | 125       | 0       | 40      | 43,727        | 62,784       | 549,103          | 0.06       |
| M3 Triage 120 tickets with varied wording | off       | 2   | PASS   | 8        | 125       | 0       | 36      | 43,725        | 61,712       | 546,764          | 0.06       |
| M3 Triage 120 tickets with varied wording | on        | 1   | PASS   | 9        | 132       | 8       | 30      | 30,668        | 21,023       | 350,369          | 0.01       |
| M3 Triage 120 tickets with varied wording | on        | 2   | FAIL   | 7        | 129       | 6       | 23      | 30,664        | 20,101       | 288,298          | 0.01       |

Three runs failed: M2 with Code Mode on, first run, and M2 with Code Mode off, second run, each of which reported 7 of the 9 tickets; and M3 with Code Mode on, second run, which reported 5 of the 9.

## Fable 5.2

| Task                                      | Code Mode | Run | Result | Requests | Tools run | Scripts | Seconds | Fixed context | Task context | Tokens processed | Cost (USD) |
| ----------------------------------------- | --------- | --- | ------ | -------- | --------- | ------- | ------- | ------------- | ------------ | ---------------- | ---------- |
| C0 Control                                | off       | 1   | PASS   | 2        | 1         | 0       | 7       | 44,243        | 2,159        | 90,733           | 0.33       |
| C0 Control                                | off       | 2   | PASS   | 2        | 1         | 0       | 7       | 44,237        | 2,160        | 90,722           | 0.28       |
| C0 Control                                | on        | 1   | PASS   | 2        | 1         | 1       | 8       | 31,183        | 2,327        | 64,789           | 0.55       |
| C0 Control                                | on        | 2   | PASS   | 2        | 1         | 1       | 8       | 31,185        | 2,332        | 64,800           | 0.28       |
| T1 Find broken links                      | off       | 1   | PASS   | 5        | 4         | 0       | 55      | 44,531        | 8,800        | 252,054          | 0.60       |
| T1 Find broken links                      | off       | 2   | PASS   | 5        | 4         | 0       | 59      | 44,528        | 10,238       | 258,075          | 0.64       |
| T1 Find broken links                      | on        | 1   | PASS   | 5        | 12        | 4       | 97      | 31,477        | 33,484       | 250,492          | 1.20       |
| T1 Find broken links                      | on        | 2   | PASS   | 5        | 8         | 4       | 57      | 31,469        | 15,159       | 212,825          | 0.70       |
| E1 Change an API across 36 call sites     | off       | 1   | PASS   | 5        | 4         | 0       | 35      | 44,311        | 10,329       | 251,409          | 0.52       |
| E1 Change an API across 36 call sites     | off       | 2   | PASS   | 5        | 4         | 0       | 37      | 44,313        | 14,019       | 259,200          | 0.59       |
| E1 Change an API across 36 call sites     | on        | 1   | PASS   | 5        | 43        | 4       | 38      | 31,260        | 17,971       | 203,335          | 0.63       |
| E1 Change an API across 36 call sites     | on        | 2   | PASS   | 5        | 20        | 4       | 41      | 31,261        | 18,011       | 200,052          | 0.64       |
| M1 Aggregate 120 tickets through MCP      | off       | 1   | PASS   | 8        | 125       | 0       | 76      | 44,417        | 53,801       | 528,284          | 1.49       |
| M1 Aggregate 120 tickets through MCP      | off       | 2   | PASS   | 7        | 125       | 0       | 64      | 44,417        | 53,740       | 481,542          | 1.48       |
| M1 Aggregate 120 tickets through MCP      | on        | 1   | PASS   | 4        | 127       | 3       | 19      | 31,359        | 8,466        | 148,779          | 0.42       |
| M1 Aggregate 120 tickets through MCP      | on        | 2   | PASS   | 4        | 127       | 3       | 13      | 31,361        | 8,339        | 147,639          | 0.42       |
| M2 Triage 120 tickets through MCP         | off       | 1   | PASS   | 8        | 125       | 0       | 78      | 44,409        | 53,869       | 528,177          | 1.49       |
| M2 Triage 120 tickets through MCP         | off       | 2   | PASS   | 8        | 125       | 0       | 64      | 44,410        | 53,856       | 528,111          | 1.49       |
| M2 Triage 120 tickets through MCP         | on        | 1   | PASS   | 5        | 127       | 4       | 30      | 31,351        | 12,858       | 194,019          | 0.52       |
| M2 Triage 120 tickets through MCP         | on        | 2   | PASS   | 5        | 128       | 4       | 20      | 31,352        | 13,835       | 206,011          | 0.54       |
| M3 Triage 120 tickets with varied wording | off       | 1   | PASS   | 8        | 125       | 0       | 76      | 44,409        | 60,490       | 548,198          | 1.60       |
| M3 Triage 120 tickets with varied wording | off       | 2   | PASS   | 8        | 125       | 0       | 65      | 44,411        | 60,695       | 548,507          | 1.61       |
| M3 Triage 120 tickets with varied wording | on        | 1   | PASS   | 6        | 129       | 5       | 35      | 31,349        | 12,202       | 223,734          | 0.54       |
| M3 Triage 120 tickets with varied wording | on        | 2   | PASS   | 5        | 128       | 4       | 27      | 31,347        | 20,276       | 210,979          | 0.68       |

All 24 runs passed.

## Against the Predictions

This repository's history begins after the runs, so it does not show when the predictions were written. For the record: the first five were written before the first round on Claude Code 2.1.325, M3's was written after that round and before any M3 run, and one line in PREDICTIONS.md, marked "Settled", was added after the runs. The prediction for Claude Code 2.1.326 was written after the update and before any run on it. That is our statement, not proof.

The table below sets the original predictions, one per task, against what happened on Claude Code 2.1.326. How they fared on 2.1.325 is in the [archived results](../archive/claude-code-2.1.325/results/README.md#against-the-predictions); on both versions M1 held, M2's saving was far larger than predicted, and the file tasks gave no saving in the conversation.

| Task | Predicted                                                                                                  | What happened on Claude Code 2.1.326                                                                                                                                                                                                                              | Prediction held?                                                                |
| ---- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| C0   | None in the answer. A small fixed cost or saving in how large the session starts                           | Same answer in all 16 runs. The session started about 13,000 tokens smaller with Code Mode on, on every model, which is more than "small"                                                                                                                         | Partly                                                                          |
| T1   | No material difference in task context. Possibly fewer requests                                            | No saving on any model. Task context was higher with Code Mode on in seven of the eight pairs, but too noisy to judge on every model. Fewer requests in three pairs, more in one                                                                                  | Partly. No saving, as predicted; the rise in context cannot be told from noise  |
| E1   | A moderate reduction in requests and task context, or none                                                 | Task context higher in seven of the eight pairs, by up to 129%. Requests fewer in three pairs, equal in three, and more in both of Haiku 5.5's                                                                                                                    | Partly. "None" for requests; task context went the other way                    |
| M1   | A large reduction in task context and requests. Same correct answer                                        | Task context 84% to 94% lower and requests fewer in all eight pairs. Same correct answer in all 16 runs                                                                                                                                                           | Yes                                                                             |
| M2   | A small reduction at best. Accuracy may be lower                                                           | Task context 65% to 77% lower on all four models. Two Haiku 5.5 runs left out two tickets, one with Code Mode on and one with it off                                                                                                                              | No on the size. Accuracy was lower once with Code Mode on, and once with it off |
| M3   | A smaller reduction than M2 showed, or a missed ticket, or both. Well over 12,500 tokens with Code Mode on | The reduction was within four points of M2's on every model, and larger on Opus 5.5. Six of the eight Code Mode runs took more than 12,500 tokens, from 14,525 to 21,023; one Opus 5.5 run and one Fable 5.2 run took less. One Haiku 5.5 run missed four tickets | Partly. A missed ticket on one model; no smaller reduction                      |

On 2.1.325 the M3 prediction held on three models and, on Opus 5.5, in one run of two. On 2.1.326 it held less well: the reduction on M3 was as large as on M2, and the one missed ticket came from a keyword filter, as the prediction said it might.

One estimate behind a prediction was off. We expected M1 with Code Mode off to put about 30,000 tokens of tickets into the conversation; it put about 54,000, on every model, on both versions.

### Against the 2.1.326 Prediction

Written after Claude Code was updated to 2.1.326 and before any run on it, in [PREDICTIONS.md](../PREDICTIONS.md#claude-code-21326-added-before-its-round).

| Predicted                                                                                                                                                            | Result                                                                                                                                                  | Verdict                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| Fixed context: Code Mode sessions still start about 13,000 smaller; each mode within 10% of 2.1.325                                                                  | Median of all runs: off 43,302 to 43,391, on 30,313 to 30,309. Start smaller by 13,055 to 13,106 per model (2.1.325: 12,965 to 13,015)                  | Held                                    |
| Code Mode off: no difference beyond noise                                                                                                                            | No task meets the cross-version rule with Code Mode off                                                                                                 | Held                                    |
| T1 Code Mode on: all eight pass; any `$` refusal shows as an error and a retry                                                                                       | All eight passed. No `$` refusal found. One auto-mode refusal in one Fable 5.2 run, of a command that contained a `\uXXXX` escape, which Claude rewrote | Held                                    |
| E1 Code Mode on: all eight pass, no difference beyond noise                                                                                                          | All eight passed; under the rule one model up, one down                                                                                                 | Held                                    |
| M1: at least 80% less task context with Code Mode on in all eight pairs                                                                                              | 84% to 94% in every pair                                                                                                                                | Held                                    |
| M2 and M3: large reduction; failures only for the same reasons as before, never a missing ticket                                                                     | Large reduction on every model; every run fetched 120 of 120; but one failure came with Code Mode off, which was not predicted                          | Mostly held                             |
| No stalled runs                                                                                                                                                      | None                                                                                                                                                    | Held                                    |
| Cross-version rule: a difference counts only if larger than the gap between repeat runs on either version and in the same direction on at least three of four models | No task and mode met it on task context                                                                                                                 | No real difference between the versions |

The one miss is a failed check with Code Mode off. Every earlier failure had been with Code Mode on, and the prediction assumed failures would stay there.

## Compared With Claude Code 2.1.325

The [same benchmark on Claude Code 2.1.325](../archive/claude-code-2.1.325/results/README.md) ran the same six tasks on the same four models, twice in each mode, at the same effort. Nothing about the tasks, prompts, data or launch settings changed between the two.

**The rule,** written before the 2.1.326 round: compare by model, task and mode, using the two runs on each version. A difference counts only if it is larger than the gap between the two runs on either version, and it is real only if it points the same way on at least three of the four models. Results from the two versions are never added together.

Applied to task context, the measure the rule is written in:

| Task | Code Mode | Models higher on 2.1.326 | Models lower on 2.1.326 | A real difference? |
| ---- | --------- | ------------------------ | ----------------------- | ------------------ |
| C0   | off       | 2                        | 0                       | No                 |
| C0   | on        | 0                        | 0                       | No                 |
| T1   | off       | 1                        | 0                       | No                 |
| T1   | on        | 0                        | 0                       | No                 |
| E1   | off       | 0                        | 0                       | No                 |
| E1   | on        | 1                        | 1                       | No                 |
| M1   | off       | 0                        | 1                       | No                 |
| M1   | on        | 2                        | 0                       | No                 |
| M2   | off       | 1                        | 1                       | No                 |
| M2   | on        | 2                        | 1                       | No                 |
| M3   | off       | 0                        | 0                       | No                 |
| M3   | on        | 0                        | 1                       | No                 |

**No task and mode differs between the versions.** In no cell did more than two of the four models move the same way beyond their run-to-run gap; the rule needs three. One move that stands out, Fable 5.2 on M1 with Code Mode on, from about 3,600 tokens of task context to about 8,400, is one of two models up and so counts as noise by the rule.

Other things that changed and do not change how a number is read:

- **The start is the same size.** Code Mode sessions started 13,055 to 13,106 tokens smaller, against 12,965 to 13,015 on 2.1.325. The median first request of all runs was 43,391 tokens with Code Mode off and 30,309 with it on, against 43,302 and 30,313.
- **Checks passed:** 93 of 96, against 94 of 96. Sonnet 5.5 passed all 24, against 23; Haiku 5.5 passed 21, against 23. All five failed checks across the two versions left out the same two tickets.
- **Tool errors** in T1 with Code Mode on rose from 12 to 380, and 345 of them are in one Haiku 5.5 run, described [above](#how-much-two-identical-runs-differ). Elsewhere the counts are similar.
- **No refusal of the `$` helper** was found, which the 2.1.326 changelog made possible. Auto mode stopped one command in one Fable 5.2 run, because it contained a `\uXXXX` escape; Claude rewrote it and the run passed.

## What Claude Did

Taken from the saved transcripts and the scripts in them. The table is Opus 5.5; where the two runs differed, both are given. The other models follow it.

| Task | Code Mode off                                                                                                                       | Code Mode on                                                                                                                                                                                                                                                                                                              |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C0   | One shell command to read the file                                                                                                  | One script that read the file                                                                                                                                                                                                                                                                                             |
| T1   | Wrote a Python checker to a scratch file and ran it. Six shell commands in both runs                                                | Four scripts in run 1 and six in run 2. They read every file, set aside code blocks, and ran a separate shell check for each link: 699 shell calls in run 1 and 1,034 in run 2. Run 1's first script added about 13,700 tokens to the conversation; run 2's added about 2,900                                             |
| E1   | Read the files with shell commands, then wrote and ran a script that rewrote the call sites. Seven commands in run 1, five in run 2 | Run 1: three scripts, one to look around, one to read every file, one to rewrite the calls by splitting their arguments. Run 2: five scripts, one of which returned a report on every file changed and added about 8,600 tokens                                                                                           |
| M1   | Fetched the 120 tickets one call each, in parallel batches, so every ticket passed through the conversation                         | Searched for the tools, then one script fetched all 120 and a later one filtered them and returned the answer                                                                                                                                                                                                             |
| M2   | Fetched all 120 tickets and read them                                                                                               | Kept the tickets in a variable between scripts, split each into sentences, counted each sentence across all tickets and read only the rare ones. The same in both runs                                                                                                                                                    |
| M3   | Fetched all 120 tickets and read them                                                                                               | Kept the tickets in a variable. Pulled out sentences matching a list of billing words, then replaced days, months, names and numbers with placeholders and grouped the sentences that became identical. Both runs took these steps; run 2's keyword filter printed more and added about 9,400 tokens, against about 2,900 |

In no task did Claude edit files one at a time or start a subagent, in either mode. On both file tasks it wrote a program to do the work, with Code Mode off as well as on.

### On the Other Models

We read the transcripts of the three failed runs, their passing twins, and the runs where the numbers stood out, and searched the scripts of every triage run with Code Mode on. The search reads the key lines of each script, which is cruder than reading the whole transcript.

- **File tasks:** every model wrote a program in both modes, as Opus 5.5 did. With Code Mode on the same kind of program arrives wrapped in a script.
- **MCP tasks:** every run fetched all 120 tickets through the server. Of the 48 MCP runs, 45 made the same 123 calls. Three runs with Code Mode on made one more: two Sonnet 5.5 runs and one Fable 5.2 run.
- **Triage with Code Mode on, M2:** seven of the eight runs split the tickets into sentences and counted each sentence across all tickets. The eighth, Haiku 5.5's first, filtered sentences by billing words, printed the doubtful tickets and judged against them; it is one of the failed checks.
- **Triage with Code Mode on, M3:** Opus 5.5 and Fable 5.2 masked the details and grouped the sentences in both runs. Sonnet 5.5 set aside sentences that matched common patterns in one run and used a broad keyword filter in the other, and both passed. Haiku 5.5 filtered by keywords in both runs, and the second is a failed check.
- **No run on any model started a subagent.**

## The Three Failed Checks

All three are Haiku 5.5 on the triage tasks, and every one fetched all 120 tickets. None named a wrong ticket; each left some out.

| Run                                      | Answer             | What happened                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ---------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Haiku 5.5, M2, Code Mode on, first run   | 7 of 9, none wrong | It left out `TCK-1060` and `TCK-1071` and called that "the one judgment call". Both say "The add-on appears on two consecutive receipts though it was bought once."                                                                                                                                                                                                                                                                                           |
| Haiku 5.5, M2, Code Mode off, second run | 7 of 9, none wrong | The same two left out, with the same reasoning. It said the count would be 9 if a duplicated receipt counts                                                                                                                                                                                                                                                                                                                                                   |
| Haiku 5.5, M3, Code Mode on, second run  | 5 of 9, none wrong | Its script filtered the tickets by keyword, then by a second pattern of payment words. It left out `TCK-1060` and `TCK-1071`, and also `TCK-1004` and `TCK-1036`, which describe a real second charge in other words. In M2's wording, `TCK-1004` reads "A single upgrade was taken from the account and then taken a second time the next morning". Most likely the filter kept these two from being read closely; we have not confirmed it ticket by ticket |

- **Two of the three turn on `TCK-1060` and `TCK-1071`,** and so did both failures on Claude Code 2.1.325: Sonnet 5.5's failed M3 run missed exactly these two behind a keyword filter, and Haiku 5.5's failed M2 run left them out by the same reading as this round. The third failure here left them out too. Every failed check on either version, five in all, on two models and in both modes, left out these two tickets. Every passing Haiku 5.5 run on 2.1.326 counted them and flagged them as uncertain. The answer key's reading of them is open to argument.
- **The answer key is unchanged.** Changing it would make every earlier result not comparable with later ones. A run that leaves these two tickets out fails, as before; read its failure as a judgement on two doubtful tickets, not as a missed record.
- **The third is the failure our M3 prediction named.** A script that filters by keywords drops the tickets worded without them.
- **One failure came with Code Mode off,** for the first time. Three failures in 96 runs, all on one model, are too few to state a rate.

## What the M2 Result Does and Does Not Show

Claude's Code Mode runs on M2 found all nine tickets, apart from one Haiku 5.5 run, while reading about a quarter to a third as much. It did so by noticing that the tickets were assembled from a small set of repeated sentences: across 120 tickets there are only 31 distinct sentences, so listing each one once is far shorter than reading every ticket.

That is good work by the model, and a fault in our test data. Real support tickets do not repeat their sentences. So the M2 result shows that Code Mode lets a model exploit repetition in data; it does not show that Code Mode can triage free text cheaply.

Task M3 was added for that reason. It asks the same question of the same tickets, reworded so that sentences do not repeat: 875 distinct sentences in place of 31. M2 is kept as it was, with its result, and M3 has its own prediction, written before it was run.

On Claude Code 2.1.326, seven of the eight Code Mode runs on M2 counted the sentences across all tickets in this way; on 2.1.325 every model did so in at least one of its runs.

## What the M3 Result Does and Does Not Show

M3 has the same fault in a weaker form. Its 875 distinct sentences were made by filling details into 31 sentence patterns: a day, a month, a number, a job title, a part of the product, a city. Two sentences from one pattern differ only in those details.

With Code Mode on, Opus 5.5 took two steps in both runs. A keyword filter found the telling sentence in some of the nine tickets. Then it masked the details that vary, grouped the sentences that became identical, and printed only the rare groups. The sentences that describe a real double charge are rare, so they appeared, and the other tickets were found. Fable 5.2 masked and grouped in both runs as well. Its scripts processed all 120 tickets; the conversation received the keyword matches and the rare groups.

Our prediction named two ways a script could go: return most of the text, or filter by keywords and miss tickets. Haiku 5.5's second Code Mode run took the second way and missed four of nine. We did not foresee the third way, masking and grouping, when we wrote the prediction; it first appeared on Claude Code 2.1.325.

So M3 shows what M2 showed: Code Mode lets a model find and exploit structure in generated data. It still does not show whether Code Mode can triage free text cheaply. A task that tests that needs tickets written one by one, with no shared patterns. That task is not built.

## Screenshots

None yet. Files go in `screenshots/`, named by task, model and mode, such as `M1-opus-off-end.png`.

## Limits of This Result

- **Two runs behind each figure.** Two samples show that a figure can move; they do not measure how far it usually moves.
- **One effort level, one Claude Code version.** Every run used medium effort on 2.1.326. The same benchmark on 2.1.325 is archived and compared above; the two are never added together.
- **Task context on the file tasks is too noisy to judge on most models,** as shown above.
- **The totals by model reflect this mix of tasks.** Three of the six make 120 MCP calls each, which is where Code Mode does best. For file work, read the file-work rows, not the totals.
- **One run can move a model's file-work total.** Haiku 5.5's file work rose with Code Mode on because of one run whose script failed 344 shell commands.
- **Tokens processed is not cost.** Most of these tokens are read from the prompt cache, which is billed at a lower rate.
- **The answer key for M2 and M3 has one doubtful wording,** the add-on on two consecutive receipts. A model that reads it as a receipt and not a charge fails the check. Two of this round's three failures turn on it.
- **Recorded costs are Claude Code's own figures,** not checked against a price list, and Haiku 5.5's are too small to compare.
- **Cost depends on run order.** The first session of each mode has to fill Claude Code's prompt cache. Fable 5.2's C0 run with Code Mode on cost $0.55 in its first pass, when it was the first Code Mode session, and $0.28 in its second. Compare tokens processed, context and requests before cost.
- **Part of every session's start comes from the tester's Claude account.** Skills and custom agents take about 10,400 tokens of fixed context, in both modes alike. Some are built into Claude Code; the rest come from plugins synced to the account, which load even in the clean configuration. We cannot say how the 10,400 divides, so your fixed context may differ by up to that much. None of it reached a result that we can find: the unrelated tools that the broad tool searches in M2 and M3 returned are built into Claude Code.
- **Task context counts the main conversation only.** No run used a subagent, so nothing is hidden by that here.
- **M2 and M3 rest on generated data with structure a script can find,** as described above.

## Run Log

What was run in each round, and what changed before the next. The [changelog](../CHANGELOG.md) records the same changes by version. Rounds 1 to 4 ran on Claude Code 2.1.325; their results are in the [archived benchmark](../archive/claude-code-2.1.325/results/README.md), and their entries are kept here as the history of the benchmark.

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
- The noise rule's per-task reading, used on this page, is written into the [README](../README.md#how-a-difference-is-judged).

### Round 3: Sonnet 5.5, Haiku 5.5 and Fable 5.2, 2026-11-16

- 72 runs: all six tasks, off then on, twice for each model, typed by `REPEAT=2 bin/run-all.py sonnet claude-haiku-5-5 fable`. Each model finished both passes before the next began.
- It took one hour: 18 minutes for Sonnet 5.5, 20 for Haiku 5.5 and 21 for Fable 5.2. The script needed no help and did not stall.
- 70 of the 72 passed. The two that failed are described under [The Two Failed Checks](../archive/claude-code-2.1.325/results/README.md#the-two-failed-checks) in the archived results.
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

### Changes Before Round 5

Nothing that changes how a session runs: the tasks, prompts, data and launch settings are as they were. Benchmark version 0.3.0, unchanged.

- Claude Code was updated from 2.1.325 to 2.1.326. A prediction for the new version, with the rule for comparing two versions, was written before any run on it.
- New scripts check a set of runs before its results are published (`bin/validate.py`), keep the published benchmark whole in `archive/` and put a checked run in its place (`bin/archive.py`), and report one Claude Code version at a time (`bin/measure.py --claude-code`). The steps are in [ARCHIVING.md](../ARCHIVING.md).

### Round 5: All Four Models on Claude Code 2.1.326, 2026-11-17

- 96 runs: all six tasks, off then on, twice for each of the four models, typed by `bin/run-all.py` into `new_run/`, so the published results did not change until the new set had been checked.
- It took about an hour and a half, from 01:03 to 02:33 Pacific time. The script needed no help, and no run stalled; the longest took 118 seconds.
- 93 of the 96 passed. The three that failed are described under [The Three Failed Checks](#the-three-failed-checks).
- Every run used Claude Code 2.1.326 at medium effort. `bin/validate.py` found the set complete and consistent: one effort level and one speed, two runs of every task and mode on every model, every MCP run fetching all 120 tickets from one server process, no subagents, and a context report for each of the 96 runs.
- Before the new results were put in place, the 2.1.325 benchmark was archived whole in `archive/claude-code-2.1.325/` and the archive verified.

What the round showed:

- **The benchmark runs unchanged on a new Claude Code version.** No task or setting needed a change, and no run stopped at a permission question.
- **The two versions give the same results within the noise,** by the rule written before the round. See [Compared With Claude Code 2.1.325](#compared-with-claude-code-21325).
- **Every failed check on either version left out the two tickets with the doubtful wording,** five runs on two models, in both modes.
- **One run can carry a model's total.** Haiku 5.5's file work cost more with Code Mode on because one script failed hundreds of shell commands.

## Raw Output

- [`measure.txt`](measure.txt): the output of `bin/measure.py` for all 96 runs on Claude Code 2.1.326
- [`compare.txt`](compare.txt): the output of `bin/measure.py --compare`, the first run of each task, mode and model beside its latest
- [`checks.txt`](checks.txt): the checker's verdict and detail for each run
- [`context/`](context/): Claude Code's own context report for each run, saved after the final answer, without the lists of skills and agents from the tester's account

---

© 2026 Bicameral, LLC. All rights reserved. See [LICENSE](../LICENSE).
