import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import ExcelWriter
from pandas import ExcelFile
import sqlite3
import os
conn = sqlite3.connect('marks_db.sqlite')
cur = conn.cursor()
conn.execute('CREATE TABLE grades_table (ID VARCHAR, Name VARCHAR, Prev_Grades, post_Fuzz_Grades VARCHAR)')
conn.commit()


def membership_fn(inp):
    opt = [0,0,0,0,0]
    if (0<=inp) and (inp<0.1):
       opt[0] = 1
       return opt
    elif (0.1<=inp) and (inp<=0.3) :
        opt[0] = (0.3-inp)/0.2
        opt[1] = (inp-0.1)/0.2
        return opt
    elif (0.3<=inp) and (inp<=0.5) :
        opt[1] = (0.5-inp)/0.2
        opt[2] = (inp-0.3)/0.2
        return opt
    elif (0.5<=inp) and (inp<=0.7) :
        opt[2] = (0.7-inp)/0.2
        opt[3] = (inp-0.5)/0.2
        return opt
    elif (0.7<=inp) and (inp<=0.9) :
        opt[3] = (0.9-inp)/0.2
        opt[4] = (inp-0.7)/0.2
        return opt
    elif (inp>0.9) and (inp<=1) :
        opt[4] = 1
        return opt
    elif (0>inp) or (inp>1) :
        return opt
    


data = pd.read_excel('marks.xlsx')
data.head()
idnum = data['ID'].values
names = data['Name'].values
attendence = data['Attendence'].values
quiz = data['Quiz'].values
lab = data['Lab'].values
mids = data['Mids'].values
compre = data['Compre'].values

num_students = len(attendence)
#cur.execute('select * from inputs_req') #it has to be taken as input later on
#max_marks = cur.fetchone()
max_marks = [100, 20, 10, 25, 45]
grade_vector = np.array(max_marks[1:])


accuracy_matrix = np.array([attendence/max_marks[0], quiz/max_marks[1], lab/max_marks[2], mids/max_marks[3], compre/max_marks[4]])
accuracy_matrix = accuracy_matrix.T
accuracy_vector = np.array([sum(attendence/max_marks[0])/num_students, sum(quiz/max_marks[1])/num_students, sum(lab/max_marks[2])/num_students, sum(mids/max_marks[3])/num_students, sum(compre/max_marks[4])/num_students])

#complexity and importance matrices  can be takenas input and put through membership functions for a proper use, for now i am taking an arbitrary value
complexity_matrix = [membership_fn(-1), membership_fn(0.46), membership_fn(0.61), membership_fn(0.7), membership_fn(0.85)]
comp_matrix = np.array(complexity_matrix)

importance_matrix = [membership_fn(0.24), membership_fn(0.35), membership_fn(0.45), membership_fn(0.55), membership_fn(0.65)]
imp_matrix = np.array(complexity_matrix)
#fuzzification:

fuzzy_acc_matrix = [membership_fn(accuracy_vector[0]), membership_fn(accuracy_vector[1]), membership_fn(accuracy_vector[2]), membership_fn(accuracy_vector[3]), membership_fn(accuracy_vector[4])]
fzam = np.array(fuzzy_acc_matrix)

#define rulebase
effort_base = [[1,1,2,2,3],[1,2,2,3,4],[2,2,3,4,4],[2,3,4,4,5],[3,4,4,5,5]]
adjustment_base = [[1,1,2,2,3],[1,2,2,3,4],[2,2,3,4,4],[2,3,4,4,5],[3,4,4,5,5]]
eff_base = np.array(effort_base)
adj_base = np.array(adjustment_base)

#inference:
def effort_lev(eff_base):
    eff_lev = []
    for i in range(1,6):
        eflev = []
        for j in range(5):
            for k in range(5):
                if(eff_base[j][k] == i):
                    eflev.append((j+1, k+1))
                    #print(j+1,"  ",k+1)
        eff_lev.append(eflev)
    return eff_lev

def get_eff_val(x, y, fzam, comp_matrix, eff_lev):
    result = 0
    for(i,j) in eff_lev[y]:
        if (fzam[x][i-1]<comp_matrix[x][j-1]):
            h = fzam[x][i-1]
        else:
            h = comp_matrix[x][j-1]
        if (result<h):
            result = h
    return result

def inference(eff_base, fzam, comp_matrix):
    eff_lev = effort_lev(eff_base)
    f_eff = np.zeros((5,5))
    for i in range(5):
        for j in range(5):
            f_eff[i][j] = get_eff_val(i, j, fzam, comp_matrix, eff_lev)
    return f_eff
    
    
fuzzy_effort= inference(eff_base, fzam, comp_matrix)
#print(fuzzy_effort)

def normalize_eff(fuzzy_effort):
    for i in range(5):
        row_sum = 0
        for j in range(5):
            row_sum+=fuzzy_effort[i][j]
        if row_sum!=0:
            for j in range(5):
                fuzzy_effort[i][j]/=row_sum
    return 

normalize_eff(fuzzy_effort)
#print(fuzzy_effort)

fuzzy_adj= inference(adj_base, fuzzy_effort, imp_matrix)
normalize_eff(fuzzy_adj)
#print(fuzzy_adj)

def vectorize(fuzzy_adj):
    adj_vec = []
    for i in range(5):
        rsum = 0
        for j in range(5):
            rsum+= fuzzy_adj[i][j] * (0.1+ 0.2*j)
        adj_vec.append(rsum/2.5)
    return adj_vec

adj_vec = vectorize(fuzzy_adj)
#print(adj_vec)

#defuzzification::
adj_grade_vec = []
for i in range(1,5):
    adj_grade_vec.append(max_marks[i]*(1+adj_vec[i]))

s=0
for i in range(1,5):
    s+= max_marks[i]
s= s/sum(adj_grade_vec)

for i in range(4):
    adj_grade_vec[i]*=s


"""
                                                        A                      >    X+2SD
                                                        
X+2SD  <                                            A-                        <=  X +1.5 SD

X+1.5SD <                                            B                      <= X+1.0SD

X + 1SD <                                             B-                        <= X+0.5SD

X+0.5SD  <                                            C                         <= X

X SD   <                                            C-                        <= X-0.5SD

X-0.5SD   <                                            D                         <=X -1 SD

X-1 SD    <                                              E                      <=X- 1.5 SD
    X-1.5 SD       <                                         NC
"""

def generate_grades(scores, mean_final, stddev_final):
    grades_final = []
    for i in scores:
        if i>= mean_final+2*stddev_final:
            grades_final.append('A')
        elif i<mean_final+2*stddev_final and i>mean_final+1.5*stddev_final:
            grades_final.append('A-')
        elif i<mean_final+1.5*stddev_final and i>mean_final+1.0*stddev_final:
            grades_final.append('B')
        elif i<mean_final+1.0*stddev_final and i>mean_final+0.5*stddev_final:
            grades_final.append('B-')
        elif i<mean_final+0.5*stddev_final and i>mean_final+stddev_final:
            grades_final.append('C')
        elif i<mean_final+stddev_final and i>mean_final-0.5*stddev_final:
            grades_final.append('C-')
        elif i<mean_final-0.5*stddev_final and i>mean_final-1.0*stddev_final:
            grades_final.append('D')
        elif i<mean_final-1.0*stddev_final and i>mean_final-1.5*stddev_final:
            grades_final.append('E')
        else:
            grades_final.append('NC')
    return grades_final

post_final_score= np.delete(accuracy_matrix, 1, 1).dot(adj_grade_vec)

post_mean = post_final_score.mean()
post_stddev = post_final_score.std()
post_grades=(generate_grades,post_mean, post_stddev)
post_grades = generate_grades(post_final_score,post_mean,post_stddev )

def attendence_effect(post_grades):
    for i in range(len(post_grades)):
        if post_grades[i]=='A-':
            if (post_final_score[i]- post_mean+2*post_stddev <= 2.5 and attendence[i]>80):
                post_grades[i] = 'A'
        elif post_grades[i]=='B':
            if (post_final_score[i]- post_mean+2*post_stddev <= 2.5 and attendence[i]>80):
                post_grades[i] = 'A-'
        elif post_grades[i]=='B-':
            if (post_final_score[i]- post_mean+2*post_stddev <= 2.5 and attendence[i]>80):
                post_grades[i] = 'B'
        elif post_grades[i]=='C':
            if (post_final_score[i]- post_mean+2*post_stddev <= 2.5 and attendence[i]>80):
                post_grades[i] = 'B-'
        elif post_grades[i]=='C-':
            if (post_final_score[i]- post_mean+2*post_stddev <= 2.5 and attendence[i]>80):
                post_grades[i] = 'C'
        elif post_grades[i]=='D':
            if (post_final_score[i]- post_mean+2*post_stddev <= 2.5 and attendence[i]>80):
                post_grades[i] = 'C-'
        elif post_grades[i]=='E':
            if (post_final_score[i]- post_mean+2*post_stddev <= 2.5 and attendence[i]>80):
                post_grades[i] = 'D'
        elif post_grades[i]=='NC':
            if (post_final_score[i]- post_mean+2*post_stddev <= 2.5 and attendence[i]>80):
                post_grades[i] = 'E'
        else:
            continue
    return post_grades
post_grades = attendence_effect(post_grades)


prev_final_score= np.delete(accuracy_matrix, 1, 1).dot(grade_vector)
prev_mean = prev_final_score.mean()
prev_stddev = prev_final_score.std()
prev_grades=(generate_grades,prev_mean, prev_stddev)
prev_grades = generate_grades(prev_final_score,prev_mean,prev_stddev )

for i in range(len(post_grades)):
    cur.execute('INSERT INTO grades_table (ID, Name , Prev_Grades, post_Fuzz_Grades) VALUES (?, ?,?,?)',(str(idnum[i]),names[i],prev_grades[i],post_grades[i]) )
    conn.commit()

conn.execute("DROP TABLE inputs_req")
conn.close()

os.remove('marks.xlsx')


#end of program









