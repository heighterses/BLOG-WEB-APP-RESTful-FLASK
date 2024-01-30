from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from forms import Create_Post, User_Form
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

# ------------------------------------------------------------------------


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

Bootstrap5(app)
ckeditor = CKEditor(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class User(UserMixin, db.Model):
    id = db.Coloumn(db.Integer, primary_key=True, nullable=False)
    name = db.Coloumn(db.String, primary_key=False, nullable=False)
    email = db.Coloumn(db.String, primary_key=False, nullable=False)
    password = db.Coloumn(db.String, primary_key=True, nullable=False)


with app.app_context():
    db.create_all()


# Class for make new Blog Post by WTF
class Make_New_Post(FlaskForm):
    blog_post_title = StringField('Blog Post Title', validators=[DataRequired()])
    blog_subtitle = StringField('Blog Subtitle', validators=[DataRequired()])
    author_name = StringField('Author Name', validators=[DataRequired()])
    blog_img_url = StringField('Blog Image URL', validators=[DataRequired(), URL()])

    # ADDING CKEDITOR FOR MAKING A BLOG CONTENT EDITOR
    blog_content = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit Post')


@app.route('/')
def get_all_posts():
    all = BlogPost.query.all()
    posts = []

    for post in all:
        posts_in_dict = {"id": post.id,
                         "title": post.title,
                         "subtitle": post.subtitle,
                         "date": post.date,
                         "body": post.body,
                         "author": post.author,
                         "img_url": post.img_url}

        posts.append(posts_in_dict)

    return render_template("index.html", all_posts=posts)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route('/add_new_post', methods=["POST", "GET"])
def add_new_blog_post():
    form = Make_New_Post()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.blog_post_title.data,
            subtitle=form.blog_subtitle.data,
            body=form.blog_content.data,
            img_url=form.blog_img_url.data,
            author=form.author_name.data,
            date=date.today().strftime("%B %d, %Y")

        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form)


@app.route('/edit-post/<int:post_id>', methods=["POST", "GET"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)

    # Pass the existing post data to the form
    edit_form = Make_New_Post(
        blog_post_title=post.title,
        blog_subtitle=post.subtitle,
        blog_content=post.body,
        blog_img_url=post.img_url,
        author_name=post.author
    )

    if edit_form.validate_on_submit():
        # Update the post details in the database
        post.title = edit_form.blog_post_title.data
        post.subtitle = edit_form.blog_subtitle.data
        post.body = edit_form.blog_content.data
        post.img_url = edit_form.blog_img_url.data
        post.author = edit_form.author_name.data
        post.date = date.today().strftime("%B %d, %Y")

        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route('/delete-post/<int:post_id>', methods=["GET", "POST"])
def delete_the_post(post_id):
    post_to_delete = BlogPost.query.filter_by(id=post_id).first()
    if post_to_delete:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    else:
        print("Post not Found!!")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
