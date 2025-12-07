import requests
from bs4 import BeautifulSoup
import sqlite3
import re


def scrape_nfl_team_scoring():
    """
    Scrapes the Team Scoring 2024 table from NFL.com and stores it in a SQLite database.
    
    Returns:
        str: Success message or error message
    """
    # URL to scrape
    url = "https://www.nfl.com/stats/team-stats/offense/scoring/2024/reg/all"
    
    try:
        # Send HTTP request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table - NFL.com uses specific table structure
        # The table data is typically in a div with specific classes
        table = soup.find('table')
        
        if not table:
            return "Error: Could not find the table on the page"
        
        # Extract headers to find the column indices
        headers_row = table.find('thead')
        if headers_row:
            header_cells = headers_row.find_all('th')
            header_names = [cell.get_text(strip=True) for cell in header_cells]
        else:
            return "Error: Could not find table headers"
        
        # Find indices for required columns
        column_indices = {}
        for idx, header in enumerate(header_names):
            if 'Rsh TD' in header or 'Rush TD' in header:
                column_indices['Rsh_TD'] = idx
            elif 'Rec TD' in header or 'Receiving TD' in header:
                column_indices['Rec_TD'] = idx
            elif 'Tot TD' in header or 'Total TD' in header:
                column_indices['Tot_TD'] = idx
            elif '2-PT' in header or '2PT' in header:
                column_indices['2-PT'] = idx
        
        # Extract table data
        rows = table.find('tbody').find_all('tr')
        team_data = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 0:
                continue
            
            # Extract team name (usually in first column)
            # NFL.com often has nested elements, get only direct text or first occurrence
            if cells:
                team_cell = cells[0]
                # Try to find a link or span with team name first
                team_link = team_cell.find('a')
                if team_link:
                    team_name = team_link.get_text(strip=True)
                else:
                    # Get text and remove duplicates if they exist
                    team_text = team_cell.get_text(strip=True)
                    # Check if team name is duplicated (e.g., "BillsBills")
                    if len(team_text) > 0 and len(team_text) % 2 == 0:
                        half_len = len(team_text) // 2
                        if team_text[:half_len] == team_text[half_len:]:
                            team_name = team_text[:half_len]
                        else:
                            team_name = team_text
                    else:
                        team_name = team_text
            else:
                team_name = None
            
            # Extract the required statistics
            row_data = {'Team': team_name}
            
            for col_name, idx in column_indices.items():
                if idx < len(cells):
                    value = cells[idx].get_text(strip=True)
                    # Handle missing values - convert to None or 0
                    if value in ['', '-', 'N/A', '--']:
                        row_data[col_name] = 0
                    else:
                        # Remove any non-numeric characters except digits and decimal point
                        cleaned_value = re.sub(r'[^\d.]', '', value)
                        try:
                            row_data[col_name] = int(cleaned_value) if cleaned_value else 0
                        except ValueError:
                            row_data[col_name] = 0
                else:
                    row_data[col_name] = 0
            
            team_data.append(row_data)
        
        # Create SQLite database and table
        conn = sqlite3.connect('NFL_Stats.db')
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_scoring_2024 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Team TEXT NOT NULL,
                Rsh_TD INTEGER,
                Rec_TD INTEGER,
                Tot_TD INTEGER,
                "2-PT" INTEGER
            )
        ''')
        
        # Clear existing data
        cursor.execute('DELETE FROM team_scoring_2024')
        
        # Insert data
        for data in team_data:
            cursor.execute('''
                INSERT INTO team_scoring_2024 (Team, Rsh_TD, Rec_TD, Tot_TD, "2-PT")
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data.get('Team', ''),
                data.get('Rsh_TD', 0),
                data.get('Rec_TD', 0),
                data.get('Tot_TD', 0),
                data.get('2-PT', 0)
            ))
        
        # Commit and close
        conn.commit()
        conn.close()
        
        return f"Successfully scraped and stored {len(team_data)} team records in NFL_Stats.db"
    
    except requests.RequestException as e:
        return f"Error fetching data from URL: {str(e)}"
    except sqlite3.Error as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


if __name__ == "__main__":
    result = scrape_nfl_team_scoring()
    print(result)
