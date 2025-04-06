
# 🧬PubMed Pharmaceutical/Biotech Papers Finder

This Python script searches PubMed for biomedical research articles based on a user-defined query, and filters for those with at least one author affiliated with a pharmaceutical or biotech company. It outputs the results to a CSV file or the console.



## Features

- Searches PubMed using Entrez API
- Identifies pharma/biotech affiliations from author information
- Extracts corresponding author email if available
- Outputs results to CSV or terminal
- Optional debug mode for verbose logging









##  Requirements

- Python 3.7+
- Biopython
- Requests

  Install the dependencies using pip:






```bash
  pip install biopython requests

```
    
## Usage

```javascript
  python pharma_papers.py "your pubmed query here"

```


## Optional Arguments

- -f, --file <filename>: Save results to a CSV file.

- -d, --debug: Enable debug mode to print internal steps.

- -m, --max <number>: Maximum number of papers to retrieve (default: 100).






## Example

```javascript
  python pharma_papers.py "diabetes treatment" -f diabetes_papers.csv -m 200 -d


```


## How It Works

- Search: Uses Entrez to search PubMed with your query.

- Fetch: Retrieves metadata for the top N results.

- Parse: Extracts author affiliations and checks for company involvement using:
     - Known pharma/biotech company names

   - Keywords (e.g., "therapeutics", "biologics", etc.)

   - Filters out academic institutions

- Output: Presents results with:

   - PubMed ID

   - Title

  - Date

  - Author names

  - Company affiliations

   - Corresponding email (if available)


## Output Example

```javascript
  PubmedID,Title,Publication Date,Non-academic Author(s),Company Affiliation(s),Corresponding Author Email
35270448,Metabolic Treatment of Wolfram Syndrome,Unknown,"Iafusco, Fernanda",CEINGE Advanced Biotech,

```

## Customization

To improve results:

- Add to KNOWN_COMPANIES set for more accurate company detection.

- Expand PHARMA_BIOTECH_KEYWORDS and ACADEMIC_KEYWORDS.


## License

MIT License. Feel free to use, modify, and distribute.





## Contact

Maintained by:  Komal Gangwar

Email: komalgangwar2004@gmail.com

