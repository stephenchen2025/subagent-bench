"""CSV export."""
import csv
import io

COLUMNS = ["id", "name", "state"]


def export_csv(store):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(COLUMNS)
    for record in store.all():
        writer.writerow([record[c] for c in COLUMNS])
    return out.getvalue()
