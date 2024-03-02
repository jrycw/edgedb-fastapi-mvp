select (
    delete Event filter .name = <str>$name
) {name, address, schedule, host_name:=.host.name};
