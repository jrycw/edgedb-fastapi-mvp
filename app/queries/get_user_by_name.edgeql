select User {name,
            created_at, 
            n_events:= count(.<host[is Event])
        } 
filter User.name=<str>$name;

