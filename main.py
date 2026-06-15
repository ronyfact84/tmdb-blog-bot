def trailer_system(title):
    search_url = f"https://www.youtube.com/results?search_query={title}+official+trailer"

    return f"""
    <div style="margin-top:10px;">

    <div onclick="openTrailer()"
    style="
        width:100%;
        height:220px;
        background:#111;
        color:white;
        display:flex;
        align-items:center;
        justify-content:center;
        border-radius:10px;
        cursor:pointer;
        font-size:18px;
        font-weight:bold;">
        ▶ Click to Watch Trailer
    </div>

    <div id="popup" style="
        display:none;
        position:fixed;
        top:0;left:0;
        width:100%;height:100%;
        background:rgba(0,0,0,0.95);
        z-index:9999;
        justify-content:center;
        align-items:center;">

        <div style="width:90%;max-width:900px;position:relative;">

            <iframe width="100%" height="500"
            src="{search_url}"
            style="border:none;background:white;">
            </iframe>

            <button onclick="closeTrailer()"
            style="
                position:absolute;
                top:-20px;
                right:-20px;
                background:white;
                border:none;
                font-size:22px;
                width:40px;
                height:40px;
                border-radius:50%;
                cursor:pointer;">
                ✖
            </button>

        </div>
    </div>

    <script>
    function openTrailer() {{
        document.getElementById("popup").style.display = "flex";
    }}
    function closeTrailer() {{
        document.getElementById("popup").style.display = "none";
    }}
    </script>

    </div>
    """
