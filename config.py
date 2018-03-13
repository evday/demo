import os
# 返回脚本的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    """配置文件"""

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    ARTICLES_PER_PAGE = 10
    COMMENTS_PER_PAGE = 6
    SECRET_KEY = 'secret key to protect from csrf'
    WTF_CSRF_SECRET_KEY = 'random key for form'

    @staticmethod
    def init_app(app):
        pass

