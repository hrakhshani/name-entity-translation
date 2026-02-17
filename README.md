# Name Entity Translation

![Dashboard](data/dashboard.png)

A benchmarking pipeline for evaluating Named Entity Recognition (NER) models on travel and hospitality domain text. The project compares multiple NER approaches on their ability to extract location-related entities such as hotel names, addresses, street names, landmarks, and cities.

## Entity Schema

| Label | Description |
|-------|-------------|
| `HOTEL_NAME` | Hotel or accommodation name |
| `HOTEL_BRAND` | Hotel brand/chain name |
| `ADDRESS` | Street address |
| `STREET_NAME` | Street or road name |
| `LANDMARK` | Landmark, square, or point of interest |
| `CITY` | City name |

## Models Compared

- **GLiNER** (`fastino/gliner2-large-v1`) — Zero-shot NER using the GLiNER2 architecture with custom entity labels
- **spaCy** (`en_core_web_trf`) — Transformer-based spaCy pipeline with entity label mapping to the target schema
- **RoBERTa-NER** (`51la5/roberta-large-NER`) — Token classification pipeline with label mapping (optional)

## Test Cases

The evaluation covers robustness across several dimensions:

- **Label confusion** — Disambiguating entities with overlapping names (e.g., "Rembrandtplein" vs "Rembrandtplein Hotel")
- **Rephrasing sensitivity** — Consistency when the same entities appear in paraphrased sentences
- **Placement sensitivity** — Stability when entity positions shift within a sentence
- **Variable entity length** — Handling entities ranging from very short to very long spans
- **Case sensitivity** — Performance on lowercased input vs. standard casing
- **Spelling errors** — Robustness to misspelled entity names and surrounding text

## Project Structure

```
pipeline.ipynb          # Main evaluation notebook
data/use_cases.json     # Test case definitions
output/output.json      # Evaluation results (JSONL)
vis/
  dashboard.html        # Interactive results dashboard
  updated_dashboard.py  # Script to refresh dashboard with new data
```

## Usage

1. Open `pipeline.ipynb` and run all cells. Models are loaded one at a time to manage memory.
2. Results are exported as JSONL to `output/output.json`.
3. Refresh the dashboard:
   ```bash
   python vis/updated_dashboard.py
   ```
4. Open `vis/dashboard.html` in a browser to explore per-phrase, per-test-case, and per-algorithm metrics.

## Metrics

Each prediction is evaluated with precision, recall, and F1 at the phrase level, aggregated up to test-case and algorithm levels. Latency per prediction is also recorded.

## License

Apache 2.0
