with tbl1 as (
select
    key
    , lead(key) over(partition by game_id order by game_id, time) following_key
    , time
    , lead(time) over(partition by game_id order by game_id, time) following_time
    , game_id

from keys_pressed
where 1=1
    and correct_key = 1
    and game_id > 100
)

select 
    key || '-' || following_key as key_combination
    , avg(following_time - time) as time_diff
    , count(*) count

from tbl1
where 1=1
    and following_key is not null
group by 1
having 1=1
    and count > 20
order by time_diff asc
