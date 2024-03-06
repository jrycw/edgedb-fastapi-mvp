delete Event;
delete User;
with data := <json>$data,
for item in json_array_unpack(data) union (
select (insert Event { name := <str>item['name'],
                       address := <optional str>item['address'] ?? <str>{},
                       schedule := <datetime>(<optional str>item['schedule'] ?? <str>{}), 
                       host := (insert User {name:= <str>item['host_name']})
                      }
        ) {name, address, schedule, host_name:=.host.name}
);