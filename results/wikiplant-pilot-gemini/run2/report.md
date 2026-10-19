# wikiplant pilot run

Puzzles designed: 1. Design or writing failures: 2. Manifest units: 3 {'gold': 1, 'decoy': 2}.
Shippable (all nine gates pass): 0. Human review is not run in this pilot, so nothing is shippable yet.

## Gate pass rates

| gate | pass | tried |
|---|---|---|
| name_collision | 1 | 1 |
| lexical_shortcut | 0 | 1 |
| closed_book | 1 | 1 |
| oracle | 1 | 1 |
| oracle_distractors | 1 | 1 |
| consistency | 0 | 1 |
| base_corpus | 1 | 1 |
| style | 0 | 1 |
| human_review | 0 | 0 |

## Puzzles

### p01 (easy, chain)

**Q:** Which merchant owned a cloth mill in 1824 in the parish that includes the now uninhabited village of Imber?

**A:** Jedidiah Thwaite (aliases: Jedidiah Thwaite, J. Thwaite, Thwaite)

- name_collision: **pass**
- lexical_shortcut: **fail** final-hop gold BM25 rank 11, tier band 2-10 {'bm25_rank': 11}
- closed_book: **pass**
- oracle: **pass**  {'accuracy': 1.0}
- oracle_distractors: **pass**  {'accuracy': 1.0, 'distractors': 2}
- consistency: **fail** p01-gold-f2: The text states that by the early nineteenth century Westfield still consisted mostly of rural land with little residential development, and it only developed into a populous area and was recognized as a settlement later in the nineteenth and early twentieth centuries.; p01-decoy-04: In the 1890s, the property was owned by furniture maker Fritz Hansen and used as a home for veterans, not as a coal supplier.
- base_corpus: **pass**
- style: **fail** judge picked the planted paragraph 1.00 vs chance 0.25 {'accuracy': 1.0, 'p_value': 0.000244140625}
- human_review: **pending** awaiting human review

Planted units:

- `p01-gold-f2` (gold, page 2567360, gemini-3.5-flash-lite): Jedidiah Thwaite owned a cloth mill in Heytesbury in 1824. The settlement continued to develop through the early nineteenth century alongside traditional agricultural pursuits and local manufacturing ventures within the surrounding Wiltshire countryside.
- `p01-decoy-02` (decoy, page 13486919, gemini-3.5-flash-lite): Local support and charitable fundraising occurred during the nineteenth century. Stavenholme Mechanics' Institute raised a subscription for Keal Cotes in 1846. This financial assistance contributed to local welfare initiatives within the rural parish community during a period of agricultural transition and development across the wider region. Such philanthropic efforts were typical of the era, providing necessary relief and support to small settlements situated on the edge of the fens where employment opportunities and local resources remained limited throughout the Victorian period.
- `p01-decoy-04` (decoy, page 36759221, gemini-3.5-flash-lite): In 1898, the property engaged in commercial transactions when the Thrushcombe Coal and Navigation Company bought coal from Brøste House. This trade reflected the varied commercial activities taking place in the buildings along the canal before the premises were later adapted for other cultural and residential purposes.

## Failures before the gates

- p02 (design): fact f1: para_id 9898493:infobox does not exist; cite one from the brief; fact f2: host page 3228118 is not a host-eligible page; fact f2: page 3228118 is outside the cluster; fact f3: host page 26425723 is not a host-eligible page; fact f3: page 26425723 is outside the cluster
- p03 (design): puzzle p03: real fact f1 must cite a para_id; puzzle p03: real fact f2 must cite a para_id; puzzle p03: real fact f5 must cite a para_id; puzzle p03: real fact f6 must cite a para_id

## Model usage

| model | calls | tokens | retries |
|---|---|---|---|
| gemini-3-flash-preview | 10 | 251067 | 6 |
| gemini-3.1-flash-lite | 8 | 2174 | 1 |
| gemini-3.5-flash-lite | 30 | 49915 | 0 |
| gemini-3.6-flash | 2 | 4254 | 0 |
| gemini-3.7-flash | 6 | 9926 | 1 |

Wall time: 28.5 min.
