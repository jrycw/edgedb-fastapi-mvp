delete Event;
delete User;
with data := <json>$data,
for item in json_array_unpack(data) union (
select (insert Event { name := <str>item['name'],
                       address := <optional str>item['address'] ?? <str>{},
                       schedule := <datetime>(<optional str>item['schedule'] ?? <str>{}), 
                       host := ( 
                            with host_name:= <str>item['host_name'],
                                 u:= assert_single((select User filter .name = host_name))
                            select 
                            if exists u then (u)
                            else (insert User {name:= host_name})
                        )
        }
) {name, address, schedule, host_name:=.host.name}
);