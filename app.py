from flask import Flask, render_template, request, Response
from initialise import initialise,shot
# from camera_module import shot
import math
import pandas as pd
import time

app = Flask(__name__)

# t_camera = []
seconds = 10
d = 0.3291
g = 9.81
delta = 0.02
t1 = 0
size = 300
master_table = pd.read_csv('master_table.csv')


@app.route("/temp", methods=['GET', 'POST', 'PUT'])
def home():
    username = request.args.get('username')
    return render_template('index1.html', username=username)


@app.route("/", methods=['GET', 'POST', 'PUT'])
def home1():
    return render_template('basic.html')


def isInGoal(point, point1):
    if point[0] > point1[0]:
        return True
    else:
        return False


@app.route('/form-handler1', methods=['GET'])
def calculate_1():
    global hittingPos, holePos, phi_angle, beta_angle, username
    hittingPos = int(request.args.get('hittingPosition'))
    holePos = int(request.args.get('holePosition'))
    phi_angle = float(request.args.get('phi_angle'))
    beta_angle = float(request.args.get('beta_angle'))
    username = request.args.get('username')

    data_points_upper = []
    data_points_lower = []

    row, col = hittingPos // 12, hittingPos % 12
    hit_x, hit_y = (col - 1) * size + size / 2, (row * size) + size / 2
    phi = phi_angle * math.pi / 180
    beta = beta_angle * math.pi / 180
    df = master_table[
        (master_table['Hitting Row'] == 'R' + str(row + 1)) & (master_table['Hitting Col'] == 'C' + str(col))]

    row, col = holePos // 12, holePos % 12
    hole_x, hole_y = (col - 1) * size + size / 2, (row * size) + size / 2
    df = df[(df['Hole Row'] == 'R' + str(row + 1)) & (df['Hole Col'] == 'C' + str(col))]

    df = df[df['Phi'] == float(phi_angle)]
    df = df[df['Beta'] == float(beta_angle)]
    flag = False
    for u, theta in zip(df.u.values, df.theta.values):
        t1 = 0
        theta = theta * math.pi / 180
        inHole = False
        cnt = 0
        start_x, start_y = hit_x, hit_y

        while not inHole and cnt < 150:
            Vx = u * math.cos(theta) - (d * math.cos(theta) + g * math.sin(beta)) * t1
            Vy = u * math.sin(theta) - (d * math.sin(theta) + g * math.sin(phi)) * t1
            v = math.sqrt(Vx ** 2 + Vy ** 2)
            theta_ = math.atan(Vy / Vx)
            Sx = v * math.cos(theta_) * delta - 0.5 * ((d * math.cos(theta_) + g * math.sin(beta)) * delta ** 2)
            Sy = v * math.sin(theta_) * delta - 0.5 * ((d * math.sin(theta_) + g * math.sin(beta)) * delta ** 2)

            cnt += 1

            x = int(start_x / 3 + (Sx * 1000) / 3)
            y = int(start_y / 3 + (Sy * 1000) / 3)
            point = {
                "initial_X": int(start_x / 3),
                "initial_Y": int(start_y / 3),
                "final_X": x,
                "final_Y": y
            }
            if flag == False:
                data_points_upper.append(point)
            else:
                data_points_lower.append(point)

            start_x = start_x + (Sx * 1000)
            start_y = start_y + (Sy * 1000)
            t1 = t1 + delta
            inHole = isInGoal((start_x, start_y), (hole_x, hole_y))

        flag = True

    python_data = {
        'hit_x': str(hit_x / 3),
        'hit_y': str(hit_y / 3),
        'hole_x': str((hole_x) / 3 - 50),
        'hole_y': str((hole_y) / 3 - 50)
    }
    return render_template('beforeshoot.html', python_data=python_data,
                           data_points_upper=data_points_upper,
                           data_points_lower=data_points_lower,
                           username=username)


@app.route('/form-handler2', methods=['GET'])
def calculate_2():
    global hittingPos, holePos, phi_angle, beta_angle, username, t_camera
    data_points_upper = []
    data_points_lower = []

    row, col = hittingPos // 12, hittingPos % 12
    hit_x, hit_y = (col - 1) * size + size / 2, (row * size) + size / 2
    phi = phi_angle * math.pi / 180
    beta = beta_angle * math.pi / 180
    df = master_table[
        (master_table['Hitting Row'] == 'R' + str(row + 1)) & (master_table['Hitting Col'] == 'C' + str(col))]

    row, col = holePos // 12, holePos % 12
    hole_x, hole_y = (col - 1) * size + size / 2, (row * size) + size / 2
    df = df[(df['Hole Row'] == 'R' + str(row + 1)) & (df['Hole Col'] == 'C' + str(col))]

    df = df[df['Phi'] == float(phi_angle)]
    df = df[df['Beta'] == float(beta_angle)]
    flag = False
    for u, theta in zip(df.u.values, df.theta.values):
        t1 = 0
        theta = theta * math.pi / 180
        inHole = False
        cnt = 0
        start_x, start_y = hit_x, hit_y

        while not inHole and cnt < 150:
            Vx = u * math.cos(theta) - (d * math.cos(theta) + g * math.sin(beta)) * t1
            Vy = u * math.sin(theta) - (d * math.sin(theta) + g * math.sin(phi)) * t1
            v = math.sqrt(Vx ** 2 + Vy ** 2)
            theta_ = math.atan(Vy / Vx)
            Sx = v * math.cos(theta_) * delta - 0.5 * ((d * math.cos(theta_) + g * math.sin(beta)) * delta ** 2)
            Sy = v * math.sin(theta_) * delta - 0.5 * ((d * math.sin(theta_) + g * math.sin(beta)) * delta ** 2)

            cnt += 1

            x = int(start_x / 3 + (Sx * 1000) / 3)
            y = int(start_y / 3 + (Sy * 1000) / 3)
            point = {
                "initial_X": int(start_x / 3),
                "initial_Y": int(start_y / 3),
                "final_X": x,
                "final_Y": y
            }
            if flag == False:
                data_points_upper.append(point)
            else:
                data_points_lower.append(point)

            start_x = start_x + (Sx * 1000)
            start_y = start_y + (Sy * 1000)
            t1 = t1 + delta
            inHole = isInGoal((start_x, start_y), (hole_x, hole_y))

        flag = True

    python_data = {
        'hit_x': str(hit_x / 3),
        'hit_y': str(hit_y / 3),
        'hole_x': str((hole_x) / 3 - 50),
        'hole_y': str((hole_y) / 3 - 50)
    }

    user = t_camera
    return render_template('calculate.html', python_data=python_data,
                           data_points_upper=data_points_upper,
                           data_points_lower=data_points_lower,
                           user_points=user,
                           username=username)


@app.route('/project', methods=['GET'])
def project():
    data_points_upper = []
    data_points_lower = []

    row, col = hittingPos // 12, hittingPos % 12
    hit_x, hit_y = (col - 1) * size + size / 2, (row * size) + size / 2
    phi = phi_angle * math.pi / 180
    beta = beta_angle * math.pi / 180
    df = master_table[
        (master_table['Hitting Row'] == 'R' + str(row + 1)) & (master_table['Hitting Col'] == 'C' + str(col))]

    row, col = holePos // 12, holePos % 12
    hole_x, hole_y = (col - 1) * size + size / 2, (row * size) + size / 2
    df = df[(df['Hole Row'] == 'R' + str(row + 1)) & (df['Hole Col'] == 'C' + str(col))]

    df = df[df['Phi'] == float(phi_angle)]
    df = df[df['Beta'] == float(beta_angle)]
    flag = False
    for u, theta in zip(df.u.values, df.theta.values):
        t1 = 0
        theta = theta * math.pi / 180
        inHole = False
        cnt = 0
        start_x, start_y = hit_x, hit_y

        while not inHole and cnt < 150:
            Vx = u * math.cos(theta) - (d * math.cos(theta) + g * math.sin(beta)) * t1
            Vy = u * math.sin(theta) - (d * math.sin(theta) + g * math.sin(phi)) * t1
            v = math.sqrt(Vx ** 2 + Vy ** 2)
            theta_ = math.atan(Vy / Vx)
            Sx = v * math.cos(theta_) * delta - 0.5 * ((d * math.cos(theta_) + g * math.sin(beta)) * delta ** 2)
            Sy = v * math.sin(theta_) * delta - 0.5 * ((d * math.sin(theta_) + g * math.sin(beta)) * delta ** 2)

            cnt += 1

            x = int(start_x / 3 + (Sx * 1000) / 3)
            y = int(start_y / 3 + (Sy * 1000) / 3)
            point = {
                "initial_X": int(start_x / 3),
                "initial_Y": int(start_y / 3),
                "final_X": x,
                "final_Y": y
            }
            if flag == False:
                data_points_upper.append(point)
            else:
                data_points_lower.append(point)

            start_x = start_x + (Sx * 1000)
            start_y = start_y + (Sy * 1000)
            t1 = t1 + delta
            inHole = isInGoal((start_x, start_y), (hole_x, hole_y))

        flag = True

    python_data = {
        'hit_x': str(hit_x / 3),
        'hit_y': str(hit_y / 3),
        'hole_x': str((hole_x) / 3 - 50),
        'hole_y': str((hole_y) / 3 - 50)
    }

    return render_template('project.html', python_data=python_data,
                           data_points_upper=data_points_upper,
                           data_points_lower=data_points_lower,
                           username=username)


def gen(initialise):
    global t
    t = []
    i = True
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        frame = initialise.get_frame()

        if frame != 0 and elapsed_time < 15:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:

            frame = initialise.after_initialised()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            if i == True:
                t = initialise.Points()

                i = False


def pre(initialise):
    while True:
        frame = initialise.after_initialised()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def gen_camera(shot):
    # Shot = shot()
    global t_camera
    i = True
    time.sleep(1)
    shot.x_1 = abs(t[0])
    shot.x_2 = abs(t[1])
    shot.y_1 = abs(t[2])
    shot.y_2 = abs(t[3])
    shot.wid = abs(t[1])
    shot.het = abs(t[3])
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time_camera
        frame = shot.get_frame()

        if frame != 0 and elapsed_time < 15:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            frame = shot.after_initialised()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            if i == True:
                t_camera = shot.Points()
                i = False


def pre_camera(shot):
    while True:
        frame = shot.after_initialised()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/prevideo')
def prevideo():
    return Response(pre(initialise()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/preconfig')
def preconfig():
    return render_template('preconfig.html')


@app.route('/video')
def video():
    global start_time
    start_time = time.time()
    return Response(gen(initialise()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/config')
def config():
    return render_template('config.html')


# -------------------- Shooting windows-----------------------------------------#


@app.route('/preshotwin')
def preshotwin():
    return Response(pre_camera(shot()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/preShotWindow')
def preShotWindow():
    return render_template('preShotWindow.html')


@app.route('/shotwin')
def shotwin():
    global start_time_camera
    start_time_camera = time.time()
    return Response(gen_camera(shot()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/shotWindow')
def shotWindow():
    return render_template('shotWindow.html')


@app.route('/hello')
def index():
    if t != 0:
        return render_template('points.html', points=t)


if __name__ == "__main__":
    app.run(debug=True)

