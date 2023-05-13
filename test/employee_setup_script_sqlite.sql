-- Script to setup Postgres Instance for Employee Data Demo

--------------------------------------------------------------------------------------
-- DEFINITIONS
--------------------------------------------------------------------------------------

-- Create Companies Table

create table companies (
	company_id VARCHAR (20) primary key,
	company_name VARCHAR (100) not null,
	company_city VARCHAR (50)
);

-- Create Department Table

create table departments (
	department_id VARCHAR (20) primary key,
	department_type VARCHAR (100) not null
);

-- Create Employees Table

create table employees (
	employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
	name VARCHAR (100) not null,
	email VARCHAR (100) not null,
	department VARCHAR (20) references departments(department_id),
	company VARCHAR (20) references companies(company_id),
	dob DATE not null,
	birth_day VARCHAR (20)
);

--------------------------------------------------------------------------------------
-- INSERTS
--------------------------------------------------------------------------------------

-- Insert Companies
insert into companies(company_id, company_name, company_city) values ('ACN_KOL', 'Accenture', 'Kolkata'), ('IBM_KOL', 'IBM', 'Kolkata'), ('TCS_BNG', 'TCS', 'Bangalore');

-- Insert Department
insert into departments(department_id, department_type) values ('ENG_HWD', 'Hardware Engineering'), ('ENG_SW', 'Software Engineering'), ('HR', 'Human Resource'), ('MGMT', 'Manager');

-- Insert Employees
insert into employees(name, email, department, company, dob) values 	('san', 'san@gmail.com', 'ENG_SW', 'IBM_KOL', '1962-04-20'),
                                                                        ('jew', 'jew@gmail.com', 'MGMT', 'ACN_KOL', '1960-01-10'),
                                                                        ('ami', 'ami@gmail.com', 'MGMT', 'TCS_BNG', '1959-06-18'),
                                                                        ('dab', 'dab@hotmail.com', 'ENG_HWD', 'TCS_BNG', '1965-03-12'),
                                                                        ('jad', 'jad@space.com', 'ENG_SW', 'IBM_KOL', '1960-05-22'),
                                                                        ('kun', 'kun@gmail.com', 'ENG_SW', 'IBM_KOL', '1968-08-17'),
                                                                        ('xun', 'xun@gmail.com', 'ENG_SW', 'IBM_KOL', '1956-09-02'),
                                                                        ('kom', 'kom@hotmail.com', 'ENG_HWD', 'TCS_BNG', '1965-05-10');


--------------------------------------------------------------------------------------
-- VIEWS
--------------------------------------------------------------------------------------

-- View Companies
-- select * from companies;

-- View Department
-- select * from departments;

-- View Employees
-- select * from employees;

