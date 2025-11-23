create or replace table model.f_release_latest as
select
    pl.release_id,
    dr.title,
    dr.artist,
    dr.year,
    dr.label,
    dr.cohort,
    pl.lowest_price,
    pl.num_for_sale,
    pl.ingested_at
from prep.lowest pl
left join model.d_release dr
    on dr.release_id = pl.release_id
qualify pl.ingested_at = (
    select max(ingested_at)
    from prep.lowest pl2    
    where pl2.release_id = pl.release_id
);

