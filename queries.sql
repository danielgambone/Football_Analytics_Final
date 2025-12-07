select 
    --ls.id, -- auto generated primary key. Not needed in output.
    ls.team_id, 
    ls.NFL_Team, 
    ls.W, 
    ls.L, 
    ls.T
from league_standings_2024 AS ls
order by ls.W DESC
;

select
    s.id AS team_id, 
    s.Team, 
    s.Rsh_TD, 
    s.Rec_TD, 
    s.Tot_TD, 
    s.'2-PT'
from team_scoring_2024 s
;

select NFL_Team, W, L, T, Rsh_TD, Rec_TD, Tot_TD, "2-PT"
from league_standings_2024
inner join team_scoring_2024
on league_standings_2024.team_id = team_scoring_2024.id
