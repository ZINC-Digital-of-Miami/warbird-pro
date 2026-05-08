-- Restore MES runtime cron schedules for Edge Function pull chain.
-- Keeps MES chart data fresh in mes_1m/mes_15m and mes_1h/mes_4h/mes_1d.

create extension if not exists pg_cron;

-- Remove stale copies first, then recreate canonical schedules.
do $$
declare
  v_job_id bigint;
begin
  for v_job_id in
    select jobid
    from cron.job
    where jobname in ('warbird_mes_1m_pull', 'warbird_mes_hourly_pull')
  loop
    perform cron.unschedule(v_job_id);
  end loop;
exception
  when undefined_table then null;
end $$;

-- MES 1m pull every minute, Sunday-Friday.
select cron.schedule(
  'warbird_mes_1m_pull',
  '* * * * 0-5',
  $$select public.run_mes_1m_pull();$$
)
where not exists (
  select 1
  from cron.job
  where jobname = 'warbird_mes_1m_pull'
);

-- MES hourly pull at :05, Sunday-Friday.
select cron.schedule(
  'warbird_mes_hourly_pull',
  '5 * * * 0-5',
  $$select public.run_mes_hourly_pull();$$
)
where not exists (
  select 1
  from cron.job
  where jobname = 'warbird_mes_hourly_pull'
);
