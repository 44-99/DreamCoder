-- search_path: "$user", public


CREATE TABLE game_templates (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	game_type VARCHAR(50), 
	tech_stack VARCHAR(50), 
	mechanics JSON, 
	file_structure JSON, 
	reference_code TEXT, 
	vector_embedding BYTEA, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT game_templates_pkey PRIMARY KEY (id), 
	CONSTRAINT game_templates_name_key UNIQUE NULLS DISTINCT (name)
);


CREATE TABLE users (
	id SERIAL NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	hashed_password VARCHAR(100) NOT NULL, 
	phone VARCHAR(20), 
	email VARCHAR(50), 
	avatar VARCHAR(200), 
	is_active BOOLEAN NOT NULL, 
	CONSTRAINT users_pkey PRIMARY KEY (id), 
	CONSTRAINT users_username_key UNIQUE NULLS DISTINCT (username)
);

INSERT INTO users (username, hashed_password, phone, email, avatar, is_active) VALUES ($dump$陈世有$dump$, $dump$$2b$12$5o6EUBYQfnUqv/aB0JMjNup9jJXJ9nkFgitdALUbJ2Orr64WfbChi$dump$, NULL, $dump$12211931@mail.sustech.edu.cn$dump$, $dump$/static/avatars/user_1.jpg$dump$, true);


CREATE TABLE game_projects (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	game_type VARCHAR(50), 
	tech_stack VARCHAR(50), 
	status VARCHAR(40) NOT NULL, 
	files JSON, 
	deployment_url VARCHAR(300), 
	quality_score DOUBLE PRECISION, 
	generation_time DOUBLE PRECISION, 
	langsmith_run_id VARCHAR(100), 
	metadata JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT game_projects_pkey PRIMARY KEY (id), 
	CONSTRAINT game_projects_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE chat_messages (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	content TEXT NOT NULL, 
	message_type VARCHAR(50), 
	extra_data JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT chat_messages_pkey PRIMARY KEY (id), 
	CONSTRAINT chat_messages_project_id_fkey FOREIGN KEY(project_id) REFERENCES game_projects (id)
);

CREATE TABLE generation_steps (
	id SERIAL NOT NULL, 
	project_id INTEGER NOT NULL, 
	step_name VARCHAR(100) NOT NULL, 
	step_type VARCHAR(50), 
	status VARCHAR(40) NOT NULL, 
	input_data JSON, 
	output_data JSON, 
	error_message TEXT, 
	duration DOUBLE PRECISION, 
	langsmith_trace_id VARCHAR(100), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT generation_steps_pkey PRIMARY KEY (id), 
	CONSTRAINT generation_steps_project_id_fkey FOREIGN KEY(project_id) REFERENCES game_projects (id)
);
