from tornado.ioloop import IOLoop
import tornado.web as web
import tornado.iostream as iostream
import audioproc, ffmpeg, shoutcast
import threading

client_connections = set([])

def push(buf):
    "Send buf to all connected clients"
    print len(buf)
    for conn in client_connections:
        conn.write(buf)
        conn.flush()

def generate_stream():
    "Returns a pipe of aac audio for our stream"
    encoder_in, encoder_out = ffmpeg.audio_writer(None)
    def background():
        urls = list(shoutcast.n_stream_urls(20))
        streams = shoutcast.numpy_streams(urls, sample_duration=0.125)
        ffmpeg.copy_to(audioproc.merge_streams(streams), encoder_in)
    thread = threading.Thread(target=background)
    thread.daemon = True
    thread.start()
    return encoder_out

def broadcast_pipe(pipe, callback):
    "Streams the contents of the given pipe to all clients"
    instream = iostream.PipeIOStream(pipe.fileno())
    instream.read_until_close(callback=callback, streaming_callback=push)

class StreamHandler(web.RequestHandler):

    @web.asynchronous
    def get(self):
        self.set_status(200)
        self.set_header('Content-Type', 'audio/mpeg')
        self.flush()
        print 'connect'
        client_connections.add(self)

    def on_connection_close(self):
        print 'disconnect'
        client_connections.remove(self)


app = web.Application([
    ('/stream.mp3', StreamHandler)
])

if __name__ == '__main__':
    import sys
    def die(_):
        sys.exit(1)
    broadcast_pipe(generate_stream(), die)
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 7878
    app.listen(port)
    IOLoop.current().start()
