select Event {
    name, 
    created_at,
    address,
    schedule,
    host_name:=.host.name
} filter .name=<str>$name;
