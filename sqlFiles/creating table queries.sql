-- 1. Providers Table
create table providers (
	provider_id INTEGER PRIMARY KEY, 
	name TEXT, 
	type TEXT,
	address TEXT,
	city TEXT, 
	contact text 
);

-- 2. Receivers Table
create table receivers (
	receiver_id INTEGER PRIMARY KEY, 
	name TEXT, 
	type TEXT,
	city TEXT, 
	contact text 
);

-- 3. Food Listings Table
create table food_listings (
	food_id INTEGER PRIMARY KEY, 
	food_name TEXT, 
	quantity INTEGER,
	expiry_date DATE,
	provider_id integer references providers(provider_id),
	provider_type text,
	location text,
	food_type text,
	meal_type text
);

--4. Claims table
create table claims (
	claim_id integer primary key,
	food_id integer references food_listings(food_id),
	receiver_id integer references receivers(receiver_id),
	status text,
	Timestamp timestamp
);