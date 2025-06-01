import secrets
import os
from PIL import Image
from flask import jsonify, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
# Import necessary modules and classes
from shopwave import app, db, bcrypt
from shopwave.forms import RegisterForm, LoginForm, UpdateAccountForm, ProductForm, EditProductForm
from shopwave.models import User, Product


@app.errorhandler(404)
def not_found(error: Exception):
    """Custom 404 error handler."""
    app.logger.error(f"404 error: {error}")
    return jsonify({"error": "Not Found"}), 404

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Route to get a specific product by ID."""
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product, title=product.name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', title="Login", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if form.admin_key.data == 'admin123':  # Example admin key, replace with a secure method
            is_admin = True
        else:
            is_admin = False
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=is_admin) # type: ignore
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
        # Here you would typically save the user's data
    return render_template('register.html', title="Register", form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


def save_picture(form_picture):
    """Function to save the profile picture."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
    

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            # Handle profile picture upload
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        # Update user information
        current_user.username = form.username.data
        current_user.email = form.email.data
        if not bcrypt.check_password_hash(current_user.password, form.password.data):
            flash('Invalid current password. Please try again.', 'danger')
            return redirect(url_for('account'))
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        # No need to set password field, it should not be pre-filled for security reasons
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title="Account", image_file=image_file, user=current_user, form=form)


@app.route('/seller')
def seller_dashboard():
    """Seller dashboard route."""
    if not current_user.is_admin:
        flash('You do not have permission to access seller dashboard.', 'danger')
        return redirect(url_for('index'))
    return render_template('seller.html', title="Seller Dashboard", user=current_user, products=Product.query.all())

def save_product_images(images):
    """Function to save product images."""
    saved_images = []
    for image in images:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(image.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/product_images', picture_fn)

        output_size = (300, 300)  # Resize to a standard size
        i = Image.open(image)
        i.thumbnail(output_size)
        i.save(picture_path)

        saved_images.append(picture_fn)
    return saved_images

@app.route('/seller/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        flash('You do not have permission to add products.', 'danger')
        return redirect(url_for('index'))
    form = ProductForm()
    if form.validate_on_submit():
        valid_images = [img for img in form.images.data if getattr(img, "filename", None)]
        valid_images = [img for img in valid_images if img.filename]
        images = save_product_images(valid_images) if valid_images else []
        product = Product(
            name=form.name.data,
            price=float(form.price.data),
            Images=images,
            description=form.description.data,
            detail=form.detail.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Your product has been added!', 'success')
        return redirect(url_for('seller_dashboard'))
    return render_template('add_product.html', title="Add Product", user=current_user, form=form)

@app.route('/seller/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Route to edit an existing product."""
    product = Product.query.get_or_404(product_id)
    if not current_user.is_admin:
        flash('You do not have permission to edit products.', 'danger')
        return redirect(url_for('index'))
    form = EditProductForm(obj=product)
    if form.validate_on_submit():
        valid_images = [img for img in form.images.data if getattr(img, "filename", None)]
        valid_images = [img for img in valid_images if img.filename]
        if valid_images:
            images = save_product_images(valid_images)
            product.Images = images
        product.name = form.name.data
        product.price = float(form.price.data)
        product.description = form.description.data
        product.detail = form.detail.data
        db.session.commit()
        flash('Your product has been updated!', 'success')
        return redirect(url_for('seller_dashboard'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = int(product.price)
        form.description.data = product.description
        form.detail.data = product.detail
    return render_template('edit_product.html', title="Edit Product", user=current_user, form=form, product=product)

@app.route('/seller/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Route to delete a product."""
    product = Product.query.get_or_404(product_id)
    if not current_user.is_admin:
        flash('You do not have permission to delete products.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('seller_dashboard'))


@app.route('/')
def index():
    product_list = Product.query.all()
    if not product_list:
        flash('No products available at the moment.', 'info')
        return render_template('products.html', products=[], title="Product List")
    return render_template('products.html', products=product_list, title="Product List")