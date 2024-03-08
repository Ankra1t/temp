CREATE TABLE
  `users` (
    "id_idx" integer not null primary key autoincrement,
    -- `created_at` datetime not null default CURRENT_TIMESTAMP,
    -- "username" varchar(255) NULL,
    -- "count_sub" INT NULL,
    -- "count_days" INT NULL,
    -- "refer" INT NULL,
    -- -- "pay_money" INT2 NULL,
    -- "balance" INT2 NULL,
    -- "count_les" INT NULL,
    -- "id" INT2 NULL,
    -- "ban" DATETIME NULL,
  );

  CREATE TABLE
  `calc_user_settings` (
    "id" integer not null primary key,
    "created_at" datetime not null default CURRENT_TIMESTAMP,
    "base_deposit" FLOAT NULL,
    "base_risk" FLOAT NULL,
  );

  CREATE TABLE
  `workers` (
    `id_idx` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `username` varchar(255) null,
    `role` TINYINT null,
    "id" INT2 NULL
  );

  CREATE TABLE
  `pay` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `name` varchar(255) null,
    `value` varchar(255) null
  );

CREATE TABLE
  `prices` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `name` varchar(255) null,
    "currency" varchar(255) NULL,
    "price" FLOAT NULL,
    "description" TEXT NULL,
    "img" varchar(255) NULL,
    "duration_days" INT NULL DEFAULT 0,
    "discount_percent" FLOAT NULL DEFAULT 0,
    "discount_findate" DATETIME NULL
  );

  CREATE TABLE
  `fut_posts` (
    `id_idx` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `img` TEXT null,
    `text` TEXT null,
    `type` varchar(255) null,
    `date` VARCHAR(255) null,
    `time` VARCHAR(255) null,
    `id` INT null
  );

  CREATE TABLE
  `posts` (
    `id` integer not null primary key autoincrement,
    `content` TEXT not null,
    `mes_type` varchar(20) DEFAULT `text`,
    `direct` varchar(20) DEFAULT `Всем`,
    `media` TEXT null,
    `date_time` datetime not null,
    `name`: TEXT null,
    `open_price`: FLOAT null,
    `stop_loss`: FLOAT null,
    `ticker`: VARCHAR(20) null,
  );

  CREATE TABLE
  `transactions` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `user_id` INT null,
    `code` varchar(255) null,
    `link` TEXT null,
    `sum` FLOAT null
  );

CREATE TABLE
  `other` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `name` varchar(255) null,
    `text` TEXT null
  );

CREATE TABLE
  `future` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `name` varchar(255) null,
    `step` varchar(255) null,
    `price_step` INT2 null
  );

CREATE TABLE
  `news` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `news` TEXT null
  );

  CREATE TABLE
  `forexes` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `pair` varchar(255) null,
    `price` FLOAT null,
    `help_pair` varchar(255) null
  );

  CREATE TABLE
  `subscribes` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `updated_at` DATETIME null default CURRENT_TIMESTAMP,
    `tg_user_id` varchar(255) null,
    `finish_dt` DATETIME null,
    `subscribe_type` varchar(255) null,
    `transactions_payed_id` varchar(255) null
  );


insert into prices (name, price, currency)
values
    ('Подписка на месяц на сигналы', 0.1, 'TON');


insert into workers (username, role, id)
values
    ('worker365', 1, 774944610),
    ('siturn4rex', 1, 626871943);

