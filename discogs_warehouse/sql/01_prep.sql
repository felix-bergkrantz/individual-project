-- flatten release-level snapshot
create or replace table prep.lowest as
select
  cast(json_extract(raw.raw_release_snapshots.json, '$.release_id')     as bigint) as release_id,
  cast(json_extract(raw.raw_release_snapshots.json, '$.lowest_price')   as double) as lowest_price,
  cast(json_extract(raw.raw_release_snapshots.json, '$.num_for_sale')   as int)    as num_for_sale,
  to_timestamp(
      cast(json_extract(raw.raw_release_snapshots.json, '$._ingested_at') as double)
  ) as ingested_at
from raw.raw_release_snapshots;
