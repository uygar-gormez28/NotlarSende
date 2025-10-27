import os
import json
import re
import uuid
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory, abort
from werkzeug.utils import secure_filename


app = Flask(
    __name__,
    static_folder='app/static',
    template_folder='app/templates'
)
app.secret_key = 'gizli-anahtar'

# ---------------- Konfigürasyon ----------------
app.config['UPLOAD_ROOT']      = 'uploads'
app.config['DATABASE_FOLDER']  = 'database'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx'}
ALLOWED_IMAGE_EXT = {'png','jpg','jpeg','gif'}

# Dosya yolları
USERS_FILE     = os.path.join(app.config['DATABASE_FOLDER'], 'kullanicibilgileri.json')
PRODUCTS_FILE  = os.path.join(app.config['DATABASE_FOLDER'], 'urunler.json')
PURCHASES_FILE = os.path.join(app.config['DATABASE_FOLDER'], 'satin_alimlar.json')
CART_FOLDER = os.path.join(app.config['DATABASE_FOLDER'], 'cartfiles')
SUPPORT_FILE = os.path.join(app.config['DATABASE_FOLDER'], 'support_requests.json')

# Klasörleri oluştur
os.makedirs(app.config['DATABASE_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_ROOT'],       exist_ok=True)
os.makedirs(CART_FOLDER, exist_ok=True)


# ---------------- Yardımcı Fonksiyonlar ----------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Kullanıcıları yükle / kaydet ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


# --- Ürünleri yükle / kaydet ---
def load_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


# --- Satın almaları yükle / kaydet (email → [product_id, ...]) ---
def load_purchases():
    if os.path.exists(PURCHASES_FILE):
        with open(PURCHASES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_purchases(purchases):
    with open(PURCHASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(purchases, f, ensure_ascii=False, indent=2)


# --- Sepet yükleme / kaydetme yardımcıları (her kullanıcıya özel .json) ---
def get_cart_path(email):
    filename = f"cart_{email}.json"
    return os.path.join(CART_FOLDER, filename)

def load_cart(email):
    path = get_cart_path(email)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_cart(email, cart):
    path = get_cart_path(email)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cart, f, ensure_ascii=False, indent=2)



def load_support_requests():
    if os.path.exists(SUPPORT_FILE):
        with open(SUPPORT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_support_requests(requests):
    with open(SUPPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)
   

def allowed_image(filename):
    ext = filename.rsplit('.',1)[1].lower()
    return ext in ALLOWED_IMAGE_EXT

# ---------------- Global Context ----------------

@app.context_processor
def inject_user():
    users = load_users()
    user_email = session.get('user_email')
    current_user = users.get(user_email)

    # Sepet sayısını hesapla
    cart_count = 0
    if user_email:
        cart = load_cart(user_email)
        # Toplam adet: quantity’leri topla
        cart_count = sum(item.get('quantity', 1) for item in cart)

    return {
        'current_user': current_user,
        'cart_count': cart_count
    }



# ---------------- Auth (Giriş / Kayıt / Çıkış) ----------------

@app.route('/login', methods=['GET'])
def show_login():
    errors = session.pop('errors', {'login': ''})
    return render_template('login.html', errors=errors, active_form='login')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    users = load_users()
    user = users.get(email)
    if user and user.get('password') == password:
        session['user_email'] = email
        return redirect(url_for('ana_sayfa'))
    session['errors'] = {'login': 'Email ya da şifre hatalı.'}
    return redirect(url_for('show_login'))

@app.route('/register', methods=['GET'])
def show_register():
    errors = session.pop('errors', {'register': ''})
    return render_template('login.html', errors=errors, active_form='register')

@app.route('/register', methods=['POST'])
def register():
    name     = request.form['name']
    email    = request.form['email']
    password = request.form['password']
    role     = request.form['role']
    users    = load_users()
    if email in users:
        session['errors'] = {'register': 'Bu email zaten kayıtlı.'}
        return redirect(url_for('show_register'))
    users[email] = {
        'name': name,
        'email': email,
        'password': password,
        'role': role
    }
    save_users(users)
    return redirect(url_for('show_login'))

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('ana_sayfa'))


# ---------------- Genel Sayfalar ----------------

@app.route('/')
def ana_sayfa():
    products = load_products()
    published = [p for p in products if p.get('published')]
    return render_template('index.html', products=published)

# ---------------- Hesap (Profile) Sayfası ----------------

@app.route('/account', methods=['GET', 'POST'])
def account():
    user_email = session.get('user_email')
    if not user_email:
        flash('Bu sayfayı görüntülemek için lütfen giriş yapın.', 'warning')
        return redirect(url_for('show_login')) # 'show_login' giriş sayfanızın adı

    users = load_users()
    profile = users.get(user_email)

    if not profile:
        session.pop('user_email', None)
        flash('Kullanıcı profili bulunamadı. Lütfen tekrar giriş yapın.', 'danger')
        return redirect(url_for('show_login'))

    profile.setdefault('email', user_email)
    profile.setdefault('name', '')
    profile.setdefault('phone', '')
    # Düz metin şifre alanı için (eğer JSON'da yoksa)
    profile.setdefault('password', '') # Bu, şifrenin gösterilmesi için değil, güncelleme mantığı için

    if request.method == 'POST':
        profile['name'] = request.form.get('name', profile['name']).strip()
        profile['phone'] = request.form.get('phone', profile['phone']).strip()
        
        new_password = request.form.get('password', '').strip()
        if new_password:
            # UYARI: ŞİFRE DÜZ METİN OLARAK KAYDEDİLİYOR! BU GÜVENLİ DEĞİLDİR!
            profile['password'] = new_password
            # Eğer 'password_hash' alanı varsa ve artık kullanılmayacaksa kaldırılabilir.
            # if 'password_hash' in profile:
            #     del profile['password_hash']
        
        users[user_email] = profile
        save_users(users)

        flash('Profiliniz başarıyla güncellendi.', 'success')
        return redirect(url_for('account'))

    all_products = load_products()
    user_purchases_data = load_purchases()
    user_purchased_ids = user_purchases_data.get(user_email, [])
    
    purchased_items_details = []
    if user_purchased_ids and all_products:
        for product in all_products:
            if product.get('id') in user_purchased_ids:
                purchased_items_details.append(product)
    
    return render_template(
        'account.html',
        profile=profile,
        purchased_items=purchased_items_details
    )


# ---------------- Mağaza (Store) ----------------

@app.route('/store')
def store():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('show_login'))
    all_products = load_products()
    user_products = [p for p in all_products if p.get('uploader') == user_email]
    return render_template('store.html', user=load_users()[user_email], user_products=user_products)


# ---------------- Ürün Yükleme & Yayınlama ----------------

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        return 'Dosya bulunamadı veya isim boş.', 400
    if not allowed_file(file.filename):
        return 'Geçersiz dosya türü.', 400

    filename   = secure_filename(file.filename)
    user_email = session.get('user_email')
    user_folder= os.path.join(app.config['UPLOAD_ROOT'], user_email)
    os.makedirs(user_folder, exist_ok=True)
    file.save(os.path.join(user_folder, filename))

    products = load_products()
    products.append({
        'filename': filename,
        'uploader': user_email,
        'published': False,
        'date': datetime.now().strftime('%d %B %Y')
    })
    save_products(products)
    return redirect(url_for('store'))

@app.route('/publish', methods=['POST'])
def publish_product():
    user_email = session.get('user_email')
    form       = request.form
    products   = load_products()

    for p in products:
        if p['filename'] == form['filename'] and p['uploader'] == user_email:
            # 1) Ürün ID'sini oluştur/yükle
            if 'id' not in p:
                p['id'] = f"{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:8]}"

            # 2) Ürün klasörünün yolunu tam olarak bu satırda oluştur
            base_folder    = os.path.join(app.config['UPLOAD_ROOT'], user_email)
            product_folder = os.path.join(base_folder, p['id'])
            os.makedirs(product_folder, exist_ok=True)

            # 3) Formdan gelen resim dosyalarını product_folder içine kaydet
            images = []
            for img in request.files.getlist('images'):
                # resim uzantılarını kontrol etmek için allowed_image() kullanıyoruz
                if img and allowed_image(img.filename):
                    fname = f"{uuid.uuid4().hex}_{secure_filename(img.filename)}"
                    img.save(os.path.join(product_folder, fname))
                    images.append(f"{user_email}/{p['id']}/{fname}")


            p['images'] = images

            # 4) Diğer metadata’yı da güncelle
            p.update({
                'title':       form['title'],
                'university':  form['university'],
                'faculty':     form['faculty'],
                'description': form['description'],
                'price':       form['price'],
                'published':   True
            })
            break

    save_products(products)
    return redirect(url_for('store'))



@app.route('/delete_product', methods=['POST'])
def delete_product():
    user_email = session.get('user_email')
    filename   = request.form['filename']
    # JSON'dan sil
    prods = [p for p in load_products() if not (p['filename']==filename and p['uploader']==user_email)]
    save_products(prods)
    # Dosyayı sil
    try:
        os.remove(os.path.join(app.config['UPLOAD_ROOT'], user_email, filename))
    except FileNotFoundError:
        pass
    return redirect(url_for('store'))


# ---------------- Sepet İşlemleri ----------------

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    user_email = session.get('user_email')
    # 1. Eğer login değilse AJAX isteğine özel 401+JSON dön, normal istekte redirect et
    if not user_email:
        if request.is_json:
            return jsonify({'redirect': url_for('show_login')}), 401
        return redirect(url_for('show_login'))

    prod_id  = request.json.get('product_id')  # JSON göndersin diye
    filename = request.json.get('filename')
    cart     = load_cart(user_email)

    if not any(item['product_id']==prod_id for item in cart):
        cart.append({'product_id': prod_id, 'filename': filename, 'quantity': 1})
        save_cart(user_email, cart)
        # yeni adet
        new_count = sum(item['quantity'] for item in cart)
        if request.is_json:
            return jsonify({
                'success': True,
                'message': '✅ Ürün sepete eklendi!',
                'cart_count': new_count
            })

    # zaten sepette varsa
    if request.is_json:
        return jsonify({
            'success': False,
            'message': '⚠️ Bu ürün zaten sepette.',
            'cart_count': sum(item['quantity'] for item in cart)
        })

    flash('✅ Ürün sepete eklendi!', 'success')
    return redirect(url_for('ana_sayfa'))


@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    user_email= session.get('user_email')
    if not user_email:
        return redirect(url_for('show_login'))
    prod_id   = request.form['product_id']
    cart      = [i for i in load_cart(user_email) if i['product_id']!=prod_id]
    save_cart(user_email, cart)
    return redirect(url_for('cart'))

@app.route('/update-cart-quantity', methods=['POST'])
def update_cart_quantity():
    user_email= session.get('user_email')
    if not user_email:
        return redirect(url_for('show_login'))
    prod_id = request.form['product_id']
    action  = request.form['action']   # "increase" / "decrease"
    cart    = load_cart(user_email)
    for item in cart:
        if item['product_id']==prod_id:
            if action=='increase':
                item['quantity'] += 1
            else:
                item['quantity'] = max(1, item['quantity'] - 1)
            break
    save_cart(user_email, cart)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('show_login'))

    cart_items   = load_cart(user_email)
    products     = load_products()
    sepet        = []
    toplam_tutar = 0

    for ci in cart_items:
        p = next((x for x in products if x.get('id')==ci['product_id']), None)
        if not p: 
            continue
        # Fiyatı tam sayı al
        m = re.search(r'(\d+)', str(p.get('price','0')).replace(',',''))
        price_val = int(m.group(1)) if m else 0
        qty = ci.get('quantity',1)

        p_copy = p.copy()
        p_copy.update({'quantity': qty, 'price_value': price_val})
        sepet.append(p_copy)
        toplam_tutar += price_val * qty

    return render_template('cart.html',
                           sepet=sepet,
                           toplam_tutar=toplam_tutar)


# ---------------- Sepetten Satın Alma ----------------


@app.route('/purchase', methods=['POST'])
def purchase():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('show_login'))

    # Sepeti al
    cart_items = load_cart(user_email)

    # Satın alma kayıtlarını güncelle
    purchases = load_purchases()           # dict: {email: [id1, id2, …]}
    user_pur  = purchases.get(user_email, [])

    for item in cart_items:
        pid = item['product_id']
        if pid not in user_pur:
            user_pur.append(pid)
    purchases[user_email] = user_pur
    save_purchases(purchases)

    # Sepeti temizle
    save_cart(user_email, [])

    # İstersen buraya bir "teşekkür" veya "sipariş onay" sayfası tanımlayabilirsin
    return redirect(url_for('cart'))

# ---------------- Support Sayfası ----------------

@app.route('/support', methods=['GET','POST'])
def support():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('show_login'))

    if request.method == 'POST':
        selected_product = request.form.get('selected_product') or None
        message          = request.form.get('message','').strip()
        if message:
            tickets      = load_support_requests()
            user_tickets = tickets.get(user_email, [])
            user_tickets.append({
                'product_id': selected_product,
                'message':    message,
                'timestamp':  datetime.now(timezone.utc).isoformat()
            })
            tickets[user_email] = user_tickets
            save_support_requests(tickets)

            # → flash mesajını server tarafında atıyoruz
            flash("Talebiniz başarıyla iletildi. En kısa sürede geri dönüş sağlayacağız.", "success")

        return redirect(url_for('support'))

    # GET:
    purchases        = load_purchases().get(user_email, [])
    products_map     = { p['id']: p for p in load_products() if 'id' in p }
    support_requests = load_support_requests().get(user_email, [])

    return render_template(
        'support.html',
        purchases=purchases,
        products_map=products_map,
        support_requests=support_requests
    )
    

@app.route('/support/delete', methods=['POST'])
def delete_support_request():
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('show_login'))

    # Formdan gelen index
    ticket_index = request.form.get('ticket_index')
    if ticket_index is not None:
        tickets = load_support_requests()
        user_tickets = tickets.get(user_email, [])

        try:
            idx = int(ticket_index)
            if 0 <= idx < len(user_tickets):
                user_tickets.pop(idx)
                tickets[user_email] = user_tickets
                save_support_requests(tickets)
        except ValueError:
            pass

    return redirect(url_for('support'))

# ---------------- Satın Alınmış ürünleri indirme Sayfası ----------------

@app.route('/download/<product_id>')
def download_product(product_id):
    user_email = session.get('user_email')
    if not user_email:
        flash('Lütfen önce giriş yapın.', 'warning')
        return redirect(url_for('show_login'))

    # Satın alma kontrolü
    if product_id not in load_purchases().get(user_email, []):
        abort(403)

    # Ürünü bul
    product = next((p for p in load_products() if p.get('id')==product_id), None)
    if not product:
        abort(404)

    uploader    = product['uploader']
    filename    = product['filename']
    user_folder = os.path.join(app.config['UPLOAD_ROOT'], uploader)

    # Burada filename, path olarak veriliyor
    try:
        return send_from_directory(
            user_folder,     # directory
            filename,        # path (dosya adı)
            as_attachment=True
        )
    except FileNotFoundError:
        abort(404)
        

@app.route('/uploads/<path:filepath>')
def uploaded_file(filepath):
    user_email = session.get('user_email')
    if not user_email:
        abort(401)

    parts = filepath.split('/')
    if parts[0] != user_email:
        abort(403)

    full_path = os.path.join(app.config['UPLOAD_ROOT'], filepath)
    if not os.path.exists(full_path):
        abort(404)

    # İşte düzeltme burada:
    return send_from_directory(
        os.path.dirname(full_path),
        os.path.basename(full_path),
        as_attachment=False
    )

        


# ---------------- Uygulamayı Başlat ----------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
