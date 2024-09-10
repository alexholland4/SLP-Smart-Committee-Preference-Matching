###########################################################################################################
#  INPUT: This script takes in csv responses from a Google Form for students' top 3 committee prferences.
#  OUPTUT: This script automatically assigns students to commmittees, respecting their committee
#          preferences in prefered order and additionally respecting committee minimum/maximum sizes.
#
#  Author: Alex Holland
#  Date: 9/10/2024
###########################################################################################################

import pandas as pd
import random

# Load the student data from a CSV (comes from Google Form)
student_data = pd.read_csv('test_data_clean.csv')

# Define committees & the minimum and maximum size of each committee
committee_limits = {
    'ACLC': {'min': 2, 'max': 6},
    "Bucky's Award Ceremony": {'min': 2, 'max': 6},
    'Empower': {'min': 1, 'max': 5},
    'Marketing': {'min': 1, 'max': 3},
    'Socials': {'min': 1, 'max': 3},
    'SCSB': {'min': 1, 'max': 6}
}

# Initialize dictionary to store assigned students for each committee
assignments = {committee: [] for committee in committee_limits}

# Function to try to assign student to a committee based on choices
def assign_student(name, choices):
    for committee in choices:
        if len(assignments[committee]) < committee_limits[committee]['max']:
            assignments[committee].append(name)
            return True
    return False

# First: Initial assignment based on student preferences
for _, student in student_data.iterrows():
    name = student['Name']
    choices = [student['FirstChoice'], student['SecondChoice'], student['ThirdChoice']]
    
    if not assign_student(name, choices):
        # If no committee from choices was available, assign to any committee with space
        available_committees = [c for c in committee_limits if len(assignments[c]) < committee_limits[c]['max']]
        if available_committees:
            random_choice = random.choice(available_committees)
            assignments[random_choice].append(name)

# Second: Rebalancing to satisfy minimum requirements
def rebalance_assignments():
    underfilled_committees = [c for c in committee_limits if len(assignments[c]) < committee_limits[c]['min']]
    
    for committee in underfilled_committees:
        # Calculate how many more students are needed
        needed = committee_limits[committee]['min'] - len(assignments[committee])
        
        # Try to take students from overfilled or more-than-minimum-filled committees
        overfilled_committees = [c for c in assignments if len(assignments[c]) > committee_limits[c]['min']]
        
        while needed > 0 and overfilled_committees:
            for overfilled in overfilled_committees:
                if len(assignments[overfilled]) > committee_limits[overfilled]['min']:
                    # Move a student from an overfilled committee to the underfilled one
                    student_to_move = assignments[overfilled].pop()  # Remove last student from the overfilled committee
                    assignments[committee].append(student_to_move)   # Add to the underfilled committee
                    needed -= 1
                    if needed == 0:
                        break
            # Update the list of overfilled committees in case they drop below minimum
            overfilled_committees = [c for c in assignments if len(assignments[c]) > committee_limits[c]['min']]

# Call the rebalancing function
rebalance_assignments()

# Show the final assignments
for committee, students in assignments.items():
    print(f"{committee}: {students}")
