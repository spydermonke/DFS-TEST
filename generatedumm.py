import pandas as pd

# Dummy data
data = {
    'project_id': ['proj4', 'proj5', 'proj6'],
    'project_name': ['Project 4', 'Project 5', 'Project 6'],
    'task1_': ['Task 1 of Project 4', 'Task 1 of Project 5', 'Task 1 of Project 6'],
    'task2_': ['Task 2 of Project 1', 'Task 2 of Project 2', 'Task 2 of Project 6'],
    'task3_': ['Task 3 of Project 1', 'Task 3 of Project 2', 'Task 3 of Project 6'],
    'task4_description': ['Task 4 of Project 4', 'Task 4 of Project 5', 'Task 4 of Project 6'],
    'task5_description': ['Task 5 of Project 4', 'Task 5 of Project 5', 'Task 5 of Project 6'],
    'task1_commit_message': ['Task 1 completed', 'Task 1 completed', 'Task 1 completed'],
    'task2_commit_message': ['Task 2 completed', 'Task 2 completed', 'Task 2 completed'],
    'task3_commit_message': ['Task 3 completed', 'Task 3 completed', 'Task 3 completed'],
    'task4_commit_message': ['Task 4 completed', 'Task 4 completed', 'Task 4 completed'],
    'task5_commit_message': ['Task 5 completed', 'Task 5 completed', 'Task 5 completed'],
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
file_path = 'dummy_dat.xlsx'
df.to_excel(file_path, index=False)

print(f'Dummy Excel file generated and saved at: {file_path}')
