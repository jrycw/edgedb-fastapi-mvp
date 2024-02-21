CREATE MIGRATION m1t4s2zsgjiurqmwgfreo6wt7duc2h44fes3m3qych2rirxwmklgqa
    ONTO initial
{
  CREATE ABSTRACT TYPE default::Auditable {
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
  };
  CREATE TYPE default::User EXTENDING default::Auditable {
      CREATE REQUIRED PROPERTY name: std::str {
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(50);
      };
  };
  CREATE TYPE default::Event EXTENDING default::Auditable {
      CREATE LINK host: default::User;
      CREATE PROPERTY address: std::str;
      CREATE REQUIRED PROPERTY name: std::str {
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(50);
      };
      CREATE PROPERTY schedule: std::datetime;
  };
};
