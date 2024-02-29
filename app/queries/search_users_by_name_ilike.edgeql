with name:= <optional str>$name ?? "%",
     name:= "%" ++ <str>$name ++ "%",
     users:= (select User filter .name ilike name),
select users.name;