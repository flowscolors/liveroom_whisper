import gradio as gr

# HTML 内容，包括引入 hls.js 库和设置 video 标签
html_content = """
<div>
    <video id="video" controls></video>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <script>
        var video = document.getElementById('video');
        var videoSrc = 'http://pull-spe-l3.douyinliving.com/fantasy/stream-692877026608284342_thirdor4.m3u8?auth_key=1734846555-0-0-4cf4396427c42d5e629073b0208f6076\\u0026major_anchor_level=vip';
        if (Hls.isSupported()) {
            var hls = new Hls();
            hls.loadSource(videoSrc);
            hls.attachMedia(video);
            hls.on(Hls.Events.MANIFEST_PARSED, function() {
                video.play();
            });
        }
        // HLS.js is not supported on platforms that do not have Media Source Extensions (MSE) enabled.
        // When the browser has built-in HLS support (check using `canPlayType`), we can provide the HLS manifest (i.e. .m3u8 URL) directly to the video element through the `src` attribute.
        else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = videoSrc;
            video.addEventListener('loadedmetadata', function() {
                video.play();
            });
        }
    </script>
</div>
"""

def app():
    with gr.Blocks() as demo:
        gr.Markdown("### 视频播放示例")
        gr.HTML(html_content)  # 使用 HTML 组件
        gr.Markdown("请观看上面的视频流。")

    return demo

# 运行 Gradio 应用
if __name__ == "__main__":
    app().launch()