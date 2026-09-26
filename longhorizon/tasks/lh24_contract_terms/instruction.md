# Vendor contract register

Procurement is building a register of our vendor agreements. For every vendor
under `/workspace/contracts/`, extract the fields defined in `docs/FIELDS.md`
from its agreement and any amendments.

Write `/workspace/answer/contracts.json`, keyed by the vendor's directory name:

```json
{"<vendor-dir>": {"start_date": "YYYY-MM-DD", "term_months": 24, "auto_renew": true, "notice_days": 90,
                  "next_renewal": "YYYY-MM-DD", "liability_cap_eur": 250000, "governing_law": "..."}}
```
