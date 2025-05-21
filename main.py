from flask import Flask, render_template, request, redirect, url_for, session
import json
from random import randint

app = Flask(__name__)
app.secret_key = '1234'

# Загрузка данных о ноутбуках из JSON файла
with open('laptops.json', 'r', encoding='utf-8') as f:
    laptops = json.load(f)


@app.route('/')
def index():
    return render_template('index.html', laptops=laptops)


@app.route('/product/<int:laptop_id>')
def product(laptop_id):
    laptop = next((item for item in laptops if item['id'] == laptop_id), None)
    if laptop:
        return render_template('product.html', laptop=laptop)
    return redirect(url_for('index'))


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    laptop_id = int(request.form.get('laptop_id'))
    quantity = int(request.form.get('quantity', 1))

    # Проверяем, есть ли уже такой ноутбук в корзине
    found = False
    for item in session['cart']:
        if item['id'] == laptop_id:
            item['quantity'] += quantity
            found = True
            break

    if not found:
        laptop = next((item for item in laptops if item['id'] == laptop_id), None)
        if laptop:
            cart_item = {
                'id': laptop['id'],
                'name': laptop['name'],
                'price': laptop['price'],
                'quantity': quantity,
                'image': laptop['image']
            }
            session['cart'].append(cart_item)

    session.modified = True
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/remove_from_cart/<int:laptop_id>')
def remove_from_cart(laptop_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != laptop_id]
        session.modified = True
    return redirect(url_for('cart'))


@app.route('/checkout')
def checkout():
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)


@app.route('/process_order', methods=['POST'])
def process_order():
    # Здесь логика обработки заказа
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    address = request.form["address"]
    payment = request.form["payment"]
    number = randint(0, 9_999_999)
    ip = request.remote_addr
    bd = open("clients.txt", "a")
    bd.write(f"'{name}', '{email}', '{phone}', '{address}', '{payment}', '{number}', '{ip}' \n")
    bd.close()
    # Очищаем корзину после оформления заказа
    session.pop('cart', None)
    return render_template('order_success.html', order_number=number)


if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")
