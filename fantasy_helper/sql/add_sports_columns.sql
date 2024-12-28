alter table fs_players_stats add column sports_team VARCHAR(255);
alter table fs_players_stats add column sports_name VARCHAR(255);
alter table fs_players_stats add column role VARCHAR(255);
alter table fs_players_stats add column price double precision;
alter table fs_players_stats add column percent_ownership double precision;
alter table fs_players_stats add column percent_ownership_diff double precision;

alter table fs_players_free_kicks add column sports_team VARCHAR(255);
alter table fs_players_free_kicks add column sports_name VARCHAR(255);
alter table fs_players_free_kicks add column role VARCHAR(255);
alter table fs_players_free_kicks add column price double precision;
alter table fs_players_free_kicks add column percent_ownership double precision;
alter table fs_players_free_kicks add column percent_ownership_diff double precision;