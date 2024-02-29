with name := <str>$name,
    address := <optional str>$address ?? <str>{},
    schedule := <datetime>(<optional str>$schedule ?? <str>{}),
    host_name := <str>$host_name,
select (
    insert Event {
        name := name,
        address := address,
        schedule := schedule,
        host := (
            with u:= assert_single((select User filter .name = host_name)),
            select 
            if exists u then (u)
            else if exists host_name then (insert User {name:= host_name})
            else (<User>{})
        )
    }
) {name, address, schedule, host: {name}};