create schema if not exists raw;
create schema if not exists prep;
create schema if not exists model;

create table if not exists model.d_release(
  release_id bigint primary key,
  title      text,
  artist     text,
  year       int,
  label      text,
  cohort     text
);
