# Prompts:
"Write a Python function that uses requests and BeautifulSoup to scrape the 'Team Scoring 2024' table from this NFL page: https://www.nfl.com/stats/team-stats/offense/scoring/2024/reg/all. Create a SQLite database named NFL Stats and use the following fields to create the new table: 'Rsh_TD', 'Rec_TD', 'Tot_TD', '2-PT'. Handle missing values and strip whitespace."

The team column value in the database is not correct. The expected value is duplicated. Can you fix this?

Write another Python function that uses requests and Beautiful Soup to scrape the 2024 Division standings table from this NFL page: https://www.nfl.com/standings/league/2024/REG. Use the existing NFL_Stats database. When creating the new team id in this table use the team id found in the original 'Team Scoring 2024' table. This id should represent the team. Also pull in the following fields: 'NFL_Team', 'W', 'L', 'T'.

There are only 18 rows or 'teams' in the league_standings_2024 table when there should be 32 from the website. Can you make sure all teams are added to the table (32 rows)?

I would like to create a no frameworks, front end, vanilla javascript, index in the root directory, web application that uses the 2024_Team_Scoring_Standings.csv file as the data. I want the web app to graph the scoring data. Make the team selectable from a user dropdown. For example scoring data: Rushing Touchdowns,Receiving Touchdowns,Total Touchdowns,Two Point Conversions

Update my index.html file to have the Project_Report.md included at the bottom of the landing page as a project description. Convert the markdown file into html.

 Update the index.html file to include another graphic using the data from Top10Teams.csv. Show the in a single visual along with Win Rank, Wins, Total TDs and Total TD Rank.