-- Enforce top-bar cross-asset pull cadence:
-- - Databento ohlcv-1h direct pull path (no rollup math)
-- - run at minute :03 every hour (Sun-Fri)
-- - applies to all 4 shards so every top-bar symbol is covered each hour

create extension if not exists pg_cron;

do $$
declare
  v_job_id bigint;
begin
  for v_job_id in
    select jobid
    from cron.job
    where jobname in (
      'warbird_cross_asset_s0',
      'warbird_cross_asset_s1',
      'warbird_cross_asset_s2',
      'warbird_cross_asset_s3'
    )
  loop
    perform cron.unschedule(v_job_id);
  end loop;
exception
  when undefined_table then null;
end $$;

select cron.schedule(
  'warbird_cross_asset_s0',
  '3 * * * 0-5',
  $$select public.run_cross_asset_pull(0);$$
)
where not exists (
  select 1
  from cron.job
  where jobname = 'warbird_cross_asset_s0'
);

select cron.schedule(
  'warbird_cross_asset_s1',
  '3 * * * 0-5',
  $$select public.run_cross_asset_pull(1);$$
)
where not exists (
  select 1
  from cron.job
  where jobname = 'warbird_cross_asset_s1'
);

select cron.schedule(
  'warbird_cross_asset_s2',
  '3 * * * 0-5',
  $$select public.run_cross_asset_pull(2);$$
)
where not exists (
  select 1
  from cron.job
  where jobname = 'warbird_cross_asset_s2'
);

select cron.schedule(
  'warbird_cross_asset_s3',
  '3 * * * 0-5',
  $$select public.run_cross_asset_pull(3);$$
)
where not exists (
  select 1
  from cron.job
  where jobname = 'warbird_cross_asset_s3'
);
