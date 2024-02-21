with name := <str>$name,
    new_name := <str>$new_name,
    address := <str>$address,
    schedule := <datetime>$schedule,
    host_name := <str>$host_name

select (
    update Event filter .name = name
    set {
        name := new_name,
        address := address,
        schedule := schedule,
        host := (select User filter .name = host_name)
    }
) {name, address, schedule, host: {name}};
