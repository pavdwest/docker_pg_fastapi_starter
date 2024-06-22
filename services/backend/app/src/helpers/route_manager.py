def add_routes(app):
    from src.modules.home.routes import router as home_router
    app.include_router(home_router)
