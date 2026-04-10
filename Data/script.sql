create table food (
    fdc_id INTEGER PRIMARY KEY,
    data_type TEXT,
    description TEXT,
    food_category_id INTEGER,
    publication_date DATE
);




create table food_nutrients (
    id INTEGER PRIMARY KEY,
    fdc_id INTEGER,
    nutrient_id INTEGER,
    amount REAL,
    "data_points" INTEGER,
    "derivation_id" INTEGER,
    "min" REAL,
    "max" REAL,
    "median" REAL,
    "footnote" TEXT,
    "min_year_acquired" INTEGER,
    FOREIGN KEY (fdc_id) REFERENCES food(fdc_id)
);


create table nutrients (
    "id" INTEGER PRIMARY KEY,
    "name" TEXT,
    "unit_name" TEXT,
    "nutrient_nbr" INTEGER,
    "rank" INTEGER
);




create view food_nutrient_summary as
select 
    f.fdc_id, f.description, protein.amount as protein, carbs.amount as carbohydrates, calories.amount as calories, fiber.amount as fiber
from 
    food f
    left join (select fdc_id, amount from food_nutrients where nutrient_id = 1003) protein on f.fdc_id = protein.fdc_id
    left join (select fdc_id, amount from food_nutrients where nutrient_id = 1005) carbs on f.fdc_id = carbs.fdc_id
    left join (select fdc_id, amount from food_nutrients where nutrient_id = 2047) calories on f.fdc_id = calories.fdc_id
    left join (select fdc_id, amount from food_nutrients where nutrient_id = 1079) fiber on f.fdc_id = fiber.fdc_id
;

