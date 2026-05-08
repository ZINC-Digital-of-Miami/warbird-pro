-- Restore MES hourly pull schedule to canonical minute :05 cadence (Sun-Fri).
-- Top-bar cadence changes are handled separately in cross-asset schedules.

create extension if not exists pg_cron;

do $$
declare
  v_job_id bigint;
begin
  for v_job_id in
    select jobid
    from cron.job
    where jobname = 'warbird_mes_hourly_pull'
  loop
    perform cron.unschedule(v_job_id);
  end loop;
exception
  when undefined_table then null;
end $$;

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
