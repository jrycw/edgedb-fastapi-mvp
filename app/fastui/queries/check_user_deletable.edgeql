with user:= assert_single((select User{events:= .<host[is Event]} filter .name=<str>$name)),
select not exists user.events;