select (
    update User filter .name = <str>$name
    set {name := <str>$new_name}
) {name, created_at};
