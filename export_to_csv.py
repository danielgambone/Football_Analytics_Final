import sqlite3
import csv

# Connect to database
conn = sqlite3.connect('NFL_Stats.db')
cursor = conn.cursor()

# Join the two tables to get scoring and standings data
cursor.execute('''
    SELECT 
        ts.Team,
        ts.Rsh_TD,
        ts.Rec_TD,
        ts.Tot_TD,
        ts."2-PT",
        ls.W,
        ls.L,
        ls.T
    FROM team_scoring_2024 ts
    LEFT JOIN league_standings_2024 ls ON ts.id = ls.team_id
    ORDER BY ts.Team
''')

# Fetch all data
data = cursor.fetchall()

# Write to CSV
with open('2024_Team_Scoring_Standings.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write header
    writer.writerow(['Team', 'Rushing_Touchdowns', 'Receiving_Touchdowns', 'Total_Touchdowns', 'Two_Point_Conversions', 'Wins', 'Losses', 'Ties'])
    # Write data
    writer.writerows(data)

conn.close()

print(f"Successfully created 2024_Team_Scoring_Standings.csv with {len(data)} teams")
