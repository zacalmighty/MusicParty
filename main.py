import pafy
import vlc
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import time
import threading

Instance = vlc.Instance()
player = Instance.media_player_new()
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app)


class MusicParty:
    def __init__(self):
        self.current_song = ""
        self.next_song = ""
        self.suggested_songs = []       # List of songs suggested by party member
        self.party_members = []         # List of party members
        self.party_code = ""            # Party Connect Code

    # Song
    def get_songs(self):
        return self.suggested_songs

    def get_current_song(self):
        return self.current_song

    def get_next_song(self):
        return self.next_song

    def clear_songs(self):
        self.suggested_songs.clear()

    def add_song(self, **new_song_):
        new_song = {}
        try:
            new_song["song_link"] = new_song_["song_link"]
        except KeyError:
            new_song["song_link"] = ""
        new_song["votes"] = 0
        existing_song = False
        for song in self.suggested_songs:
            if song["song_link"] == new_song_["song_link"]:
                print("Error: Song is already in queue")
                existing_song = True
                break
        if existing_song is False:
            self.suggested_songs.append(new_song)

    def bump_song(self, song_number):
        if song_number != 1:
            self.suggested_songs[song_number - 1], self.suggested_songs[song_number - 2] \
                = self.suggested_songs[song_number - 2], self.suggested_songs[song_number - 1]

    def vote_song(self, song_number):
        self.suggested_songs[int(song_number) - 1]["votes"] += 1

    def unvote_song(self, song_number):
        self.suggested_songs[int(song_number) - 1]["votes"] -= 1
        if(self.suggested_songs[int(song_number) - 1]["votes"] < 0):
            self.suggested_songs[int(song_number) - 1]["votes"] = 0

    # Party
    def get_party_members(self):
        return self.party_members

    def get_party_code(self):
        return self.party_code

if __name__ == '__main__':
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000}).start()

    MusicParty1 = MusicParty()
    MusicParty1.add_song(song_name="Remember The Time", song_link="https://www.youtube.com/watch?v=qM19eRgOK1Q")

    def refresh_title_names():
        while True:
            for x in range(len(MusicParty1.suggested_songs)):
                title = pafy.new(MusicParty1.suggested_songs[x]["song_link"]).title
                MusicParty1.suggested_songs[x]["song_name"] = title
                if x == 0:
                    MusicParty1.current_song = title
                elif x == 1:
                    MusicParty1.next_song = title
            time.sleep(10)
    threading.Thread(target=refresh_title_names).start()

    @app.route("/get_songs", methods=["GET"])
    def get_songs():
        return jsonify(MusicParty1.get_songs())

    @app.route("/get_current_song", methods=["GET"])
    def get_current_song():
        return jsonify({"current_song": MusicParty1.current_song})

    @app.route("/get_next_song", methods=["GET"])
    def get_next_song():
        return jsonify({"next_song": MusicParty1.next_song})

    @app.route("/add_song", methods=["PUT"])
    def add_song():
        data = request.form.to_dict(flat=False)
        try:
            if(data["song_link"][0].strip() == ""):
                return abort(404, description="No Song Link Requested")
            song_link = data["song_link"][0]
            MusicParty1.add_song(song_link=song_link)
            return jsonify(["SUCCESSFUL ADD"])
        except KeyError:
            return abort(404, description="No Song Link Requested")

    @app.route("/vote_song", methods=["PUT"])
    def vote():
        data = request.form.to_dict(flat=False)
        try:
            if(data["song_number"][0].strip() == ""):
                return abort(404, description="No Song Number")
            song_number = data["song_number"][0]
            try:
                if(int(song_number) == 0):
                    raise IndexError
                MusicParty1.vote_song(song_number)
            except IndexError:
                return abort(400, description="Invalid Song Number")
            return jsonify(["SUCCESSFUL VOTE"])
        except KeyError:
            return abort(404, description="No Song Number")
        pass

    @app.route("/unvote_song", methods=["PUT"])
    def unvote():
        data = request.form.to_dict(flat=False)
        try:
            if (data["song_number"][0].strip() == ""):
                return abort(404, description="No Song Number")
            song_number = data["song_number"][0]
            try:
                if (int(song_number) == 0):
                    raise IndexError
                MusicParty1.unvote_song(song_number)
            except IndexError:
                return abort(400, description="Invalid Song Number")
            return jsonify(["SUCCESSFUL VOTE"])
        except KeyError:
            return abort(404, description="No Song Number")
        pass

    @app.route("/play", methods=["PUT"])
    def play():
        player.play()
        return jsonify("SUCCESSFUL PLAY")

    @app.route("/pause", methods=["PUT"])
    def pause():
        player.pause()
        return jsonify("SUCCESSFUL PAUSE")

    @app.route("/stop", methods=["PUT"])
    def stop():
        player.stop()
        return jsonify("SUCCESSFUL STOP")

    while True:
        try:
            audio = pafy.new(MusicParty1.suggested_songs[0]["song_link"])
            best = audio.getbestaudio()
            playurl = best.url

            Media = Instance.media_new(playurl)
            Media.get_mrl()
            player.set_media(Media)
            player.play()
            time.sleep(2)
            while True:
                if str(player.get_state()) not in ["State.Playing", "State.Paused", "State.Stopped"]:
                    break
            MusicParty1.suggested_songs.remove(MusicParty1.suggested_songs[0])
        except IndexError:
            pass
        except ImportError:
            pass
