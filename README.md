# Football_Analytics_Final
Prompts:
"Write a Python function that uses requests and BeautifulSoup to scrape the 'Team Scoring 2024' table from this NFL page: https://www.nfl.com/stats/team-stats/offense/scoring/2024/reg/all. Create a SQLite database named NFL Stats and use the following fields to create the new table: 'Rsh_TD', 'Rec_TD', 'Tot_TD', '2-PT'. Handle missing values and strip whitespace."

The team column value in the database is not correct. The expected value is duplicated. Can you fix this?

Write another Python function that uses requests and Beautiful Soup to scrape the 2024 Division standings table from this NFL page: https://www.nfl.com/standings/league/2024/REG. Use the existing NFL_Stats database. When creating the new team id in this table use the team id found in the original 'Team Scoring 2024' table. This id should represent the team. Also pull in the following fields: 'NFL_Team', 'W', 'L', 'T'.


