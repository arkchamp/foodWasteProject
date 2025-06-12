--1) How many food providers and receivers are there in each city? - using UNION ALL
--l
select city, count(provider_id) as  total_providers, count(receiver_id) as total_receivers
from(
	select city, provider_id, NULL::integer as receiver_id
	from providers
	union all
	select city, NULL::integer as provider_id, receiver_id
	from receivers
) as combined
group by city
order by city;
)




--2)Which type of food provider (restaurant, grocery store, etc.) contributes the most food?
-- with subqueries
-- l
select provider_type,sum(quantity) as total_quantity from food_listings
group by provider_type
having sum(quantity) = (
	select max(total_quantity) from (
		select sum(quantity) as total_quantity from food_listings
		group by provider_type
		)as sub
	)



--easy way
select provider_type, sum(quantity) as total_quantity from food_listings
group by provider_type
order by total_quantity desc
limit 1;

--3) What is the contact information of food providers in a specific city?
--l
select * from providers 	--% for prefix and suffix| lower for low case
where lower(city) like lower('%port%'); -- change city name to get contact info

-- 4) Which receivers have claimed the most food?

select name,count(claim_id) as total_claims 
from receivers r
join claims c 
on r.receiver_id = c.receiver_id
group by name,c.receiver_id
having count(claim_id) = (
	select max(total_claims) from(
		select count(claim_id) as total_claims from claims 
		group by receiver_id 
		)as sub
	)
order by c.receiver_id;

--rough work
select receiver_id , count(claim_id) as total_claim 
from claims
group by receiver_id
 having count(claim_id) = (
	select max(total_claims) from(
		select count(claim_id) as total_claims from claims 
		group by receiver_id 
		) as sub
	)
order by receiver_id

--with limit
SELECT name, COUNT(c.claim_id) AS total_claims
FROM receivers r
JOIN claims c 
ON r.receiver_id = c.receiver_id
GROUP BY name
ORDER BY total_claims DESC
LIMIT 5;



-- 5) What is the total quantity of food available from all providers?
select sum(quantity) as total_quantity_available from food_listings;

-- 6) Which city has the highest number of food listings?
select location, count(food_id) as total_listings from food_listings
group by location
having count(food_id) = (
select max(total_listings) from (
select count(food_id) as total_listings from food_listings
group by location)as sub
);

-- ez way
select location, count(food_id) as total_listings from food_listings
group by location
order by total_listings desc;

-- 7) What are the most commonly available food types?
select food_type, count(*) as most_common_foodType from food_listings
group by food_type
order by most_common_foodType desc

-- 8)How many food claims have been made for each food item?

select food_name,count(claim_id) as no_of_food_Claims from claims c 
join food_listings f
on c.food_id = f.food_id
group by food_name
order by no_of_food_Claims;

--9) Which provider has had the highest number of successful food claims?

select name, count(claim_id) as successful_claims from providers p
join food_listings f on p.provider_id = f.provider_id
join claims c on f.food_id = c.food_id
where status = 'Completed'
group by name
having count(claim_id) = (
	select max(max_claims) from (
		select count(claim_id) as max_claims from food_listings f
		join claims c on f.food_id = c.food_id
		where status = 'Completed'
		group by provider_id) as sub
	);

-- 10) What percentage of food claims are completed vs. pending vs. canceled?
select status, round(100 * count(*)/(select count(*) from claims), 2) as percentage from claims
group by status


-- 11) What is the average quantity of food claimed per receiver?
select name,round(avg(quantity),2) from food_listings f
join claims c on f.food_id = c.food_id
join receivers r on c.receiver_id = r.receiver_id
group by name

--12) Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?

select meal_type,count(claim_id) as total_claims from food_listings f
join claims c on f.food_id = c.food_id
group by meal_type
having count(claim_id) = (
select max(total_claims) from (
select count(claim_id) as total_claims from food_listings f
join claims c on f.food_id = c.food_id
group by meal_type)as sub)

-- 13) What is the total quantity of food donated by each provider?
select name as provider_name ,sum(quantity) as total_quantity from providers p
join food_listings f on p.provider_id = f.provider_id
group by name
order by total_quantity desc

-- **Extra 1) Which type of provider is most common?
select type, count(provider_id) as total_providers from providers
group by type
having count(provider_id) = (
	select max(total_providers) from(
		select count(provider_id) as total_providers from providers
		group by type)as sub
		);

-- **extra 2) Which receiver names appear most frequently in the database?
select name, count(receiver_id) as total_received from receivers
group by name
having count(receiver_id) = (
select max(total_received) from (select count(receiver_id) as total_received from receivers
group by name)as sub
);


-- ** Extra 3) Which meal types are most commonly listed by food providers?

select meal_type ,count(provider_id) as meal_type_count from food_listings
group by meal_type
having count(provider_id) = (
select max(meal_type_count) from (
select count(provider_id) as meal_type_count from food_listings
group by meal_type) as sub)



-- E4) Rank the Top food items claimed
select 
	food_name, 
	count(claim_id) as no_of_claimed_food,
	dense_rank() over (
    	ORDER BY count(claim_id) DESC
	) as food_rank
from food_listings f
join claims c on f.food_id= c.food_id
group by food_name

-- E5) List the total quantiy of food per item which were never claimed?

select food_name, sum(quantity) as total_item from food_listings f
left join claims c on f.food_id=c.food_id
where status is null
group by food_name



--E6) Top 5 cities with the most completed claims
select location, count(claim_id) as completed_claims from food_listings f
join claims c on f.food_id = c.food_id
where status = 'Completed'
group by location
order by completed_claims desc limit 5;

--E7) Provider-wise breakdown of claim statuses

select name, status,count(*) as total from providers p
join food_listings f on p.provider_id=f.provider_id
join claims c on c.food_id= f.food_id
group by name, status
order by name


--E8) Count of unique food items by provider

select name as provider_name,
	count(distinct(food_name)) as unique_food 
from providers p
join food_listings f on p.provider_id = f.provider_id
group by name
order by name

-- E9) Average quantity per food type
select food_type, round(avg(quantity),2) as avg_quantity from food_listings
group by food_type
order by avg_quantity

-- E10) Claims made per day (for trend chart)
select date(timestamp) as claim_date, count(claim_id) from claims
group by claim_date
order by claim_date







