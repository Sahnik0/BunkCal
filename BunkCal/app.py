from flask import Flask, render_template, request, jsonify
import csv
import os
import math

app = Flask(__name__)

def save_to_csv(total_classes, attended_classes, attendance_percentage):
    file_exists = os.path.isfile("attendance_data.csv")
    with open("attendance_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Total Classes Held", "Classes Attended", "Attendance Percentage"])
        writer.writerow([total_classes, attended_classes, f"{attendance_percentage:.2f}%"])

def calculate_attendance(total_classes, attended_classes):
    if total_classes == 0:
        return None, "Total classes cannot be zero."
    attendance_percentage = (attended_classes / total_classes) * 100
    return attendance_percentage, None

def calculate_bunkable_classes(total_classes, attended_classes, attendance_percentage):
    required_attendance = attendance_percentage / 100
    required_classes = math.ceil(required_attendance * total_classes)
    
    if attended_classes >= required_classes:
        max_bunkable_classes = total_classes - required_classes
    else:
        remaining_classes = total_classes - (attended_classes + (total_classes - attended_classes))
        max_bunkable_classes = max(0, remaining_classes - (required_classes - attended_classes))
    
    return max_bunkable_classes

def forecast_classes_needed(total_classes, attended_classes, future_total_classes, attendance_percentage):
    required_attendance = attendance_percentage / 100
    
    current_attendance_percentage = attended_classes / total_classes

    future_classes_needed = 0
    while (attended_classes + future_classes_needed) / future_total_classes < required_attendance:
        future_classes_needed += 1
        
    return future_classes_needed

def predict_future_bunks(total_classes, attended_classes, future_total_classes, attendance_percentage):
    required_attendance = attendance_percentage / 100
    
    required_future_attended = math.ceil(required_attendance * future_total_classes)
    
    future_bunkable_classes = future_total_classes - required_future_attended
    
    return future_bunkable_classes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    total_classes = int(request.form['total_classes'])
    attended_classes = int(request.form['attended_classes'])
    attendance_percentage = float(request.form['attendance_percentage'])

    attendance_percentage_calculated, error = calculate_attendance(total_classes, attended_classes)
    if error:
        return jsonify({'error': error})

    save_to_csv(total_classes, attended_classes, attendance_percentage_calculated)
    
    bunkable_classes = calculate_bunkable_classes(total_classes, attended_classes, attendance_percentage)
    return jsonify({
        'attendance_percentage': f"{attendance_percentage_calculated:.2f}%",
        'bunkable_classes': bunkable_classes
    })

@app.route('/forecast', methods=['POST'])
def forecast():
    total_classes = int(request.form['total_classes'])
    attended_classes = int(request.form['attended_classes'])
    future_total_classes = int(request.form['future_total_classes'])
    attendance_percentage = float(request.form['attendance_percentage'])
    
    if total_classes == 0 or future_total_classes == 0:
        return jsonify({'error': "Total classes cannot be zero."})

    future_classes_needed = forecast_classes_needed(total_classes, attended_classes, future_total_classes, attendance_percentage)
    future_bunkable_classes = predict_future_bunks(total_classes, attended_classes, future_total_classes, attendance_percentage)

    return jsonify({
        'future_classes_needed': future_classes_needed,
        'future_bunkable_classes': future_bunkable_classes
    })

if __name__ == '__main__':
    app.run(debug=True)
