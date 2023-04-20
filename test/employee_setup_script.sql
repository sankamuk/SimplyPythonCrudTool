-- Script to setup Postgres Instance for Employee Data Demo

--------------------------------------------------------------------------------------
-- DEFINITIONS
--------------------------------------------------------------------------------------

-- Create Audit Table

create table governance.sct_audits (
	audit_id serial PRIMARY KEY,
	audit_user VARCHAR (100) not null,
	audit_time timestamp NOT NULL DEFAULT NOW(),
    operation_performed VARCHAR (100) not null,
    table_name VARCHAR (100) not null,
    operation_status VARCHAR (15) not null,
    operation_metadata VARCHAR (5000)
);

-- Create Companies Table

create table public.companies (
	company_id VARCHAR (20) primary key,
	company_name VARCHAR (100) not null,
	company_city VARCHAR (50)
);

-- Create Department Table

create table public.departments (
	department_id VARCHAR (20) primary key,
	department_type VARCHAR (100) not null
);

-- Create Employees Table

create table public.employees (
	employee_id serial PRIMARY KEY,
	name VARCHAR (100) not null,
	email VARCHAR (100) not null,
	department VARCHAR (20) references public.departments(department_id),
	company VARCHAR (20) references public.companies(company_id),
	dob DATE not null,
	birth_day VARCHAR (20)
);

COMMENT ON COLUMN public.employees.birth_day is 'Not Updatable: Birth day field';

-- Populate dependent column (birth_day) for Employees table

-- Trigger function
CREATE FUNCTION public.employee_trigger() 
   RETURNS TRIGGER 
   LANGUAGE PLPGSQL
AS $func$
begin
	new.birth_day = to_char(new.dob, 'Day');
	return new;
END
$func$;


-- Trigger creation
CREATE TRIGGER employee_trigger 
	BEFORE insert or update ON public.employees
		FOR EACH ROW EXECUTE PROCEDURE public.employee_trigger();

	
--------------------------------------------------------------------------------------
-- INSERTS
--------------------------------------------------------------------------------------

-- Insert Companies
insert into public.companies(company_id, company_name, company_city) values ('ACN_KOL', 'Accenture', 'Kolkata'), ('IBM_KOL', 'IBM', 'Kolkata'), ('TCS_BNG', 'TCS', 'Bangalore');

-- Insert Department 
insert into public.departments(department_id, department_type) values ('ENG_HWD', 'Hardware Engineering'), ('ENG_SW', 'Software Engineering'), ('HR', 'Human Resource'), ('MGMT', 'Manager');

-- Insert Employees
insert into public.employees(name, email, department, company, dob) values 	('san', 'san@gmail.com', 'ENG_SW', 'IBM_KOL', '1962-04-20'), 
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
select * from public.companies;

-- View Department
select * from public.departments;

-- View Employees
select * from public.employees;


