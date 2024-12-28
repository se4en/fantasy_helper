alter table coeffs add column result_1 double precision;
alter table coeffs add column result_x double precision;
alter table coeffs add column result_2 double precision;

alter table coeffs add column both_score_yes double precision;
alter table coeffs add column both_score_no double precision;

alter table coeffs add column total_over_0_5 double precision;
alter table coeffs add column total_under_0_5 double precision;
alter table coeffs add column total_over_1 double precision;
alter table coeffs add column total_under_1 double precision;
alter table coeffs add column total_over_1_5 double precision;
alter table coeffs add column total_under_1_5 double precision;
alter table coeffs add column total_over_2 double precision;
alter table coeffs add column total_under_2 double precision;
alter table coeffs add column total_over_2_5 double precision;
alter table coeffs add column total_under_2_5 double precision;
alter table coeffs add column total_over_3 double precision;
alter table coeffs add column total_under_3 double precision;
alter table coeffs add column total_over_3_5 double precision;
alter table coeffs add column total_under_3_5 double precision;
alter table coeffs add column total_over_4 double precision;
alter table coeffs add column total_under_4 double precision;
alter table coeffs add column total_over_4_5 double precision;
alter table coeffs add column total_under_4_5 double precision;

alter table coeffs add column handicap_1_minus_2_5 double precision;
alter table coeffs add column handicap_1_minus_2 double precision;
alter table coeffs add column handicap_1_minus_1_5 double precision;
alter table coeffs add column handicap_1_minus_1 double precision;
alter table coeffs add column handicap_1_0 double precision;
alter table coeffs add column handicap_1_plus_1 double precision;
alter table coeffs add column handicap_1_plus_1_5 double precision;
alter table coeffs add column handicap_1_plus_2 double precision;
alter table coeffs add column handicap_1_plus_2_5 double precision;

alter table coeffs add column handicap_2_minus_2_5 double precision;
alter table coeffs add column handicap_2_minus_2 double precision;
alter table coeffs add column handicap_2_minus_1_5 double precision;
alter table coeffs add column handicap_2_minus_1 double precision;
alter table coeffs add column handicap_2_0 double precision;
alter table coeffs add column handicap_2_plus_1 double precision;
alter table coeffs add column handicap_2_plus_1_5 double precision;
alter table coeffs add column handicap_2_plus_2 double precision;
alter table coeffs add column handicap_2_plus_2_5 double precision;

alter table coeffs add column total_1_over_0_5 double precision;
alter table coeffs add column total_1_over_1 double precision;
-- alter table coeffs add column total_1_over_1_5 double precision;
alter table coeffs add column total_1_over_2 double precision;
alter table coeffs add column total_1_over_2_5 double precision;
-- alter table coeffs add column total_1_under_0_5 double precision;
alter table coeffs add column total_1_under_1 double precision;
alter table coeffs add column total_1_under_1_5 double precision;
alter table coeffs add column total_1_under_2 double precision;
alter table coeffs add column total_1_under_2_5 double precision;

alter table coeffs add column total_2_over_0_5 double precision;
alter table coeffs add column total_2_over_1 double precision;
-- alter table coeffs add column total_2_over_1_5 double precision;
alter table coeffs add column total_2_over_2 double precision;
alter table coeffs add column total_2_over_2_5 double precision;
-- alter table coeffs add column total_2_under_0_5 double precision;
alter table coeffs add column total_2_under_1 double precision;
alter table coeffs add column total_2_under_1_5 double precision;
alter table coeffs add column total_2_under_2 double precision;
alter table coeffs add column total_2_under_2_5 double precision;

alter table players add column yellow_cards integer;
alter table players add column red_cards integer;
