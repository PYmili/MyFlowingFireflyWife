import os.path

from PySide6.QtCore import QThread, Signal
from flask import Flask, render_template, send_from_directory, abort


class FlaskThread(QThread):
    started = Signal()

    def __init__(self, port=8080):
        super().__init__()
        self.port = port
        self.flask_app = Flask(
            __name__,
            template_folder='templates',
            static_folder='static'
        )

        @self.flask_app.route('/firefly')
        def firefly():
            return render_template('firefly.html')

        @self.flask_app.route('/chun')
        def chun():
            return render_template('chun.html')

        @self.flask_app.route('/<path:subpath>')
        def live2d_model(subpath):
            # 尝试从静态目录中发送请求的文件
            try:
                return send_from_directory(self.flask_app.static_folder, subpath)
            except FileNotFoundError:
                # 如果文件不存在，返回 404 错误
                abort(404)

    def run(self):
        # host参数使用'0.0.0.0'允许服务器接受所有网络接口的连接
        self.flask_app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        self.started.emit()
