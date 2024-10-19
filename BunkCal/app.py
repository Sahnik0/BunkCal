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

def calculate_bunkable_classes(total_classes, attended_classes):
    required_attendance = 0.75
    required_classes = math.ceil(required_attendance * total_classes)
    
    if attended_classes >= required_classes:
        max_bunkable_classes = total_classes - required_classes
    else:
        remaining_classes = total_classes - (attended_classes + (total_classes - attended_classes))
        max_bunkable_classes = max(0, remaining_classes - (required_classes - attended_classes))
    
    return max_bunkable_classes

def forecast_classes_needed(total_classes, attended_classes, future_total_classes):
    required_attendance = 0.75
    current_attendance_percentage = attended_classes / total_classes

    future_classes_needed = 0
    while (attended_classes + future_classes_needed) / future_total_classes < required_attendance:
        future_classes_needed += 1
        
    return future_classes_needed

def predict_future_bunks(total_classes, attended_classes, future_total_classes):
    required_attendance = 0.75
    required_future_attended = math.ceil(required_attendance * future_total_classes)
    
    future_bunkable_classes = future_total_classes - required_future_attended
    return future_bunkable_classes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Ensure form data is received correctly
        total_classes = int(request.form.get('total_classes', 0))
        attended_classes = int(request.form.get('attended_classes', 0))

        if total_classes == 0:
            return jsonify({'error': 'Total classes cannot be zero'}), 400

        attendance_percentage, error = calculate_attendance(total_classes, attended_classes)
        if error:
            return jsonify({'error': error}), 400

        save_to_csv(total_classes, attended_classes, attendance_percentage)

        bunkable_classes = calculate_bunkable_classes(total_classes, attended_classes)
        return jsonify({
            'attendance_percentage': f"{attendance_percentage:.2f}%",
            'bunkable_classes': bunkable_classes
        }), 200

    except Exception as e:
        # Log the exception and return a 500 error
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred on the server.'}), 500

@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        total_classes = int(request.form.get('total_classes', 0))
        attended_classes = int(request.form.get('attended_classes', 0))
        future_total_classes = int(request.form.get('future_total_classes', 0))

        if total_classes == 0 or future_total_classes == 0:
            return jsonify({'error': "Total classes and future total classes cannot be zero."}), 400

        future_classes_needed = forecast_classes_needed(total_classes, attended_classes, future_total_classes)
        future_bunkable_classes = predict_future_bunks(total_classes, attended_classes, future_total_classes)

        return jsonify({
            'future_classes_needed': future_classes_needed,
            'future_bunkable_classes': future_bunkable_classes
        }), 200

    except Exception as e:
        # Log the exception and return a 500 error
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred on the server.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
