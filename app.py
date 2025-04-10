from flask import Flask

app = Flask(__name__)
# 위의 name은 모듈이라고 부름

# /자리는 주소를 넣는 자리


# http://127.0.0.1:5000 은 우리의 주소
@app.route("/")
def index():
    return "hello_world!"


# http://127.0.0.1:5000/hello 에 대응된다
# 주소 뒤 / 이후의 주소와 라우드 뒤의 주소가 대응되면 해당 함수로 이동한다.
@app.route("/excel")
def hello_world():
    return "액셀을 업로드 해주세요"


# 동적라우팅
# 주소의 어떤 부분을 변수화(<변수명>)
# 변수화된 URL의 한 부분을 파라미터로 받을 수 있음.


@app.route("/user/<user_name>")
def hello_user_name(user_name):
    return "Hello %s" % user_name


# 동적 라우팅을 사용할 때 자료 형태를 정해줄 수 있다.
# 만약 URL을 옳게 입력했음에도 자료 형태가 다르면
# 404 NOT FOUND로 이동한다.


@app.route("/user/by_id/<int:user_id>")
def get_user_by_id(user_id: int):
    return "유저 데이터를 받아왔습니다. %s" % user_id


if __name__ == "__main__":
    app.run()
