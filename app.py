from flask import Flask, jsonify, redirect, request
from flask_cors import CORS

import evaluation as Evaluation
import label as Label
import label_type.question as Question
import task as Task
import user.level as Level
import user.user as User
from utils.constant import *
import utils.respond as Respond
import user.level as Level

# import ner as Ner

app = Flask(__name__)
CORS(app)

@app.route('/')
def main():
    return "finished"
@app.route("/user", methods=['POST'])
def login():
    data = request.json
    print(data)
    userId = data.get(USERID)
    if userId == None:
        return Respond.return_failed_with_msg("No userId")
    try:
        if User.login(userId):
            labeledInfo = User.get_user_info(userId)
            print(labeledInfo)
            return Respond.return_success_with_data(labeledInfo)
        else:
            return Respond.return_failed_with_msg("Login fail")
    except:
        return Respond.return_failed_with_msg("Login fail")

@app.route("/level", methods=['POST'])
def get_level():
    data = request.json
    userId = data.get(USERID)
    if userId == None:
        return Respond.return_failed_with_msg("No userId")
    try:
        result_list = Level.get_user_all_level(userId)
        return Respond.return_success_with_data(result_list)
    except:
        return Respond.return_failed()

@app.route("/tasks", methods=['GET'])
def tasks():
    try:
        result_dict = Task.get_all_task()
        # return jsonify(result_dict)
        return Respond.return_success_with_data(result_dict)
    except:
        return Respond.return_failed()

@app.route("/taskType", methods=["POST"])
def tasks_by_task_type():
    data = request.json
    taskType = data.get(TASKTYPE)
    try:
        result_dict = Task.get_task_by_task_type(taskType)
        return Respond.return_success_with_data(result_dict)
    except:
        return Respond.return_failed()

@app.route("/task", methods=['POST'])
def single_task():
    data = request.json
    taskId = data.get(TASKID)
    if taskId == None:
        return Respond.return_failed_with_msg("No taskId")
    try:
        result = Task.get_single_task(taskId)
        if result != None:
            return Respond.return_success_with_data(result)
        else:
            return Respond.return_failed()
    except:
        return Respond.return_failed()
@app.route("/task/getMyTask", methods=['POST'])
def get_my_task():
    data = request.json
    userId = data.get(USERID)
    try:
        return Respond.return_success_with_data(Task.get_self_uncheck_task(userId))
    except:
        return Respond.return_failed()

@app.route("/task/addTask", methods=['POST'])
def add_task():
    data = request.json
    # userId = data.get(TASKOWNERID)
    try:
        if Task.add_task(data):
            return Respond.return_success_with_data(data)
    except:
        return Respond.return_failed()

@app.route("/task/getQuestion", methods=['POST'])
def get_question():
    try:
        data = request.json
        taskId = data.get(TASKID)
        if taskId == None:
            return Respond.return_failed_with_msg("No taskId")
        question_list = Question.get_question(taskId)
        return Respond.return_success_with_data(question_list)
    except:
        return Respond.return_failed()

@app.route("/task/getLabel", methods=['POST'])
def get_lebel():
    try:
        data = request.json
        userId = data.get(USERID)
        taskId = data.get(TASKID)
        taskType = data.get(TASKTYPE)
        labelCount = data.get("labelCount")
        if taskId == None:
            return return_failed_with_msg("No taskId")
            # return jsonify("No taskId")
        result_label = Label.get_label(userId, taskId, taskType, labelCount)
        if taskType == CLASSIFICATION:
            result = {TASKID: taskId, TASKTYPE: taskType, "labelList": result_label}
            print(result)
            return Respond.return_success_with_data(result)
        if taskType == NER:
            result = {TASKID: taskId, TASKTYPE: taskType, "label": result_label}
            return Respond.return_success_with_data(result)
    except:
        return Respond.return_failed()
# not so good api
@app.route("/saveAnswer", methods=['POST'])
def saveAnser():
    data = request.json
    # try:
    taskId = data.get(TASKID)
    userId = data.get(USERID)
    print("data = ", data)
    if taskId == None or userId == None:
        return Respond.return_failed_with_msg("No taskId")
    result = Label.saveAnswer(data)
    if result != False:
        return Respond.return_success_with_data(result)
    else:
        return Respond.return_failed()
    # except:
    #     return Respond.return_failed()

@app.route("/accuracy", methods=["POST"])
def get_accuracy():
    data = request.json
    userId = data.get(USERID)
    taskId = data.get(TASKID)
    if userId == None or taskId == None:
        return Respond.return_failed_with_msg("No taskId or No userId")
    taskType = data.get(TASKTYPE)
    transId = data.get(TRANSACTIONID)
    try:
        if taskType == CLASSIFICATION:
            true_answer_list, pred_answer_list = Label.get_answer_pair(taskId, transId)
            accuracy = Evaluation.simple_accuracy(true_answer_list, pred_answer_list)
        elif taskType == NER:
            true_answer_list, pred_answer_list = Label.get_answer_pair(taskId, transId)
            question_list = Question.get_question(taskId)
            accuracy = Evaluation.blue_accuracy(true_answer_list, pred_answer_list, question_list)
        result = make_accuracy_response(accuracy, taskId, userId, taskType)
        return Respond.return_success_with_data(result)
    except:
        return Respond.return_failed()
@app.route("/task/rating", methods=["POST"])
def add_rating():
    try:
        data = request.json
        taskId = data.get(TASKID)
        userId = data.get(USERID)
        if userId == None or taskId == None:
            return Respond.return_failed_with_msg("No taskId or No userId")
        if Task.add_rating(taskId, data.get("score")):
            return Respond.return_success()
    except:
        return Respond.return_failed()

def make_accuracy_response(accuracy, taskId, userId, taskType):
    task_info = Task.get_single_task(taskId)
    level_info = Level.get_user_single_level(userId, taskType)
    level_result = Level.up_level(userId, taskType, level_info, int(20*accuracy))
    if level_result != False:
        result = {
        TASKID: taskId, 
        TASKTITLE: task_info.get(TASKTITLE),
        TASKTYPE: task_info.get(TASKTYPE),
        "taskExpValue": int(20*accuracy),
        "levelPercentage": level_result.get("levelPercentage"),
        "userLevel": level_result.get("level"),
        "accuracy": accuracy}
        return result

if __name__ == '__main__':
    app.run(debug=True, host=IP, port=8000)
