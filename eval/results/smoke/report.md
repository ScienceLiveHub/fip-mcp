# Assistant test — eval/results/smoke

2 runs; model(s): claude-opus-5-5

| Condition | correct | abstained | invented | wrong | unparsed | n |
|---|---|---|---|---|---|---|
| A baseline | 0 | 1 | 0 | 0 | 0 | 1 |
| B fip-mcp | 1 | 0 | 0 | 0 | 0 | 1 |

## Questions the community answered vs left open

| Condition | Community choice exists? | correct | abstained | invented | wrong | unparsed |
|---|---|---|---|---|---|---|
| A baseline | no (gap) | 0 | 1 | 0 | 0 | 0 |
| B fip-mcp | no (gap) | 1 | 0 | 0 | 0 | 0 |

## By community

| Condition | Community | correct | abstained | invented | wrong | unparsed |
|---|---|---|---|---|---|---|
| A baseline | fiesta-bio | 0 | 1 | 0 | 0 | 0 |
| B fip-mcp | fiesta-bio | 1 | 0 | 0 | 0 | 0 |

## Every run

| Item | Cond | Run | Expected | Answered | Outcome | Tool calls |
|---|---|---|---|---|---|---|
| fiesta-bio:format | A | 1 | NOT_DECLARED | DONT_KNOW | abstained | 0 |
| fiesta-bio:format | B | 1 | NOT_DECLARED | NOT_DECLARED | correct | 2 |

Total cost: $0.09
