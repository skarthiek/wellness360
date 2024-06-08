from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import datetime
  
app = Flask(__name__)
app.secret_key = "secret_key"  # Secret key for session management

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['fitness_app']

class User:
    def __init__(self, username="", password=""):
        self.username = username
        self.password = password

def get_workout_suggestion(day):
    workouts = {
        "Monday": "CHEST\n1.Close grip press:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\n2.Flat Dumbell press:\n\t2 sets \n\t8-15 counts\n\tRest time:60 sec\n\n3.Dumbbel flys:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\n Note:-1.Put your max power on your chest rather than your hand\n2.Keep your back like ARCH position\n",
        "Tuesday": "Shoulder\n1.DB Shoulder press\n\t2 sets \n\t8-12 counts\n\tRest time:60 sec\n\n2.Dumbbel side risers:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\n3.Rear delt raiser:\n\t2 sets \n\t8-15 counts\n\tRest time:60 sec\n\nNote:-1.Put your max power on your shoulders not on forearms\n",
        "Wednesday": "Back\n1.Dumbel arm rows:\n\t2 sets \n\t8-12 counts\n\tRest time:60 sec\n\n2.Single arm rows:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\n3.DB Latpullover:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\nNote:-Focus on your target muscle",
        "Thursday": "ARMS \n1.Alternate Dumbel curls:\n\t2 sets \n\t20-15 counts\n\tRest time:60 sec\n\n2.Hammer curls:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\n3.Close grip dumbbel press:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\n4.Dumbbel Triesup extansion:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\nNote:-Focus on your target muscle",
        "Friday": "LEG\n1.Goblet squats:\n\t2 sets \n\t8-12 counts\n\tRest time:60 sec\n\n2.Walking lendes:\n\t1 set \n\t10-12 counts\n\tRest time:120 sec\n\n3.Standing Calf raises:\n\t2 sets \n\t10-15 counts\n\tRest time:60 sec\n\n Note:-Focus on your target muscle"

    }
    return workouts.get(day, "Rest")

def get_diet_plan(day, is_vegetarian):
    vegetarian_diet_plans = {
        "Monday": {
            "plan": "Breakfast: Moong Dal Chilla, Lunch: Paneer Tikka, Dinner: Mix Vegetable Curry",
            "recipes": {
                "Moong Dal Chilla": "1. Soak 1 cup moong dal overnight. 2. Grind the soaked dal into a smooth batter. 3. Add chopped onions, green chilies, and spices. 4. Cook on a non-stick pan.",
                "Paneer Tikka": "1. Marinate paneer with yogurt, spices, and lemon juice. 2. Grill until golden brown.",
                # Add other recipes...
            }
        },
        # Add other days...
    }
    non_vegetarian_diet_plans = {
               "Monday": {
            "plan": "Protein-Rich Non-Vegetarian Diet Plan for Monday:\n\nBreakfast: Egg Bhurji\nLunch: Grilled Chicken, Quinoa, Salad\nSnack: Boiled Eggs\nDinner: Fish Curry, Brown Rice",
            "recipes": {
                "Egg Bhurji": "1. Heat oil in a pan and sauté onions till golden brown.\n2. Add chopped tomatoes and spices.\n3. Add beaten eggs and cook till done.\n4. Serve hot with toast.",
                "Grilled Chicken": "1. Marinate chicken with yogurt, spices, and lemon juice.\n2. Grill the chicken until golden brown and cooked through.\n3. Serve hot with salad.",
                "Fish Curry": "1. Marinate fish with turmeric and salt.\n2. Heat oil in a pan and sauté onions till golden brown.\n3. Add ginger-garlic paste, tomatoes, and spices.\n4. Add marinated fish and cook till done.\n5. Serve hot with brown rice."
            }
        },
        "Tuesday": {
            "plan": "Protein-Rich Non-Vegetarian Diet Plan for Tuesday:\n\nBreakfast: Chicken Sandwich\nLunch: Lamb Curry, Brown Rice, Raita\nSnack: Chicken Salad\nDinner: Egg Curry, Chapati",
            "recipes": {
                "Chicken Sandwich": "1. Grill chicken breast and slice it.\n2. Place chicken slices between whole grain bread with lettuce, tomato, and sauce of your choice.\n3. Serve immediately.",
                "Lamb Curry": "1. Marinate lamb with yogurt, spices, and lemon juice.\n2. Heat oil in a pan and sauté onions till golden brown.\n3. Add ginger-garlic paste, tomatoes, and cook till soft.\n4. Add marinated lamb and cook till done.\n5. Serve hot with brown rice.",
                "Egg Curry": "1. Boil eggs and peel them.\n2. Heat oil in a pan and sauté onions till golden brown.\n3. Add ginger-garlic paste, tomatoes, and spices.\n4. Add boiled eggs and simmer for 10 minutes.\n5. Serve hot with chapati."
            }
        },
        "Wednesday": {
            "plan": "Protein-Rich Non-Vegetarian Diet Plan for Wednesday:\n\nBreakfast: Omelette with Spinach\nLunch: Turkey Breast, Sweet Potato, Stir-Fried Vegetables\nSnack: Protein Shake\nDinner: Grilled Fish, Quinoa",
            "recipes": {
                "Omelette with Spinach": "1. Beat eggs and mix with chopped spinach.\n2. Heat oil in a pan and pour the egg mixture.\n3. Cook till done and serve hot.",
                "Turkey Breast": "1. Marinate turkey breast with spices and lemon juice.\n2. Grill until golden brown and cooked through.\n3. Serve hot with sweet potato and stir-fried vegetables.",
                "Grilled Fish": "1. Marinate fish with lemon juice, garlic, and spices.\n2. Grill until golden brown and cooked through.\n3. Serve hot with quinoa."
            }
        },
        "Thursday": {
            "plan": "Protein-Rich Non-Vegetarian Diet Plan for Thursday:\n\nBreakfast: Dosa with Chutney\nMid-Morning Snack: Pear\nLunch: Roti, Bhindi Masala, Salad\nEvening Snack: Makhana\nDinner: Chapati, Vegetable Pulao, Dal Fry",
            "recipes": {
                "Dosa": "1. Soak rice and urad dal separately for 6 hours.\n2. Grind them into a smooth batter and ferment overnight.\n3. Pour a ladle of batter on a hot tawa and spread into a circle.\n4. Drizzle oil around the edges and cook till crisp.\n5. Serve hot with chutney.",
                "Bhindi Masala": "1. Heat oil in a pan and add chopped bhindi.\n2. Cook till bhindi is soft and slightly crispy.\n3. Add onions, tomatoes, and spices.\n4. Cook for another 5 minutes.\n5. Serve hot with roti.",
                "Vegetable Pulao": "1. Heat oil in a pan and add whole spices.\n2. Add chopped vegetables and sauté for 5 minutes.\n3. Add washed rice and mix well.\n4. Add water and cook till rice is done.\n5. Serve hot.",
                "Dal Fry": "1. Boil lentils with turmeric and salt.\n2. Heat oil in a pan and add cumin seeds.\n3. Add chopped onions, tomatoes, and spices.\n4. Add boiled lentils and simmer for 10 minutes.\n5. Garnish with coriander and serve hot."
            }
        },
        "Friday": {
            "plan": "Protein-Rich Non-Vegetarian Diet Plan for Friday:\n\nBreakfast: Paratha with Curd\nMid-Morning Snack: Guava\nLunch: Roti, Rajma, Salad\nEvening Snack: Vegetable Soup\nDinner: Chapati, Baingan Bharta, Raita",
            "recipes": {
                "Paratha": "1. Knead a dough with whole wheat flour and water.\n2. Roll out a portion of dough and cook on a hot tawa till golden brown.\n3. Serve hot with curd or pickle.",
                "Rajma": "1. Soak kidney beans overnight and pressure cook until soft.\n2. Heat oil in a pan and sauté onions till golden brown.\n3. Add ginger-garlic paste, tomatoes, and spices.\n4. Add cooked kidney beans and simmer for 10 minutes.\n5. Garnish with coriander and serve hot.",
                "Vegetable Soup": "1. Heat oil in a pot and sauté onions till golden brown.\n2. Add chopped vegetables and cook for 5 minutes.\n3. Add water or vegetable stock and simmer till vegetables are tender.\n4. Season with salt and pepper.\n5. Serve hot.",
                "Baingan Bharta": "1. Roast eggplants till the skin is charred and the flesh is soft.\n2. Peel and mash the roasted eggplants.\n3. Heat oil in a pan and sauté onions till golden brown.\n4. Add ginger-garlic paste, tomatoes, and spices.\n5. Add mashed eggplants and cook for 10 minutes.\n6. Garnish with coriander and serve hot with chapati."
            }
        }

        # Add other days...
    }
    if is_vegetarian:
        plan = vegetarian_diet_plans.get(day, {"plan": "Rest", "recipes": {}})
    else:
        plan = non_vegetarian_diet_plans.get(day, {"plan": "Rest", "recipes": {}})
    return plan["plan"], plan["recipes"]

@app.route('/')
def index():
    return render_template('Front.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    users_collection = db['users']

    if users_collection.find_one({"username": username}):
        flash("Username already exists. Please choose a different username.")
        return redirect(url_for('index'))

    users_collection.insert_one({"username": username, "password": password})
    flash("Account created successfully!")
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users_collection = db['users']

    user = users_collection.find_one({"username": username, "password": password})
    if user:
        session['username'] = username
        return redirect(url_for('health_details'))
    flash("Login failed. Incorrect username or password.")
    return redirect(url_for('index'))

@app.route('/health_details', methods=['GET', 'POST'])
def health_details():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        weight = float(request.form['weight'])
        height = int(request.form['height'])
        h = height / 100.0
        BMI = weight / (h * h)
        glucose = float(request.form['glucose'])
        systolic_bp = float(request.form['systolic_bp'])
        diastolic_bp = float(request.form['diastolic_bp'])
        is_vegetarian = request.form['is_vegetarian'].lower() == "yes"

        if glucose < 100:
            diabetes_result = "Normal"
        elif 100 <= glucose < 125:
            diabetes_result = "Prediabetes"
        else:
            diabetes_result = "Diabetes"

        if systolic_bp < 120 and diastolic_bp < 80:
            bp_result = "Normal"
        elif 120 <= systolic_bp < 130 and diastolic_bp < 80:
            bp_result = "Elevated"
        elif 130 <= systolic_bp < 140 or 80 <= diastolic_bp < 90:
            bp_result = "Hypertension Stage 1"
        elif systolic_bp >= 140 or diastolic_bp >= 90:
            bp_result = "Hypertension Stage 2"
        else:
            bp_result = "Hypertensive Crisis"

        today = datetime.datetime.now().strftime("%A")
        workout_suggestion = get_workout_suggestion(today)
        diet_plan, recipes = get_diet_plan(today, is_vegetarian)

        data = {
            "name": name,
            "weight": weight,
            "height": height,
            "BMI": BMI,
            "glucose": glucose,
            "diabetes_result": diabetes_result,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "bp_result": bp_result,
            "is_vegetarian": is_vegetarian,
            "workout_suggestion": workout_suggestion,
            "diet_plan": diet_plan,
            "recipes": recipes,
            "date": datetime.datetime.now()
        }
        db['user_health_data'].insert_one(data)
        return render_template('result.html', data=data)

    return render_template('health_details.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
