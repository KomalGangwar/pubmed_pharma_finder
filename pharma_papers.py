#!/usr/bin/env python3
"""
PubMed Pharmaceutical/Biotech Papers Finder

This script fetches research papers from PubMed based on a user-specified query,
identifies papers with at least one author affiliated with a pharmaceutical or biotech company,
and returns the results as a CSV file.
"""

import argparse
import csv
import re
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

import requests
from Bio import Entrez

# Set your email for Entrez
Entrez.email = "komalgangwar2004@gmail.com"  # Replace with your email

# List of common pharmaceutical and biotech company keywords
# This list can be expanded for better coverage
PHARMA_BIOTECH_KEYWORDS = {
    'pharma', 'pharmaceutical', 'therapeutics', 'biopharm', 'biotech', 
    'biologics', 'laboratories', 'medicines', 'vaccines', 'health products',
    'bioscience', 'life science', 'drug', 'biopharma', 'genomics',
    'diagnostics', 'medical technology', 'biotechnology'
}

# List of common academic institution keywords to exclude
ACADEMIC_KEYWORDS = {
    'university', 'college', 'institute', 'school of medicine', 'academy',
    'hospital', 'medical center', 'clinic', 'medical school', 'faculty',
    'department of', 'center for', 'research center', 'national institute',
    'foundation', 'laboratory of', 'health system'
}

# Known pharmaceutical/biotech companies (add more as needed)
KNOWN_COMPANIES = {
    'pfizer', 'merck', 'novartis', 'roche', 'sanofi', 'gsk', 'glaxosmithkline',
    'astrazeneca', 'johnson & johnson', 'j&j', 'janssen', 'lilly', 'eli lilly',
    'abbvie', 'bristol myers squibb', 'bms', 'gilead', 'amgen', 'biogen',
    'regeneron', 'moderna', 'vertex', 'bayer', 'boehringer ingelheim',
    'genentech', 'takeda', 'novo nordisk', 'astellas', 'daiichi sankyo',
    'celgene', 'servier', 'teva', 'otsuka', 'eisai', 'alexion', 'biomarin',
    'incyte', 'illumina', 'iqvia', 'medimmune', 'grail', '23andme', 'beam',
    'editas', 'crispr', 'intellia', 'allogene', 'sarepta', 'bluebird bio',
    'sage therapeutics', 'alnylam', 'mirati', 'seagen', 'blueprint medicines',
    'acceleron', 'exelixis', 'guardant health', 'applied therapeutics'
}

def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Fetch PubMed papers with authors affiliated with pharmaceutical/biotech companies."
    )
    parser.add_argument(
        "query", 
        type=str,
        help="PubMed search query (supports full PubMed query syntax)"
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Filename to save results (CSV format). If not provided, prints to console."
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode to print additional information during execution"
    )
    parser.add_argument(
        "-m", "--max",
        type=int,
        default=100,
        help="Maximum number of papers to retrieve (default: 100)"
    )
    return parser

def debug_print(message: str, debug_mode: bool) -> None:
    """Print debug messages if debug mode is enabled."""
    if debug_mode:
        print(f"DEBUG: {message}", file=sys.stderr)

def search_pubmed(query: str, max_results: int, debug_mode: bool) -> List[str]:
    """
    Search PubMed for papers matching the query.
    
    Args:
        query: PubMed search query
        max_results: Maximum number of results to return
        debug_mode: Whether to print debug information
        
    Returns:
        List of PubMed IDs matching the query
    """
    debug_print(f"Searching PubMed with query: {query}", debug_mode)
    
    try:
        # Search PubMed
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )
        record = Entrez.read(handle)
        handle.close()
        
        # Get the IDs of the matching papers
        id_list = record["IdList"]
        debug_print(f"Found {len(id_list)} papers matching the query", debug_mode)
        
        return id_list
    
    except Exception as e:
        print(f"Error searching PubMed: {e}", file=sys.stderr)
        return []

def fetch_paper_details(id_list: List[str], debug_mode: bool) -> List[Dict]:
    """
    Fetch details for a list of PubMed IDs.
    
    Args:
        id_list: List of PubMed IDs
        debug_mode: Whether to print debug information
        
    Returns:
        List of paper details
    """
    if not id_list:
        return []
    
    debug_print(f"Fetching details for {len(id_list)} papers", debug_mode)
    
    try:
        # Fetch paper details
        handle = Entrez.efetch(
            db="pubmed",
            id=",".join(id_list),
            rettype="xml",
            retmode="xml"
        )
        records = Entrez.read(handle)
        handle.close()
        
        return records["PubmedArticle"]
    
    except Exception as e:
        print(f"Error fetching paper details: {e}", file=sys.stderr)
        return []

def is_company_affiliation(affiliation: str) -> Tuple[bool, Optional[str]]:
    """
    Check if an affiliation string belongs to a pharmaceutical or biotech company.
    
    Args:
        affiliation: Affiliation string
        
    Returns:
        Tuple of (is_company, company_name)
    """
    # Convert to lowercase for case-insensitive matching
    affiliation_lower = affiliation.lower()
    
    # Check for known companies first
    for company in KNOWN_COMPANIES:
        if company in affiliation_lower:
            # Extract the actual company name from the affiliation
            pattern = re.compile(f"({company}[^,;.]*)", re.IGNORECASE)
            match = pattern.search(affiliation)
            if match:
                return True, match.group(1).strip()
            return True, company
    
    # Check for academic keywords (negative signal)
    for keyword in ACADEMIC_KEYWORDS:
        if keyword in affiliation_lower:
            return False, None
    
    # Check for pharma/biotech keywords
    for keyword in PHARMA_BIOTECH_KEYWORDS:
        if keyword in affiliation_lower:
            # Try to extract company name
            # Look for patterns like "XYZ Pharmaceuticals", "XYZ, Inc.", etc.
            patterns = [
                r"([A-Z][A-Za-z0-9\s]+(?:Pharma|Therapeutics|Biotech|Biologics|Laboratories|Sciences|Health|Medical|Genomics|Diagnostics))",
                r"([A-Z][A-Za-z0-9\s]+(?:Inc\.|LLC|Ltd\.?|GmbH|Corp\.?|S\.A\.|Co\.|B\.V\.))",
                r"([A-Z][A-Za-z0-9\s]+)(?:\s+Inc\.|\s+LLC|\s+Ltd\.?|\s+GmbH|\s+Corp\.?|\s+S\.A\.|\s+Co\.|\s+B\.V\.)",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, affiliation)
                if match:
                    return True, match.group(1).strip()
            
            # If no specific company name found, use a chunk of the affiliation
            return True, affiliation[:50] + "..." if len(affiliation) > 50 else affiliation
    
    return False, None

def extract_author_info(paper: Dict) -> List[Dict]:
    """
    Extract author information from a paper.
    
    Args:
        paper: PubMed paper record
        
    Returns:
        List of author information dictionaries
    """
    authors_info = []
    
    try:
        article = paper["MedlineCitation"]["Article"]
        author_list = article.get("AuthorList", [])
        
        for author in author_list:
            if not isinstance(author, dict):
                continue
                
            # Get author name
            last_name = author.get("LastName", "")
            fore_name = author.get("ForeName", "")
            initials = author.get("Initials", "")
            name = f"{last_name}, {fore_name}" if fore_name else f"{last_name}, {initials}"
            
            # Get affiliation
            affiliations = []
            
            # Handle different versions of the PubMed XML structure
            if "AffiliationInfo" in author:
                for aff_info in author["AffiliationInfo"]:
                    affiliations.append(aff_info.get("Affiliation", ""))
            elif "Affiliation" in author:
                if isinstance(author["Affiliation"], list):
                    affiliations.extend(author["Affiliation"])
                else:
                    affiliations.append(author["Affiliation"])
            
            # Check for corresponding author information
            is_corresponding = False
            email = ""
            
            for affiliation in affiliations:
                # Look for email addresses
                email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", affiliation)
                if email_match:
                    email = email_match.group(0)
                
                # Look for corresponding author indicators
                if re.search(r"correspond", affiliation, re.IGNORECASE):
                    is_corresponding = True
            
            # Add author info to the list
            authors_info.append({
                "name": name,
                "affiliations": affiliations,
                "is_corresponding": is_corresponding,
                "email": email
            })
        
    except Exception as e:
        print(f"Error extracting author information: {e}", file=sys.stderr)
    
    return authors_info

def process_papers(papers: List[Dict], debug_mode: bool) -> List[Dict]:
    """
    Process papers to identify those with pharma/biotech company affiliations.
    
    Args:
        papers: List of PubMed paper records
        debug_mode: Whether to print debug information
        
    Returns:
        List of processed papers with pharma/biotech authors
    """
    results = []
    
    for i, paper in enumerate(papers):
        debug_print(f"Processing paper {i+1}/{len(papers)}", debug_mode)
        
        try:
            # Extract basic paper information
            pubmed_id = paper["MedlineCitation"]["PMID"]
            article = paper["MedlineCitation"]["Article"]
            title = article["ArticleTitle"]
            
            # Extract publication date
            pub_date = "Unknown"
            if "PubDate" in article["Journal"]["JournalIssue"]["PubDate"]:
                date_parts = article["Journal"]["JournalIssue"]["PubDate"]
                year = date_parts.get("Year", "")
                month = date_parts.get("Month", "")
                day = date_parts.get("Day", "")
                pub_date = f"{year} {month} {day}".strip()
            
            # Extract author information
            authors_info = extract_author_info(paper)
            
            # Identify authors with company affiliations
            company_authors = []
            company_affiliations = set()
            corresponding_author_email = ""
            
            for author in authors_info:
                for affiliation in author["affiliations"]:
                    is_company, company_name = is_company_affiliation(affiliation)
                    if is_company:
                        company_authors.append(author["name"])
                        if company_name:
                            company_affiliations.add(company_name)
                        break
                
                # Collect corresponding author email
                if author["is_corresponding"] and author["email"]:
                    corresponding_author_email = author["email"]
                elif author["email"] and not corresponding_author_email:
                    # Use any email as a fallback
                    corresponding_author_email = author["email"]
            
            # Only include papers with at least one company-affiliated author
            if company_authors:
                results.append({
                    "PubmedID": pubmed_id,
                    "Title": title,
                    "Publication Date": pub_date,
                    "Non-academic Author(s)": "; ".join(company_authors),
                    "Company Affiliation(s)": "; ".join(company_affiliations),
                    "Corresponding Author Email": corresponding_author_email
                })
                
                debug_print(f"Found paper with company affiliation: {title}", debug_mode)
        
        except Exception as e:
            print(f"Error processing paper: {e}", file=sys.stderr)
    
    return results

def save_results(results: List[Dict], filename: Optional[str], debug_mode: bool) -> None:
    """
    Save results to a CSV file or print to the console.
    
    Args:
        results: List of paper results
        filename: Optional filename to save results to
        debug_mode: Whether to print debug information
    """
    if not results:
        print("No papers with pharmaceutical/biotech company affiliations found.")
        return
    
    # Define field names
    fieldnames = [
        "PubmedID", 
        "Title", 
        "Publication Date", 
        "Non-academic Author(s)", 
        "Company Affiliation(s)", 
        "Corresponding Author Email"
    ]
    
    if filename:
        # Save to file
        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in results:
                    writer.writerow(row)
            
            print(f"Results saved to {filename} ({len(results)} papers)")
        except Exception as e:
            print(f"Error saving results to file: {e}", file=sys.stderr)
    else:
        # Print to console
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
        
        print(f"\nTotal papers with pharmaceutical/biotech company affiliations: {len(results)}")

def main():
    """Main function."""
    # Parse command-line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Search PubMed
    id_list = search_pubmed(args.query, args.max, args.debug)
    
    if not id_list:
        print("No papers found matching the query.")
        return
    
    # Fetch paper details
    papers = fetch_paper_details(id_list, args.debug)
    
    if not papers:
        print("Failed to fetch paper details.")
        return
    
    # Process papers to identify those with company affiliations
    results = process_papers(papers, args.debug)
    
    # Save or print results
    save_results(results, args.file, args.debug)

if __name__ == "__main__":
    main()