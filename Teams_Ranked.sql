-- Rank teams by wins using window function, and ranked tot_td order by wins desc, show top 10
select
    ls.team_id,
    ls.NFL_Team AS "Team",
    ls.W AS "Wins",
    RANK() OVER (ORDER BY ls.W DESC) AS "Wins Rank",
    s.Tot_TD AS "Total Touchdowns",
    RANK() OVER (ORDER BY s.Tot_TD DESC) AS "Total TD Rank"
from league_standings_2024 ls
inner join team_scoring_2024 s
on ls.team_id = s.id
order by "Wins Rank"
LIMIT 10
;
