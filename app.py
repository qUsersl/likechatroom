from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, stream_with_context
from flask_socketio import SocketIO, emit, join_room, leave_room
import config
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Store connected users: sid -> nickname
connected_users = {}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html', servers=config.SERVERS)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    nickname = data.get('nickname')
    password = data.get('password')
    server = data.get('server')
    
    if not nickname:
        return jsonify({'success': False, 'message': '请输入昵称'})
    if password != '123456':
        return jsonify({'success': False, 'message': '密码错误'})
    if not server:
        return jsonify({'success': False, 'message': '请选择服务器'})
        
    # Store in session
    session['nickname'] = nickname
    session['server'] = server
    
    return jsonify({'success': True})

@app.route('/chat')
def chat():
    if 'nickname' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', nickname=session['nickname'])

@app.route('/api/searchImage')
def search_image():
    # Mock API for the image placeholders in the design
    # Using ui-avatars for simplicity
    query = request.args.get('query', 'User')
    # Extract name from query if possible, or just use the query
    name = query.split(' ')[0] if ' ' in query else query
    return redirect(f"https://ui-avatars.com/api/?name={name}&background=random&color=fff")

@app.route('/api/ai_chat')
def ai_chat():
    prompt = request.args.get('prompt', '')
    if not prompt:
        return "No prompt provided", 400

    def generate():
        client = OpenAI(
            api_key=config.AI_API_KEY,
            base_url=config.AI_BASE_URL
        )
        
        try:
            response = client.chat.completions.create(
                model=config.AI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "你是一个乐于助人的AI助手成小理。"},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    # Replace newlines with a special marker or handle them on frontend
                    # SSE expects data: ...
                    # We will just send the content directly. 
                    # Since content can contain newlines, we need to be careful.
                    # Standard SSE: data: <content>\n\n
                    # If content has \n, we might need to split. 
                    # For simplicity, we can JSON encode the chunk.
                    import json
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

def broadcast_user_list():
    # Get unique users list
    unique_users = list(set(connected_users.values()))
    socketio.emit('update_user_list', {
        'users': unique_users,
        'count': len(unique_users)
    }, room='general')

@socketio.on('connect')
def on_connect():
    if 'nickname' in session:
        nickname = session['nickname']
        join_room('general')
        connected_users[request.sid] = nickname
        emit('system_message', {'msg': f"{nickname} 进入了房间"}, room='general')
        broadcast_user_list()

@socketio.on('disconnect')
def on_disconnect():
    if request.sid in connected_users:
        nickname = connected_users[request.sid]
        del connected_users[request.sid]
        leave_room('general')
        emit('system_message', {'msg': f"{nickname} 离开了房间"}, room='general')
        broadcast_user_list()

@socketio.on('send_message')
def handle_message(data):
    if 'nickname' in session:
        msg = data['msg']
        msg_type = 'text'
        
        # Check for @电影 command
        if msg.startswith('@电影 '):
            url = msg.replace('@电影 ', '', 1).strip()
            if url:
                msg_type = 'video'
                # Construct the parsing URL
                msg = f"https://jx.2s0.cn/player/?url={url}"
        
        current_time = datetime.now().strftime('%H:%M')
        emit('receive_message', {
            'nickname': session['nickname'],
            'msg': msg,
            'type': msg_type,
            'time': current_time
        }, room='general')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
