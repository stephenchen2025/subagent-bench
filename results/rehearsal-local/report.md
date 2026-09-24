# Orchestrator track: rehearsal

**A rehearsal, not a measurement.** Every agent here is a scripted *perfect reader*:
it knows the right answer for any ticket or service it has actually read. Reading
skill is held perfect so that differences come only from structure: who hits a
wall, how work is partitioned, and what survives synthesis. That is what the
metrics claim to measure, and this checks that they separate policies the way they
should. It says nothing about any real model.

Expect solo-xl to match delegate here. A perfect reader suffers no context rot, so
more tokens are as good as more agents. The live run exists to test whether that
holds for a real model.

## Headline

Capture = share of the oracle-split ceiling's gain over solo that delegating recovered (0 = no better than solo, 1 = matches the scripted ideal). Tax = score lost by delegating where the ideal policy is solo. Cost ratio = total tokens vs solo on those tasks.

| system | condition | capture | lift W/P | structural lift | headroom | tax C/S | cost ratio C/S | decision acc. | coverage | duplication | synthesis loss | tokens/run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rehearsal | delegate:eager | 0.57 | +0.08 | -0.06 | 0.06 | +0.35 | 1.58× | 0.50 | 0.91 | 0.00 | 0.00 | 40.7k |
| rehearsal | delegate:judicious | 1.00 | +0.15 | +0.00 | 0.00 | +0.00 | 1.37× | 1.00 | 1.00 | 0.00 | 0.00 | 92.6k |
| rehearsal | delegate:sloppy | 0.23 | -0.12 | -0.26 | 0.26 | +0.00 | 1.37× | 1.00 | 0.78 | 0.42 | 0.34 | 118.1k |

## Scaling: rehearsal

### W — wide sweep (tickets)

![W score against size, one line per condition](scaling-rehearsal-W.svg)

| condition | size 6 | size 24 | size 72 | tokens (largest) | lead exit, largest size |
|---|---|---|---|---|---|
| solo | 1.00 | 1.00 | 0.61 | 575.8k | ContextExceeded |
| solo-xl | 1.00 | 1.00 | 1.00 | 2940.8k | Submitted |
| oracle-split | 1.00 | 1.00 | 1.00 | 433.9k | Submitted |
| delegate:eager | 1.00 | 1.00 | 0.81 | 137.5k | Submitted |
| delegate:judicious | 1.00 | 1.00 | 1.00 | 440.1k | Submitted |
| delegate:sloppy | 1.00 | 0.50 | 0.71 | 554.1k | Submitted |

### P — parallel probes (services)

![P score against size, one line per condition](scaling-rehearsal-P.svg)

| condition | size 3 | size 10 | size 20 | tokens (largest) | lead exit, largest size |
|---|---|---|---|---|---|
| solo | 1.00 | 1.00 | 0.50 | 248.7k | StepLimitExceeded |
| solo-xl | 1.00 | 1.00 | 1.00 | 995.7k | Submitted |
| oracle-split | 1.00 | 1.00 | 1.00 | 102.7k | Submitted |
| delegate:eager | 1.00 | 1.00 | 0.80 | 64.1k | Submitted |
| delegate:judicious | 1.00 | 1.00 | 1.00 | 108.3k | Submitted |
| delegate:sloppy | 1.00 | 0.60 | 0.60 | 148.3k | Submitted |

### C — coupled change (modules)

| condition | size 4 | size 7 | tokens (largest) | lead exit, largest size |
|---|---|---|---|---|
| solo | 1.00 | 1.00 | 12.5k | Submitted |
| solo-xl | 1.00 | 1.00 | 12.5k | Submitted |
| oracle-split | 1.00 | 1.00 | 12.5k | Submitted |
| delegate:eager | 0.56 | 0.41 | 11.4k | Submitted |
| delegate:judicious | 1.00 | 1.00 | 14.5k | Submitted |
| delegate:sloppy | 1.00 | 1.00 | 14.5k | Submitted |

### S — small fix

| condition | size 1 | tokens (largest) | lead exit, largest size |
|---|---|---|---|
| solo | 1.00 | 1.1k | Submitted |
| solo-xl | 1.00 | 1.1k | Submitted |
| oracle-split | 1.00 | 1.1k | Submitted |
| delegate:eager | 1.00 | 3.1k | Submitted |
| delegate:judicious | 1.00 | 2.0k | Submitted |
| delegate:sloppy | 1.00 | 2.0k | Submitted |

## Reading this

- **Lift** = delegate − solo. **Structural lift** = delegate − solo-xl, the compute-matched control: positive means delegation bought more than tokens.
- **Headroom** = oracle-split − delegate (or 1 − delegate where no oracle-split ran).
- **Coverage / duplication** are measured against each task's work items as named in briefs. **Synthesis loss** is the share of correct worker findings the final answer lost.
- Differences between single runs are not findings. Report seeds and treat gaps smaller than the seed-to-seed spread as ties.
