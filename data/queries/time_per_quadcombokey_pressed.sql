with tbl1 as (
select
    key
    , lead(key) over(partition by game_id order by game_id, time) following_key
    , lead(key, 2) over(partition by game_id order by game_id, time) following2_key
    , lead(key, 3) over(partition by game_id order by game_id, time) following3_key
    , time
    , lead(time, 3) over(partition by game_id order by game_id, time) following3_time
    , game_id

from keys_pressed
where 1=1
    and correct_key = 1
    and game_id > 100
)

select 
    key || '-' || following_key || '-' || following2_key || '-' || following3_key as key_combination
    , avg(following3_time - time) as time_diff
    , count(*) count

from tbl1
where 1=1
    and following_key is not null
group by 1
having 1=1
    and count > 20
    and time_diff is not null
order by time_diff asc
