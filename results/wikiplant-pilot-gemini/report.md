# wikiplant pilot run

Puzzles designed: 2. Design or writing failures: 1. Manifest units: 15 {'gold': 3, 'decoy': 11, 'near_miss': 1}.
Shippable (all nine gates pass): 0. Human review is not run in this pilot, so nothing is shippable yet.

## Gate pass rates

| gate | pass | tried |
|---|---|---|
| name_collision | 2 | 2 |
| lexical_shortcut | 0 | 2 |
| closed_book | 2 | 2 |
| oracle | 2 | 2 |
| oracle_distractors | 2 | 2 |
| consistency | 0 | 2 |
| base_corpus | 2 | 2 |
| style | 0 | 2 |
| human_review | 0 | 0 |

## Puzzles

### p01 (easy, chain)

**Q:** Who was appointed as the head porter in 1857 at the station in the historic market town on the western edge of Salisbury Plain that is a stop on the railway line completed in 1856 between Westbury and Salisbury?

**A:** Cuthbert Entwistle (aliases: Entwistle, Mr. Entwistle, C. Entwistle)

- name_collision: **pass**
- lexical_shortcut: **fail** final-hop gold BM25 rank 24, tier band 2-10 {'bm25_rank': 24}
- closed_book: **pass**
- oracle: **pass**  {'accuracy': 1.0}
- oracle_distractors: **pass**  {'accuracy': 1.0, 'distractors': 4}
- consistency: **fail** p01-decoy-03: Navigation ceased in the 1850s and the channel to the coal wharf had disappeared altogether by 1891, contradicting the claim that the wharf was leased in 1895.; p01-decoy-04: The Stonehaven derailment did not happen until 12 August 2020, so a survey of it could not have been published in 1879.
- base_corpus: **pass**
- style: **fail** judge picked the planted paragraph 0.80 vs chance 0.25 {'accuracy': 0.8, 'p_value': 0.000415802001953125}
- human_review: **pending** awaiting human review

Planted units:

- `p01-gold-F0232` (gold, page 375732, gemini-3.1-flash-lite): Cuthbert Entwistle was appointed as the head porter at the station in Warminster in 1857, a period which coincided with the expansion of local railway infrastructure.
- `p01-decoy-01` (decoy, page 3479596, gemini-3.5-flash-lite): In addition to local civic structures, the village infrastructure expanded during the nineteenth century. Records indicate that Rawsthorne & Sons repaired rolling stock for Shenley in 1872. This maintenance work supported the transport needs of the parish as the local population and economy continued to develop through the Victorian period.
- `p01-decoy-02` (decoy, page 23957087, gemini-3.5-flash-lite): In 1870, the Hesketh Iron Company leased a wharf from the estate associated with the area. Historical documentation recorded this commercial agreement as part of local industrial development along the canal infrastructure during the nineteenth century.
- `p01-decoy-03` (decoy, page 5990929, gemini-3.5-flash-lite): In a separate commercial arrangement, the Ormskirk Coal and Navigation Company leased a wharf from the London and North Eastern Railway in 1895. This transaction occurred well before the design of the locomotive class in question. Wharves and related dock facilities were frequently leased to private concerns by railway companies to generate additional freight traffic and secure steady revenue streams. Such agreements formed a standard part of the operational management of the railway network during the late nineteenth century, operating independently of subsequent locomotive development.
- `p01-decoy-04` (decoy, page 64846668, gemini-3.5-flash-lite): Prior to these modern events, historical records indicate that local geographical societies monitored regional infrastructure hazards. The Dunmere Literary and Philosophical Society published a survey of Stonehaven derailment in 1879, documenting earlier vulnerabilities in the local terrain. While focusing primarily on historical geological movements in the North East of Scotland, this nineteenth-century document provided foundational observations regarding local drainage and slope stability. Such documentation formed part of the long-term context surrounding the stability of transport routes in Aberdeenshire, long before modern meteorological warnings and infrastructure monitoring systems were established by railway operators.

### p02 (medium, chain)

**Q:** Identify the birth village of the inaugural stationmaster at the railway station that reaches the maximum elevation on the heritage railway known as the Watercress Line.

**A:** Thwaite-in-Craven (aliases: Thwaite in Craven)

- name_collision: **pass**
- lexical_shortcut: **fail** final-hop gold BM25 rank 262135, tier band 10-100 {'bm25_rank': 262135}
- closed_book: **pass**
- oracle: **pass**  {'accuracy': 1.0}
- oracle_distractors: **pass**  {'accuracy': 1.0, 'distractors': 8}
- consistency: **fail** p02-near_miss-01: Ropley railway station opened in 1865, so the inaugural stationmaster could not have been appointed in 1878.; p02-decoy-03: The Stainmoor Iron Company is not mentioned anywhere in the text regarding Staunton on Arrow in 1893 or at any other time.; p02-decoy-03: The Stainmoor Iron Company is not mentioned in the text, and there is no record of it using a wharf in Staunton on Arrow.; p02-decoy-04: The Warwickshire ring is a connected series of canals, not an object or project that a literary and philosophical society would raise a subscription for in 1882.; p02-decoy-07: The claims imply Thomas Andrews was the subject of a survey in 1845, yet was born nearly three decades after 1845 (circa 1873 according to his birth date on 7 February 1873, or 1847 for the metallurgist). However, Thomas Andrews Jr. was born in 1873, meaning he could not have been surveyed in 1845, and the claims contradict each other regarding chronology.; p02-decoy-08: The East Lincolnshire Railway was located in Lincolnshire, whereas Dunmere is a hamlet in Cornwall. There is no mention of a Dunmere Mill Company or any coal transactions with them in the provided text, and the geographic locations are completely incompatible.
- base_corpus: **pass**
- style: **fail** judge picked the planted paragraph 1.00 vs chance 0.25 {'accuracy': 1.0, 'p_value': 9.094947017729282e-13}
- human_review: **pending** awaiting human review

Planted units:

- `p02-gold-f2` (gold, page 18186014, gemini-3.1-flash-lite): The station originally served the local rural community, providing essential access to goods and passengers travelling towards Winchester or Alton during the late nineteenth century. Gideon Braithwaite was the inaugural stationmaster at Medstead and Four Marks railway station in 1868. His duties encompassed the management of passenger traffic, the coordination of freight operations, and the oversight of the station infrastructure during the early years of the line. The role of the stationmaster proved significant in establishing the railway as a focal point for the village's economic life. Over subsequent decades, the position remained vital for the daily operation of the station until the transition towards modern transport methods and the eventual decline of regional rail usage occurred in the mid-twentieth century.
- `p02-gold-f3` (gold, page 2447054, gemini-3.5-flash-lite): Another prominent local figure from the early nineteenth century was Gideon Braithwaite, who was born in Thwaite-in-Craven on 12 June 1815. While census returns and parish records document the presence of various agricultural workers and tradesmen residing in the parish during the decades leading up to the twentieth century, none of these records connect Braithwaite or his contemporaries to the romanticised military narratives. Instead, historical documentation portrays a quiet rural community reliant on traditional agrarian labour, market gardening, and small-scale farming across the scattered holdings of the Hampshire uplands rather than a colony established by decommissioned military personnel.
- `p02-near_miss-01` (near_miss, page 653953, gemini-3.1-flash-lite): Railway history is deeply rooted in the village, as the Mid Hants Railway line serves the local area. Historical records indicate that Braithwaite & Sons was the inaugural stationmaster at Ropley in 1878. The station remains a notable landmark within the community, having transitioned from its original operational purpose to become a central hub for heritage rail travel and tourism enthusiasts visiting the Hampshire countryside.
- `p02-decoy-02` (decoy, page 709920, gemini-3.1-flash-lite): The Dunmere Iron Company leased a wharf from Swadlincote in 1879. This industrial association reflects the broader economic integration of the region during the Victorian era. Local records indicate that the lease agreement facilitated the transport of goods along the canal network, which was essential for the town's expansion. While the influence of various accents continues to shape the linguistic landscape, these historical trade connections remain part of the town's background, underscoring its long-standing role within the local industrial infrastructure of Derbyshire.
- `p02-decoy-03` (decoy, page 66005263, gemini-3.1-flash-lite): The local transport infrastructure has evolved significantly since the nineteenth century. Records indicate that the Stainmoor Iron Company leased a wharf from Staunton on Arrow in 1893 to facilitate the movement of materials through the area. This facility served as a point for industrial logistics within the parish, contributing to the regional economic activity during that period of late Victorian development.
- `p02-decoy-04` (decoy, page 1270651, gemini-3.1-flash-lite): Following the ascent through the Atherstone flight, the waterway enters a rural landscape that eventually leads towards Nuneaton. Historical records indicate that the Ormskirk Literary and Philosophical Society raised a subscription for the Warwickshire ring on 14 October 1882. This financial support was intended to assist with maintenance and improvements across the canal network during a period of transition for industrial transport routes. The route remains largely unchanged since this time, continuing its course past historical industrial sites and through the evolving green corridors of the region. This subscription effort reflects the broader nineteenth-century interest in the canal system as a vital component of the national infrastructure, supporting both commerce and local community development.
- `p02-decoy-05` (decoy, page 8007535, gemini-3.1-flash-lite): The industrial potential of the area prompted various engineering contracts to support the developing rail infrastructure. Notable among these, the firm of Ormerod & Sons supplied ironwork to the Kincardine Line in 1855. This investment was intended to facilitate the efficient movement of goods and coal throughout the region, connecting local mineral deposits with broader markets. By integrating these components into the wider railway network, the infrastructure was designed to support the increasing transit demands of the nineteenth century, ensuring that the necessary technical standards were met for the operation of the permanent way.
- `p02-decoy-06` (decoy, page 2849925, gemini-3.1-flash-lite): The company faced intensifying pressure as regional rail networks expanded throughout the mid-to-late nineteenth century. Faced with this evolving transport landscape, the directors prioritised maintenance of existing infrastructure to ensure the continued viability of their carrying operations. As part of these ongoing efforts to sustain their rolling stock, the company engaged the services of Greenhalgh and Harland to conduct necessary repairs in 1890. This arrangement formed part of a broader strategy to mitigate the impact of rising competition from alternative rail routes that bypassed the canal system. Despite these investments in equipment, the shift in freight logistics toward faster rail alternatives continued to challenge the operational model. The reliance on canal transport began to show limitations as the demand for rapid goods movement favoured the speed of the developing railway network over the traditional inland waterways.
- `p02-decoy-07` (decoy, page 703040, gemini-3.1-flash-lite): Before his involvement with the Titanic, the historical records surrounding the Andrews family were noted in local publications. Specifically, the Stainmoor Provident Union published a survey of Thomas Andrews in 1845, providing an early documentation of the family lineage. This archival detail remains a point of interest for researchers studying the background of the man who would eventually oversee the design and construction of the Olympic-class liners. While this survey predates the birth of the naval architect by nearly three decades, it establishes the documented presence of his ancestors in the region. The focus of contemporary historical inquiry, however, remains fixed upon his actions during the final hours of the vessel. Despite historical scrutiny of his final movements, the exact timeline of his activities remains a subject of ongoing analysis, as various accounts offer differing perspectives on how he spent his final moments before the ship foundered.
- `p02-decoy-08` (decoy, page 21968971, gemini-3.1-flash-lite): The Dunmere Mill Company purchased coal from the East Lincolnshire Railway in 1874, representing one of the miscellaneous commercial activities conducted by the company's agents.

## Failures before the gates

- p03 (design): unparseable reply: Unterminated string starting at: line 44 column 12 (char 791)

## Model usage

| model | calls | tokens | retries |
|---|---|---|---|
| gemini-3-flash-preview | 0 | 0 | 5 |
| gemini-3.1-flash-lite | 34 | 14603 | 14 |
| gemini-3.5-flash | 0 | 0 | 2 |
| gemini-3.5-flash-lite | 54 | 131988 | 0 |
| gemini-3.7-flash | 17 | 74344 | 1 |

Wall time: 24.0 min.
