from toc import setup as toc_setup
from ctxhelp import setup as ctxhelp_setup


def setup(app):
    app.add_config_value('eclipse_base_path', 'build/html', 'html')

    toc_setup(app)
    ctxhelp_setup(app)
