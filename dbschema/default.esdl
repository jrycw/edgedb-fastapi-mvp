# dbschema/default.esdl

module default {
  abstract type Auditable {
    required created_at : datetime {
      readonly := true;
      default := datetime_current();
    }
  }

  type User extending Auditable {
    required name : str {
      constraint exclusive;
      constraint max_len_value(50);
    };
  }

  type Event extending Auditable {
    required name : str {
      constraint exclusive;
      constraint max_len_value(50);
    }
    address : str;
    schedule : datetime;
    required host : User;
  }
}