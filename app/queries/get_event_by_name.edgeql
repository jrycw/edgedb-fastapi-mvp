select Event {
    name, 
    created_at,
    address,
    schedule,
    host : {name}
} filter .name=<str>$name;
