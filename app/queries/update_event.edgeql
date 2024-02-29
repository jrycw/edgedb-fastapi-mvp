with name := <str>$name,
     orig_event := assert_exists(assert_single((select Event filter .name=name))),
     orig_event_name:= orig_event.name,
     orig_event_address:= orig_event.address,
     orig_event_schedule:= orig_event.schedule,
     orig_event_host_name:= orig_event.host.name,
     new_name := <optional str>$new_name ?? orig_event_name,
     address := <optional str>$address ?? orig_event_address,
     schedule := <datetime>(<optional str>$schedule) ?? orig_event_schedule,
     host_name := <optional str>$host_name ?? orig_event_host_name,
select (
    update Event filter .name = name
    set {
        name := new_name,
        address := address,
        schedule := schedule,
        host := (
            with u:= assert_single((select detached User filter .name = host_name)),
            select 
            if exists u then (u)
            else if exists host_name then (insert User {name:= host_name})
            else (<User>{})
        )
    }
) {name, address, schedule, host: {name}};
