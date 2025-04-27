from flask import Flask, request, render_template_string
import psycopg2
import os

app = Flask(__name__)

# Database connection
try:
    conn = psycopg2.connect(
        dbname="farewell_db_ng3i",
        user="farewell_db_ng3i_user",
        password="12zw2quhNJY8C72FWN4qLE0QQ1C1zytY",
        host="dpg-d06rct3uibrs73es2pbg-a",
        port="5432",
        sslmode="require"  # important for Render
    )
    conn.autocommit = True
    print("✅ Database connected successfully.")
except Exception as e:
    conn = None
    print("❌ Error connecting to the database:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        try:
            student_name = request.form['name']
            student_id = request.form['student_id']

            if not student_name or not student_id:
                message = "Please fill all fields."
            elif conn is None:
                message = "Database connection failed."
            else:
                cur = conn.cursor()

                # Check if student_id is already used
                try:
                    cur.execute("SELECT * FROM coupon_used WHERE student_id = %s", (student_id,))
                    used = cur.fetchone()
                except Exception as e:
                    print("Error checking used coupons:", e)
                    used = None

                if used:
                    message = "Coupon already used!"
                else:
                    # Check if student_id is available
                    try:
                        cur.execute("SELECT * FROM coupon WHERE student_id = %s", (student_id,))
                        available = cur.fetchone()
                    except Exception as e:
                        print("Error checking available coupons:", e)
                        available = None

                    if available:
                        try:
                            # Insert into coupon_used
                            cur.execute(
                                "INSERT INTO coupon_used (student_id, name) VALUES (%s, %s)",
                                (student_id, student_name)
                            )
                            # Delete from coupon
                            cur.execute("DELETE FROM coupon WHERE student_id = %s", (student_id,))
                            message = "Coupon accepted! 🎉"
                        except Exception as e:
                            print("Error updating coupon tables:", e)
                            message = "Error redeeming coupon. Try again."
                    else:
                        message = "Invalid Coupon ID!"
                cur.close()

        except Exception as e:
            print("❌ Unexpected error during form processing:", e)
            message = "An unexpected error occurred. Please try again."

    return render_template_string('''
        <!doctype html>
        <html>
            <head><title>Coupon Redemption</title></head>
            <body style="text-align: center; margin-top: 50px;">
                <h1>Welcome to the Farewell Coupon Page</h1>
                <form method="POST">
                    <input type="text" name="name" placeholder="Your Name" required><br><br>
                    <input type="text" name="student_id" placeholder="Your Student ID" required><br><br>
                    <input type="submit" value="Redeem Coupon">
                </form>
                <h2 style="color:green;">{{ message }}</h2>
            </body>
        </html>
    ''', message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
