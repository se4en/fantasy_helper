alter table coeffs drop column if exists tour;
alter table coeffs add column tour_number integer DEFAULT NULL;

alter table fs_coeffs drop column if exists tour;
alter table fs_coeffs add column tour_number integer;
