import streamlit as st
import spotipy


def render_player(sp: spotipy.Spotify):
    st.title("Player")

    # Device selector
    try:
        devices = sp.devices().get("devices", [])
    except Exception as e:
        st.error(f"Failed to fetch devices: {e}")
        devices = []

    if devices:
        device_names = [d["name"] for d in devices]
        active_idx = next((i for i, d in enumerate(devices) if d["is_active"]), 0)
        selected = st.selectbox(
            "Playback device", device_names, index=active_idx, key="device_select"
        )
        selected_device = devices[device_names.index(selected)]

        if not selected_device["is_active"]:
            try:
                sp.transfer_playback(selected_device["id"], force_play=False)
            except Exception as e:
                st.error(f"Failed to transfer playback: {e}")
    else:
        st.warning("No active Spotify devices found. Open Spotify on a device first.")

    st.divider()

    @st.fragment(run_every=5)
    def now_playing():
        try:
            playback = sp.current_playback()
        except Exception as e:
            st.error(f"Failed to get playback state: {e}")
            return

        if not playback or not playback.get("item"):
            st.info("Nothing is currently playing.")
            return

        track = playback["item"]
        is_playing = playback["is_playing"]
        progress = playback.get("progress_ms", 0)
        duration = track.get("duration_ms", 1)
        shuffle = playback.get("shuffle_state", False)
        repeat = playback.get("repeat_state", "off")
        volume = playback.get("device", {}).get("volume_percent", 50)

        img = track["album"]["images"][0]["url"] if track["album"]["images"] else ""
        artist_names = ", ".join(a["name"] for a in track["artists"])
        album_name = track["album"]["name"]
        
        st.html(f"""
        <div class="np-card" style="margin-bottom: 20px;">
            <img src="{img}" class="np-art" alt="{track['name']}">
            <div class="np-info">
                <div class="np-title">{track['name']}</div>
                <div class="np-artist">{artist_names}</div>
                <div class="np-album">{album_name}</div>
            </div>
        </div>
        """)
        
        st.progress(progress / duration)
        mins_progress = f"{progress // 60000}:{(progress // 1000) % 60:02d}"
        mins_total = f"{duration // 60000}:{(duration // 1000) % 60:02d}"
        st.caption(f"{mins_progress} / {mins_total}")

        st.write("")
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            if st.button("⏮ Prev", key="prev", use_container_width=True):
                try:
                    sp.previous_track()
                except Exception as e:
                    st.error(str(e))
        with c2:
            label = "⏸ Pause" if is_playing else "▶ Play"
            if st.button(label, key="play_pause", use_container_width=True):
                try:
                    if is_playing:
                        sp.pause_playback()
                    else:
                        sp.start_playback()
                except Exception as e:
                    st.error(str(e))
        with c3:
            if st.button("⏭ Next", key="next", use_container_width=True):
                try:
                    sp.next_track()
                except Exception as e:
                    st.error(str(e))
        with c4:
            shuffle_label = "🔀 On" if shuffle else "🔀 Off"
            if st.button(shuffle_label, key="shuffle", use_container_width=True):
                try:
                    sp.shuffle(not shuffle)
                except Exception as e:
                    st.error(str(e))
        with c5:
            repeat_states = ["off", "context", "track"]
            next_repeat = repeat_states[
                (repeat_states.index(repeat) + 1) % len(repeat_states)
            ]
            repeat_labels = {"off": "🔁 Off", "context": "🔁 All", "track": "🔂 One"}
            if st.button(repeat_labels[repeat], key="repeat", use_container_width=True):
                try:
                    sp.repeat(next_repeat)
                except Exception as e:
                    st.error(str(e))

        new_vol = st.slider("Volume", 0, 100, volume, key="volume")
        if new_vol != volume:
            try:
                sp.volume(new_vol)
            except Exception as e:
                st.error(str(e))

    now_playing()
