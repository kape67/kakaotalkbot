import os
import threading
import requests
from google import genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Gemini API 설정
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"API 키 설정 중 오류 발생: {e}")
    client = None

def get_gemini_response(prompt):
    """Gemini API 호출 함수"""
    if not client:
        return "Gemini 클라이언트가 초기화되지 않았습니다."
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini API 호출 오류: {type(e).__name__} - {e}")
        return "죄송합니다, 지금은 답변을 생성할 수 없어요."

def send_callback_response(callback_url, response_text):
    """콜백 URL로 최종 응답을 전송하는 함수"""
    callback_data = {
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
    
    try:
        response = requests.post(callback_url, json=callback_data, timeout=10)
        print(f"콜백 전송 성공: {response.status_code}")
    except Exception as e:
        print(f"콜백 전송 실패: {e}")

def process_gemini_request(user_message, callback_url):
    """백그라운드에서 Gemini API를 호출하고 콜백으로 응답을 보내는 함수"""
    # 프롬프트 생성
    if "미주" in user_message:
        prompt = "현재 미국 주식 시장(미주) 개장 여부와 주요 지수(다우, 나스닥, S&P 500) 현황을 간략하게 요약해줘."
    elif "국장" in user_message or "국내증시" in user_message:
        prompt = "현재 한국 주식 시장(국장) 개장 여부와 코스피, 코스닥 지수 현황을 간략하게 요약해줘."
    else:
        prompt = user_message
    
    # Gemini API 호출
    response_text = get_gemini_response(prompt)
    
    # 콜백으로 최종 응답 전송
    send_callback_response(callback_url, response_text)

@app.route('/skill', methods=['POST'])
def skill_endpoint():
    req_json = request.get_json()
    
    print("="*20, "Request JSON", "="*20)
    print(req_json)
    
    user_message = req_json['userRequest']['utterance']
    
    # 콜백 URL 확인
    callback_url = req_json.get('userRequest', {}).get('callbackUrl')
    
    if callback_url:
        # 콜백이 가능한 경우 - 백그라운드에서 처리
        # 별도 스레드에서 Gemini API 호출 시작
        threading.Thread(
            target=process_gemini_request,
            args=(user_message, callback_url)
        ).start()
        
        # 즉시 임시 응답 반환
        response_text = "🔍 정보를 찾고 있습니다. 잠시만 기다려주세요..."
        
    else:
        # 콜백이 불가능한 경우 - 동기 처리 (기존 방식)
        if "미주" in user_message:
            prompt = "현재 미국 주식 시장(미주) 개장 여부와 주요 지수(다우, 나스닥, S&P 500) 현황을 간략하게 요약해줘."
            response_text = get_gemini_response(prompt)
        elif "국장" in user_message or "국내증시" in user_message:
            prompt = "현재 한국 주식 시장(국장) 개장 여부와 코스피, 코스닥 지수 현황을 간략하게 요약해줘."
            response_text = get_gemini_response(prompt)
        else:
            response_text = get_gemini_response(user_message)

    # 응답 반환
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