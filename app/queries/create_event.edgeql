with name := <str>$name,
    address := <str>$address,
    schedule := <datetime>$schedule,
    host_name := <str>$host_name

select (
    insert Event {
        name := name,
        address := address,
        schedule := schedule,
        host := assert_single(
            (select detached User filter .name = host_name)
        )
    }
) {name, address, schedule, host: {name}};
