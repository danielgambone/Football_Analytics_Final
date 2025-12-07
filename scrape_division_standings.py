import requests
from bs4 import BeautifulSoup
import sqlite3
import re


def scrape_league_standings():
    """
    Scrapes the 2024 League standings table from NFL.com and stores it in the existing NFL_Stats database.
    Links team data using the team id from the team_scoring_2024 table.
    
    Returns:
        str: Success message or error message
    """
    # URL to scrape
    url = "https://www.nfl.com/standings/league/2024/REG"
    
    try:
        # Send HTTP request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the standings table
        table = soup.find('table')
        
        if not table:
            return "Error: Could not find the standings table on the page"
        
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
            header_lower = header.lower()
            if 'team' in header_lower:
                column_indices['NFL_Team'] = idx
            elif header_lower == 'w':
                column_indices['W'] = idx
            elif header_lower == 'l':
                column_indices['L'] = idx
            elif header_lower == 't':
                column_indices['T'] = idx
        
        # Extract table data
        rows = table.find('tbody').find_all('tr')
        standings_data = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 0:
                continue
            
            # Extract team name
            if cells:
                team_cell = cells[0]
                # Get text and clean it
                team_text = team_cell.get_text(strip=True)
                
                # Extract team name from the last word, handling corrupted suffixes
                words = team_text.split()
                last_word = words[-1] if words else ""
                
                if last_word:
                    # Find the team name: start from first uppercase, continue collecting letters
                    # Stop when we encounter a sequence that looks like corruption (lowercase after the team name)
                    team_name = ""
                    for j, char in enumerate(last_word):
                        if char.isupper():
                            if not team_name:
                                # Starting the team name
                                team_name = char
                            else:
                                # Add uppercase letters
                                team_name += char
                        elif char.isalpha() and team_name:
                            # Add lowercase only if it's right after uppercase (like "McD" in McDonald)
                            # or if we've been building the name
                            if len(team_name) > 0:
                                team_name += char
                        elif not char.isalpha() and team_name:
                            # Hit non-letter, stop building
                            break
                    
                    # Handle duplicated names like "BrownsBrowns" where the entire name appears twice
                    if team_name and len(team_name) > 2:
                        # Check if it's a duplication (even length and first half = second half)
                        if len(team_name) % 2 == 0:
                            half_len = len(team_name) // 2
                            if team_name[:half_len].lower() == team_name[half_len:].lower():
                                team_name = team_name[:half_len]
                else:
                    team_name = None
            else:
                team_name = None
            
            # Extract the required statistics
            row_data = {'NFL_Team': team_name}
            
            for col_name, idx in column_indices.items():
                if col_name != 'NFL_Team' and idx < len(cells):
                    value = cells[idx].get_text(strip=True)
                    # Handle missing values
                    if value in ['', '-', 'N/A', '--']:
                        row_data[col_name] = 0
                    else:
                        # Remove any non-numeric characters
                        cleaned_value = re.sub(r'[^\d]', '', value)
                        try:
                            row_data[col_name] = int(cleaned_value) if cleaned_value else 0
                        except ValueError:
                            row_data[col_name] = 0
                elif col_name != 'NFL_Team':
                    row_data[col_name] = 0
            
            standings_data.append(row_data)
        
        # Connect to the existing database
        conn = sqlite3.connect('NFL_Stats.db')
        cursor = conn.cursor()
        
        # Get list of teams from the scoring table for matching
        cursor.execute('SELECT id, Team FROM team_scoring_2024 ORDER BY Team')
        db_teams = {row[1].lower(): row[0] for row in cursor.fetchall()}
        
        # Create standings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS league_standings_2024 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                NFL_Team TEXT NOT NULL,
                W INTEGER,
                L INTEGER,
                T INTEGER,
                FOREIGN KEY (team_id) REFERENCES team_scoring_2024(id)
            )
        ''')
        
        # Clear existing data
        cursor.execute('DELETE FROM league_standings_2024')
        
        # Insert data with team_id lookup
        inserted_count = 0
        for data in standings_data:
            # Look up team_id from team_scoring_2024 table using fuzzy matching
            team_name = data.get('NFL_Team', '')
            
            # Try exact match first (case-insensitive)
            team_id = db_teams.get(team_name.lower())
            
            # If no exact match, try to find it by checking if it's a substring or contains team name
            if not team_id:
                for db_team_name, tid in db_teams.items():
                    # Check if the extracted team is in the database team name or vice versa
                    if db_team_name in team_name.lower() or team_name.lower() in db_team_name:
                        team_id = tid
                        team_name = db_team_name.title()
                        break
            
            if team_id:
                cursor.execute('''
                    INSERT INTO league_standings_2024 (team_id, NFL_Team, W, L, T)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    team_id,
                    team_name,
                    data.get('W', 0),
                    data.get('L', 0),
                    data.get('T', 0)
                ))
                inserted_count += 1
        
        # Commit and close
        conn.commit()
        conn.close()
        
        return f"Successfully scraped and stored {inserted_count} team standings in NFL_Stats.db"
    
    except requests.RequestException as e:
        return f"Error fetching data from URL: {str(e)}"
    except sqlite3.Error as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


if __name__ == "__main__":
    result = scrape_league_standings()
    print(result)
