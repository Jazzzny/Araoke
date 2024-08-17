from flask import Flask, request, render_template, jsonify
import search_support

app = Flask(__name__)
music_search = search_support.MusicSearch()

@app.route('/')
def search_page():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    results = music_search.search_tracks(request.form['term'])
    return render_template('results.html', results=results)

@app.route('/select', methods=['POST'])
def select():
    selected_track = request.json
    print(selected_track)
    print(music_search.id_to_track_info(selected_track['id']))
    return jsonify({'status': 'success', 'selected_track': selected_track})


if __name__ == "__main__":
    app.run(debug=True)