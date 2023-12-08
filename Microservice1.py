from fastapi import FastAPI, HTTPException, Form, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import aiomysql
import pandas as pd
from io import StringIO
from loguru import logger
from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from github import Github  # Import the Github class
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import re
# List
from typing import List

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",  # Add the origin of your React app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)
# Replace these with your actual database credentials
database_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "db": "DFS_Pro_new",
}

async def create_tables(course_name: str, conn):
    # Define the schemas for the three tables
    course_schema = """
        user_id INT PRIMARY KEY,
        role VARCHAR(255),
        name VARCHAR(255),
        email VARCHAR(255),
        team_id VARCHAR(100) DEFAULT NULL,
        project_id VARCHAR(100) DEFAULT NULL,
        task1 INT DEFAULT NULL,
        task2 INT DEFAULT NULL,
        task3 INT DEFAULT NULL,
        task4 INT DEFAULT NULL,
        task5 INT DEFAULT NULL,
        ta_userid VARCHAR(100) DEFAULT NULL,
        Final_grade VARCHAR(30) DEFAULT NULL,
        github_link VARCHAR(500) DEFAULT NULL
    """

    comments_schema = """
        team_id VARCHAR(100),
        comment VARCHAR(400),
        timestamp TIME
    """

    projects_schema = """
        project_id VARCHAR(30),
        template_id VARCHAR(30),
        num_tasks INT
    """

    code_project_schema = """
        project_id VARCHAR(30) PRIMARY KEY,
        project_name VARCHAR(255) NOT NULL,
        task1_description VARCHAR(500),
        task2_description VARCHAR(500),
        task3_description VARCHAR(500),
        task4_description VARCHAR(500),
        task5_description VARCHAR(500),
        task1_status VARCHAR(20),
        task2_status VARCHAR(20),
        task3_status VARCHAR(20),
        task4_status VARCHAR(20),
        task5_status VARCHAR(20),
        task1_commit_message VARCHAR(500),
        task2_commit_message VARCHAR(500),
        task3_commit_message VARCHAR(500),
        task4_commit_message VARCHAR(500),
        task5_commit_message VARCHAR(500)
    """

    research_project_schema = """
        project_id VARCHAR(30) PRIMARY KEY,
        project_name VARCHAR(255) NOT NULL,
        task1_description VARCHAR(500),
        task2_description VARCHAR(500),
        task3_description VARCHAR(500),
        task4_description VARCHAR(500),
        task5_description VARCHAR(500),
        task1_status VARCHAR(20),
        task2_status VARCHAR(20),
        task3_status VARCHAR(20),
        task4_status VARCHAR(20),
        task5_status VARCHAR(20),
        task1_commit_message VARCHAR(500),
        task2_commit_message VARCHAR(500),
        task3_commit_message VARCHAR(500),
        task4_commit_message VARCHAR(500),
        task5_commit_message VARCHAR(500)
    """

    normal_project_schema = """
        project_id VARCHAR(30) PRIMARY KEY,
        project_name VARCHAR(255) NOT NULL,
        task1_description VARCHAR(500),
        task2_description VARCHAR(500),
        task3_description VARCHAR(500),
        task4_description VARCHAR(500),
        task5_description VARCHAR(500),
        task1_status VARCHAR(20),
        task2_status VARCHAR(20),
        task3_status VARCHAR(20),
        task4_status VARCHAR(20),
        task5_status VARCHAR(20),
        task1_commit_message VARCHAR(500),
        task2_commit_message VARCHAR(500),
        task3_commit_message VARCHAR(500),
        task4_commit_message VARCHAR(500),
        task5_commit_message VARCHAR(500)
    """

    # Create the three tables with predefined schemas
    for table_name, schema in [
        ("_", course_schema),
        ("__comments", comments_schema),
        ("__projects", projects_schema),
        ("__codeproject", code_project_schema),
        ("__researchproject", research_project_schema),
        ("__normalproject", normal_project_schema)
    ]:
        query = f"""
        CREATE TABLE IF NOT EXISTS {course_name}{table_name} (
            {schema}
        );
        """
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            await conn.commit()

async def insert_sem_course(course_code: str, course_name: str, professor_email: str, conn):
    query = f"""
        INSERT INTO sem_courses (course_code, course_name, professor_email)
        VALUES (%s, %s, %s);
    """
    values = (course_code, course_name, professor_email)
    async with conn.cursor() as cursor:
        await cursor.execute(query, values)
        await conn.commit()


@app.post("/create-coursetable/")
async def create_table_endpoint(
    course_name: str = Form(...),
    professor_email: str = Form(...),
    course_code: str = Form(...)
):
    try:
        # Create a connection pool to the database
        async with aiomysql.create_pool(**database_config) as pool:
            async with pool.acquire() as conn:
                # Create the tables with the specified course name
                await create_tables(course_name, conn)

                # Insert data into sem_courses table
                await insert_sem_course(course_code, course_name, professor_email, conn)

        return JSONResponse(content={"message": f"Tables and data created successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

async def insert_data(course_name: str, file_contents: UploadFile = File(...), conn=None):
    try:
        # Read CSV data from file
        content = await file_contents.read()
        csv_data = StringIO(content.decode("utf-8"))
        df = pd.read_csv(csv_data)
        print(df.values.tolist())
        temp = df.values.tolist()

        # Insert data into the specified table
        table_name = f"{course_name}"  # Adjust table name as needed
        logger.info(f"Table name: {table_name}")
        async with conn.cursor() as cursor:
            for  row in temp:
                

                query = f"""
                    INSERT INTO {table_name} (user_id, role, name, email)
                    VALUES (%s, %s, %s, %s);
                """
                values = (row[0], row[1], row[2], row[3])
                logger.info(f"Executing query: {query} with values: {values}")
                await cursor.execute(query, values)
        await conn.commit()

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
@app.post("/insert-data/")
async def insert_data_endpoint(course_name: str = Form(...), file: UploadFile = File(...)):
    try:
        # Create a connection pool to the database
        course_name=course_name+"_"
        async with aiomysql.create_pool(**database_config) as pool:
            async with pool.acquire() as conn:
                # Insert data into the specified table
                await insert_data(course_name, file, conn)

        return JSONResponse(content={"message": f"Data inserted into {course_name} successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@app.post("/create-team/")
async def create_team_endpoint(
    course_name: str = Form(...),
    team_id: str = Form(...),
    selected_students: str = Form(...),
):  
    print(selected_students)
    try:
        # Create a connection pool to the database
        async with aiomysql.create_pool(**database_config) as pool:
            async with pool.acquire() as conn:
                # Parse selected students' emails
                selected_students_list = selected_students.split(',')

                # Update the dynamically named table with the team_id against each selected student's email
                for student_email in selected_students_list:
                    table_name = f"{course_name}_"
                    query = f"""
                        UPDATE {table_name}
                        SET team_id = %s
                        WHERE email = %s;
                    """
                    values = (team_id, student_email)
                    async with conn.cursor() as cursor:
                        await cursor.execute(query, values)
                        await conn.commit()

        return JSONResponse(content={"message": f"Team created and table updated successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
    
@app.post("/team-details/")
async def team_details_endpoint(course_name: str = Form(...)):
    try:
        course = course_name + "_"
        async with aiomysql.create_pool(**database_config) as pool:
            async with pool.acquire() as conn:
                # Define the SQL query
                sql_query = f"SELECT distinct team_id FROM {course}"

                # Execute the query
                async with conn.cursor() as cursor:
                    await cursor.execute(sql_query)
                    rows = await cursor.fetchall()

                # Extract course names from rows
                teams = [row[0] for row in rows]

                data = {}
                for team_name in teams:
                    if team_name is not None:
                        query = f"SELECT * FROM {course} WHERE team_id = %s"
                        async with conn.cursor() as cursor:
                            await cursor.execute(query, (team_name,))
                            rows = await cursor.fetchall()
                            # Convert each tuple into a dictionary and replace None with ""
                            data[team_name] = [
                                [value if value is not None else "" for value in row] for row in rows
                            ]

                return {"message": "Team details fetched successfully", "team_details": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def check_and_add_project_name_column(conn, table_name):
    try:
        async with conn.cursor() as cursor:
            # Check if the 'project_name' column exists in the table
            check_query = f"SHOW COLUMNS FROM {table_name} LIKE %s"
            await cursor.execute(check_query, ('project_name',))
            result = await cursor.fetchone()

            if not result:
                # If 'project_name' column doesn't exist, add it to the table
                alter_query = f"ALTER TABLE {table_name} ADD COLUMN project_name VARCHAR(255)"
                await cursor.execute(alter_query)
        await conn.commit()
    except Exception as e:
        logger.error(f"An error occurred while adding a column: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

async def insert_excel_data(course_name: str, project_type: str, file_contents: UploadFile = File(...), conn=None):
    try:
        # Read Excel data from file
        content = await file_contents.read()
        excel_data = pd.read_excel(content)
        temp = excel_data.values.tolist()

        # Insert data into the specified codeproject table
        codeproject_table_name = f"{course_name}__{project_type}project"  # Adjust table name as needed
        logger.info(f"Codeproject Table name: {codeproject_table_name}")
        async with conn.cursor() as cursor:
            for row in temp:
                query_codeproject = f"""
                    INSERT INTO {codeproject_table_name} (project_id, project_name, task1_description, task2_description, task3_description, task4_description, task5_description, task1_commit_message, task2_commit_message, task3_commit_message, task4_commit_message, task5_commit_message)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                values_codeproject = tuple(row)
                logger.info(f"Executing query: {query_codeproject} with values: {values_codeproject}")
                await cursor.execute(query_codeproject, values_codeproject)

        # Check and add 'project_name' column if not exists
        projects_table_name = f"{course_name}__projects"  # Adjust table name as needed
        logger.info(f"Projects Table name: {projects_table_name}")
        await check_and_add_project_name_column(conn, projects_table_name)

        # Insert data into the specified projects table
        async with conn.cursor() as cursor:
            for row in temp:
                project_id = row[0]
                project_name = row[1]
                query_projects = f"""
                    INSERT INTO {projects_table_name} (project_id, project_name, template_id)
                    VALUES (%s, %s, %s);
                """
                values_projects = (project_id, project_name, project_type)
                logger.info(f"Executing query: {query_projects} with values: {values_projects}")
                await cursor.execute(query_projects, values_projects)

        await conn.commit()

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@app.post("/insert-projectdetail/")
async def insert_excel_data_endpoint(
    course_name: str = Form(...),
    project_type: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        # Create a connection pool to the database
        course_name = course_name 
        async with aiomysql.create_pool(**database_config) as pool:
            async with pool.acquire() as conn:
                # Insert data into the specified tables
                await insert_excel_data(course_name, project_type, file, conn)

        return JSONResponse(content={"message": f"Data inserted into {course_name}_{project_type}project and {course_name}_projects successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
    


async def allot_project(course_name: str, proj_id: str, team_id: str):
    try:
        async with aiomysql.create_pool(**database_config) as pool:
            async with pool.acquire() as conn:
                print(course_name, proj_id, team_id)
                table_name = f"{course_name}_"
                query = f"""
                    UPDATE {table_name}
                    SET project_id = '{proj_id}'
                    WHERE team_id = '{team_id}';
                """
                # values = (table_name, proj_id, team_id)
                async with conn.cursor() as cursor:
                    await cursor.execute(query)
                    await conn.commit()

        return JSONResponse(content={"message": f"Project allotted to team {team_id} successfully"}, status_code=200)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
@app.post("/allot-project/")
async def allot(
    course_name: str = Form(...),
    proj_Id: str = Form(...),
    team: str = Form(...),
):
    result = await allot_project(course_name, proj_Id, team)
    return result



def get_github_commits_internal(owner: str, repo_name: str, access_token: str):
    # Create a Github instance and authenticate using the personal access token
    g = Github(access_token)

    try:
        # Get the repository
        repo = g.get_repo(f"{owner}/{repo_name}")

        # List all commits in the repository
        commits = repo.get_commits()

        # Extract commit information
        commit_list = [{'sha': commit.sha, 'message': commit.commit.message} for commit in commits]

        return commit_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-github-commits/")
async def get_github_commits(
    repo_url: str = Form(...),
#     token: str = Depends(get_current_user)
):
    try:
        # Extract the owner and repository name from the URL
        match = re.match(r"https://github\.com/([^/]+)/([^/]+)", repo_url)

        if not match:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL format")

        owner = match.group(1)
        print(owner)
        repo_name = match.group(2)
        print(repo_name)

        # Retrieve the GitHub personal access token from an environment variable
        access_token = "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"

        if not access_token:
            raise HTTPException(status_code=500, detail="GitHub personal access token not found")

        # Call the internal function to get GitHub commits
        commit_list = get_github_commits_internal(owner, repo_name, access_token)
        print(commit_list)
        return JSONResponse(content={"commits": commit_list}, status_code=200)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@app.post("/update-task-status/")
async def update_task_status(
    course_name: str = Form(...),
    project_type: str = Form(...),
    project_id: str = Form(...),
    commit_messages: List[str] = Form(...),

):
    print(course_name, project_type, project_id, commit_messages)
    try:
        # Form the table name based on the course_name and project_type
        print(commit_messages)
        async with aiomysql.create_pool(**database_config) as pool:
            async with pool.acquire() as conn:
             table_name = f"{course_name}__{project_type}project"

        # Iterate through each task number (1 to 5)
             for task_number in range(1, 6):
              task_status_column = f"task{task_number}_status"
              task_commit_message_column = f"task{task_number}_commit_message"

            # Check if the task_commit_message is present in the commit_messages list
              task_commit_message = f"{task_number}_commit_message"
              task_status_value = "completed" if task_commit_message in commit_messages else "not completed"

            # Update the task_status in the table
              query = f"""
                UPDATE {table_name}
                SET {task_status_column} = '{task_status_value}'
                WHERE project_id = '{project_id}';
            """
              async with conn.cursor() as cursor:
                await cursor.execute(query)
                await conn.commit()

        return {"message": "Task statuses updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
    

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
