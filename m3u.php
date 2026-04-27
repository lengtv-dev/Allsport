
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IPTV เครื่องเล่นเว็บเพจ</title>
<script src="https://ofiii.dpdns.org/hls.min.js"></script>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    background: #0f1115;
    color: #e5e7eb;
    font-family: "Segoe UI", Arial, sans-serif;
}
.header {
    background: #1b1f2a;
    padding: 12px 20px;
    font-size: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}
.header small {
    color: #9ca3af;
    font-size: 12px;
}
.container {
    display: flex;
    height: calc(100vh - 56px);
}
.sidebar {
    width: 360px;
    background: #141824;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #222;
}
.section {
    padding: 10px;
    border-bottom: 1px solid #222;
}
.section-title {
    font-size: 13px;
    margin-bottom: 6px;
    color: #9ca3af;
}
input, select {
    width: 100%;
    padding: 9px 10px;
    background: #1f2433;
    border: 1px solid #2a3145;
    color: #fff;
    border-radius: 6px;
    outline: none;
}
input:focus, select:focus {
    border-color: #3b82f6;
}
button {
    width: 100%;
    margin-top: 6px;
    padding: 9px 10px;
    background: #3b82f6;
    border: none;
    color: #fff;
    cursor: pointer;
    border-radius: 6px;
}
button:hover {
    background: #2563eb;
}
.meta {
    padding: 8px 10px;
    font-size: 12px;
    color: #9ca3af;
    border-bottom: 1px solid #222;
    display: flex;
    justify-content: space-between;
    gap: 8px;
    flex-wrap: wrap;
}
.status {
    padding: 8px 10px;
    font-size: 12px;
    color: #cbd5e1;
    border-bottom: 1px solid #222;
    background: #121621;
    min-height: 34px;
}
.list {
    flex: 1;
    overflow-y: auto;
}
.group {
    border-bottom: 1px solid #1f2432;
}
.group-title {
    position: sticky;
    top: 0;
    z-index: 2;
    background: #171c29;
    color: #93c5fd;
    font-size: 12px;
    padding: 8px 10px;
    border-bottom: 1px solid #222;
}
.item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-bottom: 1px solid #202532;
    cursor: pointer;
    transition: background .15s ease;
}
.item:hover {
    background: #1e2233;
}
.item.active {
    background: #1d4ed8;
}
.logo {
    width: 36px;
    height: 36px;
    border-radius: 6px;
    background: #0b0f18;
    object-fit: cover;
    flex-shrink: 0;
    border: 1px solid #2a3145;
}
.logo-fallback {
    width: 36px;
    height: 36px;
    border-radius: 6px;
    background: #263149;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: #bfdbfe;
    flex-shrink: 0;
}
.item-text {
    min-width: 0;
    flex: 1;
}
.item-name {
    font-size: 14px;
    color: #f8fafc;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.item-sub {
    margin-top: 3px;
    font-size: 12px;
    color: #94a3b8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.empty {
    padding: 20px;
    color: #94a3b8;
    font-size: 13px;
}
.player {
    flex: 1;
    background: #000;
    display: flex;
    flex-direction: column;
}
.player-top {
    padding: 10px 14px;
    background: #111723;
    border-bottom: 1px solid #1f2937;
    font-size: 13px;
    color: #cbd5e1;
}
.player-top strong {
    color: #fff;
}
video {
    width: 100%;
    height: calc(100% - 44px);
    background: #000;
}
@media (max-width: 900px) {
    .container { flex-direction: column; height: auto; }
    .sidebar { width: 100%; height: 50vh; }
    .player { height: 50vh; }
    video { height: calc(100% - 44px); }
}
</style>
</head>
<body>
<div class="header">
    <div>📺 IPTV เครื่องเล่นเว็บเพจ</div>
    <small>การแยกวิเคราะห์การสมัครสมาชิก + การเล่นผ่านพร็อกซี + การค้นหากลุ่ม</small>
</div>

<div class="container">
    <div class="sidebar">
        <div class="section">
            <div class="section-title">📡 ที่อยู่ของแหล่งข้อมูล (การสมัครรับข้อมูล/การเล่น)）</div>
            <select id="subSelect" onchange="document.getElementById('sourceUrl').value = this.value">
                <option value="">-- โปรดเลือกหรือป้อนข้อมูลด้วยตนเอง --</option>
                <option value="https://ufile.eu.org/juli.php">juli</option>
                <option value="https://dl.dropbox.com/scl/fi/e4u8shspjt0ylrb3552dj/dootv.m3u?rlkey=ug92sfb8z9xqd1srefpqan5bh&st=y2zzd2iw&dl=0">tv</option>
                <option value="https://de.ufile.eu.org/ppv_m3u.php">ppv</option>
            </select>
            <input id="sourceUrl" placeholder="https://example.com/iptv.m3u" style="margin-top: 6px;">
            <div style="display: flex; gap: 8px; margin-top: 6px;">
                <button onclick="loadSub()" style="margin-top: 0;">โหลดการสมัครสมาชิก</button>
                <button onclick="playDirect()" style="margin-top: 0; background: #10b981;">เล่นโดยตรง</button>
            </div>
        </div>

        <div class="meta">
            <span id="channelCount">หมายเลขช่อง：0</span>
            <span id="groupCount">จำนวนกลุ่ม：0</span>
        </div>

        <div class="status" id="status">พร้อม</div>

        <div class="list" id="list">
            <div class="empty">โปรดป้อนที่อยู่สำหรับการสมัครสมาชิกของคุณ หรือป้อนลิงก์การเล่นโดยตรง</div>
        </div>
    </div>

    <div class="player">
        <div class="player-top">
            กำลังเล่นอยู่：<strong id="nowPlaying">ไม่ได้เล่น</strong>
        </div>
        <video id="video" controls autoplay></video>
    </div>
</div>

<script>
let hls = null;
let channels = [];
let currentItemId = '';

function setStatus(text) {
    document.getElementById('status').textContent = text;
}

function escapeHtml(str) {
    return (str || '').replace(/[&<>"]/g, s => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;'
    }[s]));
}

function getInitial(name) {
    return (name || '?').trim().charAt(0) || '?';
}

function getSourceUrl() {
    const input = document.getElementById('sourceUrl');
    return input ? input.value.trim() : '';
}

function getSearchKeyword() {
    const input = document.getElementById('searchInput');
    return input ? input.value : '';
}

function updateMeta(list) {
    const groups = new Set(list.map(i => i.group || 'ไม่ได้จัดกลุ่ม''));
    document.getElementById('channelCount').textContent = 'หมายเลขช่อง：' + list.length;
    document.getElementById('groupCount').textContent = 'จำนวนกลุ่ม：' + groups.size;
}

function normalizeKeyword(v) {
    return (v || '').trim().toLowerCase();
}

function renderList() {
    const box = document.getElementById('list');
    const keyword = normalizeKeyword(getSearchKeyword());

    const filtered = channels.filter(ch => {
        if (!keyword) return true;
        const text = [ch.name, ch.group, ch.tvg_name, ch.tvg_id].join(' ').toLowerCase();
        return text.includes(keyword);
    });

    updateMeta(filtered);

    if (!channels.length) {
        box.innerHTML = '<div class="empty">โปรดป้อนที่อยู่การสมัครสมาชิกของคุณแล้วคลิก "โหลดการสมัครสมาชิก" หรือป้อนลิงก์การเล่นโดยตรง。</div>';
        return;
    }

    if (!filtered.length) {
        box.innerHTML = '<div class="empty">ไม่พบช่องที่ตรงกัน</div>';
        return;
    }

    const grouped = {};
    filtered.forEach(ch => {
        const group = ch.group || 'ไม่ได้จัดกลุ่ม';
        if (!grouped[group]) grouped[group] = [];
        grouped[group].push(ch);
    });

    const html = Object.keys(grouped).sort().map(groupName => {
        const items = grouped[groupName].map(ch => {
            const itemId = encodeURIComponent(ch.url);
            const activeClass = currentItemId === itemId ? 'active' : '';
            const logoHtml = ch.logo
                ? `<img class="logo" src="${escapeHtml(ch.logo)}" alt="logo" onerror="this.outerHTML='<div class=\'logo-fallback\'>${escapeHtml(getInitial(ch.name))}</div>'">`
                : `<div class="logo-fallback">${escapeHtml(getInitial(ch.name))}</div>`;

            const subText = ch.tvg_name || ch.tvg_id || ch.url;

            return `
                <div class="item ${activeClass}" onclick="playChannel('${itemId}')">
                    ${logoHtml}
                    <div class="item-text">
                        <div class="item-name">${escapeHtml(ch.name || 'ช่องที่ไม่มีชื่อ')}</div>
                        <div class="item-sub">${escapeHtml(subText)}</div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="group">
                <div class="group-title">${escapeHtml(groupName)}</div>
                ${items}
            </div>
        `;
    }).join('');

    box.innerHTML = html;
}

function attachHls(proxyUrl, title) {
    const video = document.getElementById('video');

    if (hls) {
        hls.destroy();
        hls = null;
    }

    video.pause();
    video.removeAttribute('src');
    video.load();

    document.getElementById('nowPlaying').textContent = title || 'ช่องที่ไม่มีชื่อ';

    if (Hls.isSupported()) {
        hls = new Hls({
            enableWorker: true,
            lowLatencyMode: true,
            backBufferLength: 90
        });

        hls.on(Hls.Events.MEDIA_ATTACHED, function () {
            setStatus('ผู้เล่นเชื่อมต่อแล้วและกำลังโหลดสตรีม...');
        });

        hls.on(Hls.Events.MANIFEST_PARSED, function (_, data) {
            setStatus('พร้อมสำหรับการเล่น，ความละเอียดที่มีอยู่：' + (data.levels ? data.levels.length : 0));
            video.play().catch(() => {});
        });

        hls.on(Hls.Events.ERROR, function (_, data) {
            console.error('HLS error:', data);
            if (data && data.fatal) {
                if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
                    setStatus('ข้อผิดพลาดเครือข่าย: การโหลดสตรีมล้มเหลว');
                    try { hls.startLoad(); } catch (e) {}
                } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) {
                    setStatus('ข้อผิดพลาดของสื่อ: กำลังพยายามเล่นต่อ');
                    try { hls.recoverMediaError(); } catch (e) {}
                } else {
                    setStatus('ข้อผิดพลาดร้ายแรง: ไม่สามารถเล่นช่องปัจจุบันได้');
                    try { hls.destroy(); } catch (e) {}
                }
            } else {
                setStatus('เกิดข้อผิดพลาด：' + (data && data.details ? data.details : 'ข้อผิดพลาดที่ไม่ทราบสาเหตุ'));
            }
        });

        hls.loadSource(proxyUrl);
        hls.attachMedia(video);
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = proxyUrl;
        video.play().catch(() => {});
        setStatus('เล่นโดยใช้ HLS ดั้งเดิมของเบราว์เซอร์');
    } else {
        setStatus('เบราว์เซอร์ปัจจุบันไม่รองรับการเล่น HLS);
        alert('เบราว์เซอร์ปัจจุบันไม่รองรับการเล่น HLS');
    }
}

function play(src, title = 'ที่อยู่แบบกำหนดเอง') {
    if (!src) {
        setStatus(ที่อยู่สำหรับเล่นไฟล์ว่างเปล่า');
        return;
    }

    const proxy = src.includes('proxy.php?url=') ? src : 'proxy.php?url=' + encodeURIComponent(src);
    setStatus('กำลังโหลด：' + title);
    attachHls(proxy, title);
}

function playChannel(itemId) {
    const url = decodeURIComponent(itemId);
    const channel = channels.find(ch => ch.url === url);
    if (!channel) return;

    currentItemId = itemId;
    renderList();
    play(channel.proxy_url || channel.url, channel.name || 'ช่องที่ไม่มีชื่อ');
}

function loadSub() {
    const url = getSourceUrl();
    if (!url) {
        alert('โปรดป้อนที่อยู่สำหรับสมัครรับข้อมูลของคุณ');
        return;
    }

    setStatus('กำลังโหลดการสมัครสมาชิก...');

    fetch('playlist.php?url=' + encodeURIComponent(url))
        .then(async r => {
            const text = await r.text();
            try {
                return JSON.parse(text);
            } catch (e) {
                throw new Error('การสมัครสมาชิกแสดงข้อความแสดงข้อผิดพลาด: 'ข้อผิดพลาดรูปแบบ');
            }
        })
        .then(list => {
            if (!Array.isArray(list)) {
                throw new Error(list && list.message ? list.message : '');
            }

            channels = list;
            currentItemId = '';
            renderList();
            setStatus('การสมัครสมาชิกถูกโหลดสำเร็จแล้ว，ทั่วไป ' + list.length + ' ช่อง);
        })
        .catch(err => {
            console.error(err);
            channels = [];
            renderList();
            setStatus('การสมัครสมาชิกโหลดไม่สำเร็จ);
            alert('การสมัครสมาชิกโหลดไม่สำเร็จ：' + (err.message || 'ข้อผิดพลาดที่ไม่ทราบสาเหตุ'));
        });
}

function playDirect() {
    const url = getSourceUrl();
    if (!url) {
        alert('โปรดป้อนที่อยู่สำหรับเล่นวิดีโอ');
        return;
    }
    currentItemId = '';
    renderList();
    play(url, 'เล่นโดยตรง');
}
</script>
</body>
</html>
