from flask import Flask, request, jsonify

app = Flask(__name__)

# 스킬 서버의 메인 로직이 들어가는 부분
@app.route('/skill', methods=['POST'])
def skill_endpoint():
    # 1. 카카오로부터 받은 요청 데이터(JSON)를 파싱합니다.
    req_json = request.get_json()
    
    # 디버깅을 위해 전체 요청 데이터를 출력해봅니다. (매우 중요!)
    print("="*20, "Request JSON", "="*20)
    print(req_json)
    
    # 2. 사용자가 실제로 보낸 메시지를 추출합니다.
    user_message = req_json['userRequest']['utterance']
    
    # 3. 여기에 핵심 로직을 구현합니다.
    #    지금은 단순히 받은 메시지를 되돌려주는 로직입니다.
    #    - OpenAI GPT API 연동
    #    - 날씨/뉴스 API 호출
    #    - 데이터베이스 조회 등 모든 Python 코드를 여기에!
    response_text = f"당신이 보낸 메시지는 '{user_message}'군요!"

    # 4. 카카오톡이 이해할 수 있는 JSON 형식으로 응답을 구성합니다.
    res_json = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }
    
    return jsonify(res_json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)