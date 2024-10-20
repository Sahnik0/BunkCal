from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

# Function to calculate attendance percentage
def calculate_attendance(total_classes, attended_classes):
    if total_classes == 0:
        return None, "Total classes cannot be zero."
    attendance_percentage = (attended_classes / total_classes) * 100
    return attendance_percentage, None

# Function to calculate bunkable classes
def calculate_bunkable_classes(total_classes, attended_classes, required_percentage):
    required_attendance = required_percentage / 100.0  # Convert percentage to decimal
    
    # Calculate the minimum number of classes needed to maintain required attendance
    min_required_classes = math.ceil(total_classes * required_attendance)
    
    if attended_classes >= min_required_classes:
        # If already meeting the requirement, calculate how many more can be missed
        bunkable_classes = attended_classes - min_required_classes
    else:
        # If below the requirement, can't miss any more classes
        bunkable_classes = 0
    
    return bunkable_classes

# Function to forecast classes needed to maintain required attendance
def forecast_classes_needed(total_classes, attended_classes, future_total_classes, required_percentage):
    required_attendance = required_percentage / 100.0
    
    future_classes_needed = max(0, math.ceil(future_total_classes * required_attendance) - attended_classes)
    
    return future_classes_needed

# Function to predict future bunkable classes based on future total classes
def predict_future_bunks(total_classes, attended_classes, future_total_classes, required_percentage):
    required_attendance = required_percentage / 100.0
    
    required_future_attended = math.ceil(future_total_classes * required_attendance)
    
    future_bunkable_classes = max(0, future_total_classes - required_future_attended)
    
    return future_bunkable_classes

# Main route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to calculate attendance and bunkable classes
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        total_classes = int(request.form['total_classes'])
        attended_classes = int(request.form['attended_classes'])
        
        # Optional percentage input from the user
        required_percentage = request.form.get('required_percentage', default=75)
        
        # Convert required_percentage to float
        required_percentage = float(required_percentage) if required_percentage else 75.0
        
        if total_classes == 0:
            return jsonify({'error': "Total classes cannot be zero."})
        
        if attended_classes > total_classes:
            return jsonify({'error': "Attended classes cannot be more than total classes."})
        
        attendance_percentage, error = calculate_attendance(total_classes, attended_classes)
        if error:
            return jsonify({'error': error})
        
        bunkable_classes = calculate_bunkable_classes(total_classes, attended_classes, required_percentage)
        
        return jsonify({
            'attendance_percentage': f"{attendance_percentage:.2f}%",
            'bunkable_classes': bunkable_classes
        })
    except ValueError:
        return jsonify({'error': "Invalid input. Please enter valid numbers."})
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"})

# Route to forecast future attendance and bunkable classes
@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        total_classes = int(request.form['total_classes'])
        attended_classes = int(request.form['attended_classes'])
        future_total_classes = int(request.form['future_total_classes'])
        
        # Optional percentage input from the user
        required_percentage = request.form.get('required_percentage', default=75)
        
        # Convert required_percentage to float
        required_percentage = float(required_percentage) if required_percentage else 75.0
        
        if total_classes == 0 or future_total_classes == 0:
            return jsonify({'error': "Total classes cannot be zero."})
        
        if attended_classes > total_classes:
            return jsonify({'error': "Attended classes cannot be more than total classes."})
        
        future_classes_needed = forecast_classes_needed(total_classes, attended_classes, future_total_classes, required_percentage)
        future_bunkable_classes = predict_future_bunks(total_classes, attended_classes, future_total_classes, required_percentage)
        
        return jsonify({
            'future_classes_needed': future_classes_needed,
            'future_bunkable_classes': future_bunkable_classes
        })
    except ValueError:
        return jsonify({'error': "Invalid input. Please enter valid numbers."})
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
