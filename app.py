from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config, IS_PROD
from extensions import csrf, db, login_manager
from utils import money


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    if IS_PROD and app.config["SECRET_KEY"] == "dev-secret-change-me":
        raise RuntimeError("Set a strong SECRET_KEY environment variable in production.")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."

    from models import User, ShoppingTrip

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/"):
            return jsonify(error="Please log in first."), 401
        flash("Please log in to continue.", "info")
        return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))

    from routes.auth import bp as auth_bp
    from routes.dashboard import bp as dashboard_bp
    from routes.trips import bp as trips_bp
    from routes.expenses import bp as expenses_bp
    from routes.pantry import bp as pantry_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(pantry_bp)

    app.jinja_env.filters["money"] = money

    @app.context_processor
    def inject_global_data():
        active_trip = None
        if current_user.is_authenticated:
            active_trip = ShoppingTrip.query.filter_by(
                user_id=current_user.id,
                status="active"
            ).order_by(ShoppingTrip.created_at.desc()).first()
        return {"current_active_trip": active_trip}

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        if request.path.startswith("/api/"):
            return jsonify(error="Session expired. Please refresh the page."), 400
        flash("Your session expired. Please try again.", "error")
        return redirect(request.referrer or url_for("dashboard.home"))

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def too_large(e):
        flash("That file is too large (max 5 MB).", "error")
        return redirect(request.referrer or url_for("dashboard.home"))

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    with app.app_context():
        db.create_all()
        seed_categories()

    return app


def seed_categories():
    from models import Category, DEFAULT_CATEGORIES
    if Category.query.count() == 0:
        for name, icon in DEFAULT_CATEGORIES:
            db.session.add(Category(name=name, icon=icon))
        db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=not IS_PROD, load_dotenv=False)
