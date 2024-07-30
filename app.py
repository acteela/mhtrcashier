from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
import random
import string

app = Flask(__name__)

# Fungsi untuk menghubungkan ke database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="mahatari_db"
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        return None

# Route untuk halaman utama
@app.route('/')
def index():
    current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    return render_template('index.html', datetime=current_datetime)

# Route untuk menangani transaksi
@app.route('/transaksi', methods=['POST'])
def transaksi():
    data = request.get_json()  # Mengambil data JSON dari request
    items = data.get('items', [])
    total_belanja = sum(float(item['price']) for item in items)  # Menghitung total belanja

    # Menghitung diskon berdasarkan total belanja
    discount = 0
    if total_belanja >= 1200000:
        discount = 0.20
    elif total_belanja >= 900000:
        discount = 0.15
    elif total_belanja >= 500000:
        discount = 0.10

    total_belanja -= total_belanja * discount  # Mengurangi total belanja dengan diskon

    # Menentukan voucher jika memenuhi syarat
    voucher_code = None
    voucher_nominal = 0
    if total_belanja >= 900000:
        voucher_code = generate_voucher_code()
        voucher_nominal = 150000
    elif total_belanja >= 500000:
        voucher_code = generate_voucher_code()
        voucher_nominal = 100000
    elif total_belanja >= 300000:
        voucher_code = generate_voucher_code()
        voucher_nominal = 50000

    # Menghubungkan ke database
    db_connection = connect_to_database()
    if db_connection:
        cursor = db_connection.cursor()
        transaction_id = get_next_transaction_id(db_connection)

        # Menyimpan transaksi ke dalam tabel 'transactions'
        query = "INSERT INTO transactions (transaction_id, total_amount, transaction_date, voucher_code, voucher_nominal) VALUES (%s, %s, %s, %s, %s)"
        data = (transaction_id, total_belanja, datetime.now(), voucher_code, voucher_nominal)
        cursor.execute(query, data)

        # Menyimpan item transaksi ke dalam tabel 'transaction_items'
        for item in items:
            query = "INSERT INTO transaction_items (transaction_id, item_name, item_price) VALUES (%s, %s, %s)"
            data = (transaction_id, item['name'], item['price'])
            cursor.execute(query, data)
        db_connection.commit()

        # Menyimpan voucher ke dalam tabel 'vouchers' jika ada
        if voucher_code:
            query = "INSERT INTO vouchers (voucher_code, nominal) VALUES (%s, %s)"
            data = (voucher_code, voucher_nominal)
            cursor.execute(query, data)
            db_connection.commit()

        cursor.close()
        db_connection.close()

    # Menyusun respons JSON
    response = {
        'total_belanja': total_belanja,
        'voucher_code': voucher_code,
        'voucher_nominal': voucher_nominal
    }

    return jsonify(response)

# Route untuk halaman voucher
@app.route('/voucher')
def voucher():
    return render_template('voucher.html')

# Route untuk menerapkan voucher
@app.route('/apply_voucher', methods=['POST'])
def apply_voucher():
    data = request.get_json()
    voucher_code = data.get('voucher_code')
    total_belanja = data.get('total_belanja')

    db_connection = connect_to_database()
    if db_connection:
        cursor = db_connection.cursor()
        query = "SELECT nominal FROM vouchers WHERE voucher_code = %s AND is_used = FALSE"
        cursor.execute(query, (voucher_code,))
        result = cursor.fetchone()

        if result:
            nominal = result[0]
            new_total = total_belanja - nominal
            query = "UPDATE vouchers SET is_used = TRUE WHERE voucher_code = %s"
            cursor.execute(query, (voucher_code,))
            query = "UPDATE transactions SET total_amount = %s WHERE voucher_code = %s"
            cursor.execute(query, (new_total, voucher_code))
            db_connection.commit()
            cursor.close()
            db_connection.close()
            return jsonify({'success': True, 'nominal': nominal, 'new_total': new_total})
        else:
            cursor.close()
            db_connection.close()
            return jsonify({'success': False, 'message': 'Voucher tidak valid atau sudah digunakan'})

    return jsonify({'success': False, 'message': 'Kesalahan database'})

# Route untuk halaman riwayat transaksi
@app.route('/history')
def history():
    db_connection = connect_to_database()
    if db_connection:
        cursor = db_connection.cursor(dictionary=True)
        query = """
            SELECT t.transaction_id, 
                   t.total_amount - t.voucher_nominal AS final_amount, 
                   t.transaction_date, 
                   t.voucher_code, 
                   t.voucher_nominal
            FROM transactions t
            ORDER BY t.transaction_date DESC
        """
        cursor.execute(query)
        transactions = cursor.fetchall()
        cursor.close()
        db_connection.close()

        return render_template('history.html', transactions=transactions)
    return "Kesalahan menghubungkan ke database"

# Fungsi untuk menghasilkan kode voucher acak
def generate_voucher_code(length=8):
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

# Fungsi untuk mendapatkan ID transaksi berikutnya
def get_next_transaction_id(db_connection):
    cursor = db_connection.cursor()
    query = "SELECT MAX(transaction_id) FROM transactions"
    cursor.execute(query)
    result = cursor.fetchone()
    last_transaction_id = result[0] if result[0] is not None else 0
    next_transaction_id = last_transaction_id + 1
    cursor.close()
    return next_transaction_id

if __name__ == '__main__':
    app.run(debug=True)
