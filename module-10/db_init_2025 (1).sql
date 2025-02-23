/*
    Title: db_init_2025.sql
    Author: Professor Sampson
	Modified by: Vaneshiea Bell, DeJanae Faison, Jess Monnier
    Date: 22 February 2025
    Description: outland database initialization script.
*/

-- create database if it doesn't exist yet
CREATE DATABASE IF NOT EXISTS outland;

-- drop database user if exists 
DROP USER IF EXISTS 'adm'@'localhost';

-- create movies_user and grant them all privileges to the movies database 
CREATE USER 'adm'@'localhost' IDENTIFIED WITH mysql_native_password BY 'adventure';

-- grant all privileges to the movies database to user movies_user on localhost 
GRANT ALL PRIVILEGES ON outland.* TO 'adm'@'localhost';

-- drop tables if they are present
DROP TABLE IF EXISTS guide_req_tracker;
DROP TABLE IF EXISTS guide_req;
DROP TABLE IF EXISTS trip_member;
DROP TABLE IF EXISTS trip;
DROP TABLE IF EXISTS rental_inventory;
DROP TABLE IF EXISTS rental;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_inventory;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS staff;

-- create the customer table 
CREATE TABLE customer (
    cust_id   		INT             NOT NULL        AUTO_INCREMENT,
    first_name  	VARCHAR(75)     NOT NULL,
	last_name		VARCHAR(75)		NOT NULL,
	phone_number	CHAR(12)		NOT NULL, -- 12-char for 555-555-5555 format
	addr_street		VARCHAR(75)		NOT NULL,
	addr_city		VARCHAR(30)		NOT NULL,
	addr_state		CHAR(2)			NOT NULL, -- 2-char for NE format
	addr_zip		INT				NOT NULL,
	email			VARCHAR(50)		NOT NULL,
     
    PRIMARY KEY(cust_id)
); 

-- create the staff table 
CREATE TABLE staff (
    staff_id    	INT             NOT NULL        AUTO_INCREMENT,
    first_name  	VARCHAR(75)     NOT NULL,
	last_name		VARCHAR(75)		NOT NULL,
	nick_name		VARCHAR(25),			  -- nick name is optional
    phone_number	CHAR(12)		NOT NULL, -- 12-char for 555-555-5555 format
	addr_street		VARCHAR(75)		NOT NULL,
	addr_city		VARCHAR(30)		NOT NULL,
	addr_state		CHAR(2)			NOT NULL, -- 2-char for NE format
	addr_zip		INT				NOT NULL,
	email			VARCHAR(50)		NOT NULL,
    salary			INT				NOT NULL,
    bonus			INT,					  -- not all employees get a bonus (mastly it's for the guides)
    staff_role		VARCHAR(20)		NOT NULL,
     
    PRIMARY KEY(staff_id)
); 

-- create the trip table and set the foreign keys
CREATE TABLE trip (
    trip_id			INT           	NOT NULL        AUTO_INCREMENT,
    destination 	VARCHAR(75)     NOT NULL,
    trip_start   	DATE     		NOT NULL,
	trip_end		DATE			NOT NULL,
	staff_id		INT				NOT NULL,
	unit_fee		INT 			NOT NULL,
	cust_primary	INT				NOT NULL,
	
    PRIMARY KEY(trip_id),

	CONSTRAINT fk_trip_staff_id -- this gives the foreign key a name for easy reference if we want to delete or change it later
    FOREIGN KEY(staff_id)
        REFERENCES staff(staff_id),
	
	CONSTRAINT fk_trip_cust_id
    FOREIGN KEY(cust_primary)
        REFERENCES customer(cust_id)
);
    
-- create the trip_members table and set the foreign keys, add check on cust_id
CREATE TABLE trip_member (
	id					INT 			NOT NULL	AUTO_INCREMENT,
	trip_id				INT				NOT NULL,
    date_of_birth		DATE			NOT NULL,
    reservations		VARCHAR(255),			  -- empty until reservations are booked
    waiver				MEDIUMBLOB		NOT NULL,
    email 				VARCHAR(50),			  -- email & phone only filled if no cust_id
    phone_number 		CHAR(12),
    cust_id		 		INT,					  -- only one trip member is required to have a customer account
    passport_status		VARCHAR(25) 	NOT NULL,
    emergency_number	CHAR(12)		NOT NULL,
    emergency_name  	VARCHAR(75)     NOT NULL,
    emergency_relation	VARCHAR(25)		NOT NULL,
    cost				FLOAT 			NOT NULL,
    
    PRIMARY KEY(id),
    
	CONSTRAINT fk_trip_members_trip_id
	FOREIGN KEY(trip_id)
		REFERENCES trip(trip_id),
	
	CONSTRAINT fk_trip_members_cust_id
	FOREIGN KEY(cust_id)
		REFERENCES customer(cust_id),
	
	-- ensure there's either a cust_id OR email and phone number
	-- this prevents duplication of info in the customer table
	CONSTRAINT check_cust_id CHECK(
	(cust_id IS NULL AND email IS NOT NULL AND phone_number IS NOT NULL)
	OR
	(cust_id IS NOT NULL and email IS NULL and phone_number IS NULL))
);

-- create order_inventory table and composite primary key
CREATE TABLE order_inventory (
	product_code		VARCHAR(75)		NOT NULL,
	product_condition	VARCHAR(9)		NOT NULL,
	name				VARCHAR(25)		NOT NULL,
    unit_price			FLOAT 			NOT NULL,
    stock				INT				NOT NULL,
    weight				INT				NOT NULL,
    dimensions 			VARCHAR(25) 	NOT NULL,
	description			VARCHAR(255)	NOT NULL,
	
	CONSTRAINT pk_product -- because any given product could have a new, used-good, or used-fair condition,
	PRIMARY KEY (product_code, product_condition) -- the pair forms a unique primary key
);

-- create orders table and add foreign key; note orders is plural where other table names aren't to deconflict with sql keyword
CREATE TABLE orders (
	order_id		INT				NOT NULL 	AUTO_INCREMENT,
    order_date 		DATE 			NOT NULL,
    cust_id			INT				NOT NULL,
    ship_street		VARCHAR(75),			  -- shipping address columns not used when pick up in store selected
	ship_city		VARCHAR(30),
	ship_state		CHAR(2),
	ship_zip		INT,
    
    PRIMARY KEY(order_id),
	
	CONSTRAINT fk_orders_cust_id
	FOREIGN KEY(cust_id)
		REFERENCES customer(cust_id)
);

-- create order_item table and add foreign keys
CREATE TABLE order_item (
	id					INT 			NOT NULL 	AUTO_INCREMENT,
	product_code		VARCHAR(75)		NOT NULL,
	product_condition	VARCHAR(9)		NOT NULL,
    quantity			INT 			NOT NULL,
    ship_tracking 		INT 			NOT NULL,
	order_id			INT				NOT NULL,
    
    PRIMARY KEY(id),
	
	CONSTRAINT fk_product
	FOREIGN KEY(product_code, product_condition)
		REFERENCES order_inventory(product_code, product_condition),
	
	CONSTRAINT fk_order_item_order_id
	FOREIGN KEY(order_id)
		REFERENCES orders(order_id)
);

-- create rental table and set foreign key
CREATE TABLE rental (
	rental_id	INT		NOT NULL 	AUTO_INCREMENT,
    rental_date	DATE	NOT NULL,
    cust_id		INT		NOT NULL,
    start_date	DATE 	NOT NULL,
    end_date	DATE	NOT NULL,
    
    PRIMARY KEY(rental_id),
    
	CONSTRAINT fk_rental_cust_id
	FOREIGN KEY(cust_id)
		REFERENCES customer(cust_id)
);

-- create rental inventory and set foreign keys
CREATE TABLE rental_inventory (
	item_id 			INT			NOT NULL	AUTO_INCREMENT,
    initial_use			DATE,				  -- this value is not filled until first time item is rented
    rate				FLOAT		NOT NULL,
    product_condition 	VARCHAR(25)	NOT NULL,
    product_code		VARCHAR(75)	NOT NULL,
    rental_id			INT,				  -- this value is only filled when the item is currently rented/reserved
    
    PRIMARY KEY(item_id),
	
	CONSTRAINT fk_rental_inventory_rental_id
	FOREIGN KEY(rental_id)
		REFERENCES rental(rental_id),
	
	CONSTRAINT fk_rental_inventory_product
	FOREIGN KEY(product_code)
		REFERENCES order_inventory(product_code)
);

-- create guide_req table
CREATE TABLE guide_req (
	req_id			INT				NOT NULL	AUTO_INCREMENT,
	name			VARCHAR(75)		NOT NULL,
	description		VARCHAR(255)	NOT NULL,
	valid_months	INT,					  -- number of months req is valid once obtained; if empty, never expires
	governing_org	VARCHAR(255)	NOT NULL,
	
	PRIMARY KEY(req_id)
);

-- create guide_req_tracker table and add foreign keys
CREATE TABLE guide_req_tracker (
	id				INT				NOT NULL	AUTO_INCREMENT,
	complete_date	DATE,					  -- can be empty if member has not completed it yet
	status			VARCHAR(25)		NOT NULL,
	req_id			INT				NOT NULL,
	staff_id		INT				NOT NULL,
	
	PRIMARY KEY(id),
	
	CONSTRAINT fk_guid_req_tracker_staff_id
    FOREIGN KEY(staff_id)
        REFERENCES staff(staff_id),
	
	CONSTRAINT fk_guide_req_tracker_req_id
    FOREIGN KEY(req_id)
        REFERENCES guide_req(req_id)
);

-- insert customers
INSERT INTO customer 
(first_name, last_name, phone_number, addr_street, 
	addr_city, addr_state, addr_zip, email)
VALUES 
("John", "Doe", "555-555-1234", "123 West Adventure Terrace", 
	"Denver", "CO", 80014, "john.doe.3535@gmail.com"),
("Sally", "Ride", "555-555-2323", "418 Slip St Apt 3",
	"Palatine", "IL", 60067, "sally.rides.again@gmail.com");

-- insert staff, example with all fields and with no nick name/bonus
INSERT INTO staff 
(first_name, nick_name, last_name, phone_number, addr_street,
	addr_city, addr_state, addr_zip, email,
	salary, bonus, staff_role)
VALUES 
("John", "Mac", "MacNell", "555-555-4321", "5612 Wandering Rd",
	"Denver", "CO", 80016, "mac@outlandadventures.com",
	48000, 50, "Guide"),
("Blythe", NULL, "Timmerson", "555-555-8111", "2380 Chipper Ave",
	"Denver", "CO", 80016, "blythe@outlandadventures.com",
	75000, NULL, "Owner");

/*
INSERT INTO trip 
(destination, trip_start, trip_end, staff_id, unit_fee, cust_primary)
VALUES 
("Zimbabwe, Africa", "2024-09-15", "2024-09-21", 
	(
);

-- example of someone with an account/customer id
INSERT INTO trip_members (
	trip_id,
	date_of_birth,
	reservations,
	waiver,
	cust_id,
	passport_status,
	emergency_number,
	emergenc
*/