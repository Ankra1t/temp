

create TABLE users(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    id_telegram INTEGER,
    deposit VARCHAR(255),
    count_update_dep INTEGER,
    date_register VARCHAR(255),
    currency VARCHAR(255),
    balance VARCHAR(255),
    not_news VARCHAR(255),
    not_signals VARCHAR(255),
    not_orders VARCHAR(255),
    def_save_order VARCHAR(255),
    type_trade VARCHAR(255),
);



create TABLE forex(
    paire VARCHAR(255),
    price numeric,
    help_paire VARCHAR(255)
);

create TABLE orders(
    id SERIAL PRIMARY KEY,
    userId VARCHAR,
    market VARCHAR,
    date VARCHAR,
    time VARCHAR,
    dep VARCHAR,
    risk VARCHAR,
    paire VARCHAR,
    symbol VARCHAR,
    open VARCHAR,
    stop VARCHAR,
    pips VARCHAR,
    valume VARCHAR,
    bay_on VARCHAR,
    tp_price VARCHAR,
    risk_money VARCHAR,
    cur VARCHAR,
    credit VARCHAR,
    lot VARCHAR,
    tp_money VARCHAR,
    multiplier VARCHAR,
    status VARCHAR,
    type_order VARCHAR,
    save_mode VARCHAR,
    time_die VARCHAR,
    date_die VARCHAR
);

create TABLE top_crypto(
    name VARCHAR,
    price VARCHAR,
    percent VARCHAR
);

CREATE TABLE
  `bot_texts` (
    `id` integer not null primary key autoincrement,
    `created_at` datetime not null default CURRENT_TIMESTAMP,
    `label` varchar(255) null,
    `content` TEXT null,
    `content_img` VARCHAR(255) null,
    `content_video` varchar(255) null,
    `category` varchar(255) null default main
  );

