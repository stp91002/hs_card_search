CREATE TABLE card (
  card_name varchar(255) primary key,
  card_image_url text not null,
  card_mana TINYINT not null,
  card_text text,
  card_class TINYINT not null,
  card_type text not null,
  card_attack TINYINT,
  card_health TINYINT,
  card_series text not null,
  card_introduction text not null
)
  CHARACTER SET utf8 COLLATE utf8_general_ci;