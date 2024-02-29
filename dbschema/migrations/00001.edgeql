CREATE MIGRATION m1hap22pa54folvlgr5w4iwft7xhw43nd32txuobmaf2b7rbkfujzq
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
      CREATE REQUIRED LINK host: default::User;
      CREATE PROPERTY address: std::str;
      CREATE REQUIRED PROPERTY name: std::str {
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(50);
      };
      CREATE PROPERTY schedule: std::datetime;
  };
};
