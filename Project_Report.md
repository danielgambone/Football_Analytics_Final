# Landing page: 
## Overview: 
I used the 2024 NFL regular season league standings statistics and the 2024 NFL team scoring statistics from the NFL website to create a web application that educates the user about a given team's success during the year with statistical proof. I hoped to show the correlation between team standings and scoring.

Git Hub Repository:
https://github.com/danielgambone/Football_Analytics_Final

## Web scraping:
I scraped data from NFL.com because it is a trustworthy source and provided the correct dabular format of the data. The table was organized in the format I wanted. I used the following two websites: 
https://www.nfl.com/stats/team-stats/offense/scoring/2024/reg/all
https://www.nfl.com/standings/league/2024/REG

I used the two following AI prompts to create the web scrape code:
"Write a Python function that uses requests and BeautifulSoup to scrape the 'Team Scoring 2024' table from this NFL page: https://www.nfl.com/stats/team-stats/offense/scoring/2024/reg/all. Create a SQLite database named NFL Stats and use the following fields to create the new table: 'Rsh_TD', 'Rec_TD', 'Tot_TD', '2-PT'. Handle missing values and strip whitespace."

"Write another Python function that uses requests and Beautiful Soup to scrape the 2024 Division standings table from this NFL page: https://www.nfl.com/standings/league/2024/REG. Use the existing NFL_Stats database. When creating the new team id in this table use the team id found in the original 'Team Scoring 2024' table. This id should represent the team. Also pull in the following fields: 'NFL_Team', 'W', 'L', 'T'."

### Example HTTP request and parse step:
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

## Database:
I used the following tables and columns:
 - league_standings_2024 - Team standings for the 2024 NFL season (Team Name, Wins, Losses, Ties)
    id, -- auto generated primary key. Not needed in output.
    team_id, -- Team Id used to uniquely identify each team 
    NFL_Team,-- Team name
    W, -- Wins
    L, -- Losses
    T  -- Ties
 - team_scoring_2024 - Team scoring statistics for the 2024 NFL season (includes Rushing TDs, Receiving TDs, Total TDs, 2 Points Conversions)
    id AS team_id, -- Team Id used to uniquely identify each team and to match with the standings table team id's 
    Team, -- Team name
    Rsh_TD, -- Rushing Touchdowns
    Rec_TD, -- Receiving Touchdowns
    Tot_TD, -- Total Touchdowns
    '2-PT'  -- Successful 2-Point conversions

### Example data from csv file for the web app:
Team,Rushing_Touchdowns,Receiving_Touchdowns,Total_Touchdowns,Two_Point_Conversions,Wins,Losses,Ties
49ers,17,23,42,0,6,11,0

### Query used to generate csv:
select NFL_Team as "Team", W as "Wins", L as "Losses", T as "Ties", Rsh_TD as "Rushing Touchdowns", Rec_TD as "Receiving Touchdowns", Tot_TD as "Total Touchdowns", "2-PT" as "Two Point Conversions"
from league_standings_2024
inner join team_scoring_2024
on league_standings_2024.team_id = team_scoring_2024.id

## Web Application:
 
My application includes the following 6 visualizations to look at team scoring and record.
The user selects an NFL team to see the related data on the first three graphs below.
Graph 4 requires the user to select two teams for comparison. Graph 5 gives the user the option to highlight a selected team to use as a visual help. Graph 6 requires no user input.
1. Individual Team Scoring Statistics (bar chart)
 - Shows the selected team's scoring statistics and record in a bar chart
2. Offensive Balance (pie chart)
 - Shows the proportion of Rushing TDs vs Receiving TDs
 - Includes percentages and raw numbers
 - Shows if a team is more run biased or throw biased
3. Team Profile (radar chart)
 - Shows 5 dimensions on a pentagon:
    - Wins
    - Total TDs
    - Rushing TDs
    - Receiving TDs
    - 2-Point Conversions
 - Normalized to show relative performance
 - Raw values displayed with labels
4. Team Comparison (side-by-side bars)
 - Two dropdowns to select any two teams
 - Side-by-side bar charts comparing:
    - Wins
    - Rushing TDs
    - Receiving TDs
    - Total TDs
    - 2-Point Conversions
5. Scatter Plot (Wins vs Total TDs with highlighting)
 - Shows all 32 teams plotted with Wins (x-axis) vs Total Touchdowns (y-axis)
 - Visually demonstrates the correlation between scoring and winning
6. Top 10 Teams (ranked visualization)
 - Gives the top 10 teams based off of record through a ranking system and compares it to the total touchdowns rank 



 



