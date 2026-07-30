import requests, re, json, os, time, random
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, urljoin
from clint.textui import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

#####################################################################
# 🔧 ค่าตั้งต้น - ปรับแก้ได้ง่าย
web_category = "https://www.24hd.vip/category/netflix/"
start_page = 1
end_page = 5
MAX_RETRY = 3
TIMEOUT = 25
MAX_WORKERS = 10
MIN_SLEEP = 0.1
MAX_SLEEP = 0.3
######################################################################
f_path = os.path.join("C:", "24hd", "movies")
os.makedirs(f_path, exist_ok=True)
########################################################################
category_name = unquote(urlparse(web_category).path.strip('/').split('/')[-1])
f_w3u = f"24HD_Movies_{category_name}_page{start_page}-{end_page}.w3u"
f_m3u = f"24HD_Movies_{category_name}_page{start_page}-{end_page}.m3u"

#################################################
W_W3U = 1
W_M3U = 1
#################################################
from datetime import datetime
now = datetime.now()
date = now.strftime("%d")
mo = now.strftime("%m")
month = ['', 'ม.ค.', 'ก.พ.', 'มี.ค', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
timeday = f'{date} {month[int(mo)]} {int(now.strftime("%Y"))+543}'
timehour = now.strftime("%H:%M")
#################################################

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
        thread_local.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'th,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        })
    return thread_local.session

def safe_get_fast(url, **kwargs):
    sess = get_session()
    try:
        r = sess.get(url, timeout=10, **kwargs)
        r.raise_for_status()
        return r
    except Exception:
        return None

def safe_get(sess, url, **kwargs):
    last_err = None
    for attempt in range(1, MAX_RETRY+1):
        try:
            r = sess.get(url, timeout=TIMEOUT, **kwargs)
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            last_err = e
            wait = round(attempt * 0.5, 1)
            time.sleep(wait)
    return None

def create_session(referer):
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    sess = requests.Session()
    sess.headers.update({
        'User-Agent': ua,
        'Referer': referer,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'th,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
    })
    return sess

def get_image_url(img_element):
    if not img_element:
        return ""
    return img_element.get("src") or img_element.get("data-src") or ""

def get_cover_image(soup):
    og_image = soup.find('meta', property='og:image')
    if og_image:
        url = og_image.get('content', '')
        if url:
            return url
    
    img = soup.find('img', class_='attachment-full')
    if img:
        url = get_image_url(img)
        if url:
            return url
    
    img = soup.find('img', class_=re.compile(r'wp-image'))
    if img:
        url = get_image_url(img)
        if url:
            return url
    
    for div in soup.find_all('div', style=True):
        style = div.get('style', '')
        match = re.search(r'background-image:\s*url\(["\']?([^"\'\)]+)["\']?\)', style, re.IGNORECASE)
        if match:
            url = match.group(1)
            if '/uploads/' in url and 'cropped-24-HD' not in url:
                return url
    
    return ""

def get_audio_info(soup):
    for h2 in soup.find_all('h2', class_='elementor-heading-title'):
        text = h2.text.strip()
        if 'เสียง :' in text or 'เสียง:' in text:
            if ':' in text:
                audio = text.split(':', 1)[-1].strip()
            elif '：' in text:
                audio = text.split('：', 1)[-1].strip()
            else:
                audio = text.replace('เสียง', '').strip()
            return audio
    return "ไม่พบข้อมูล"

def get_movie_title(soup, default=""):
    h1 = soup.find('h1', class_='elementor-heading-title')
    if h1:
        return h1.text.strip()
    h2 = soup.find('h2', class_='elementor-heading-title')
    if h2:
        return h2.text.strip()
    title = soup.find('title')
    if title:
        return title.text.strip()
    return default

def extract_movie_links_from_page(soup, base_url):
    movie_links = []
    loop_container = soup.find('div', class_='elementor-loop-container')
    
    if loop_container:
        for a_tag in loop_container.find_all('a', href=True):
            href = a_tag.get('href', '')
            if href and '/category/' not in href and '#' not in href:
                if href not in [link['url'] for link in movie_links]:
                    title = ''
                    title_div = a_tag.find('div', class_=re.compile(r'd793f5f'))
                    if title_div:
                        inner = title_div.find('div', class_='elementor-heading-title')
                        if inner:
                            title = inner.text.strip()
                    
                    if not title:
                        slug = href.rstrip('/').split('/')[-1]
                        title = slug.replace('-', ' ').title()
                    
                    img_url = ''
                    bg_div = a_tag.find('div', style=re.compile(r'background-image'))
                    if bg_div:
                        style = bg_div.get('style', '')
                        match = re.search(r'background-image:\s*url\(["\']?([^"\'\)]+)["\']?\)', style, re.IGNORECASE)
                        if match:
                            img_url = match.group(1)
                    
                    movie_links.append({
                        'url': urljoin(base_url, href),
                        'title': title,
                        'image': img_url
                    })
    
    return movie_links

def extract_embed_id_from_url(iframe_url):
    """ดึง embed_id จาก URL playermhd.p2phls.xyz (รูปแบบเก่า)"""
    if not iframe_url or iframe_url == 'about:blank':
        return None
    
    if 'playermhd.p2phls.xyz/embed/' not in iframe_url:
        return None
    
    embed_id = iframe_url.split('/embed/')[-1]
    embed_id = embed_id.split('?')[0]
    embed_id = embed_id.rstrip('/')
    
    if embed_id and embed_id != 'about:blank':
        return embed_id
    
    return None

def extract_embed_id_from_url_v2(iframe_url):
    """ดึง embed_id จาก URL player77hdfree.xyz (รูปแบบใหม่)"""
    if not iframe_url or iframe_url == 'about:blank':
        return None
    
    if 'player77hdfree.xyz/embed/' not in iframe_url:
        return None
    
    embed_id = iframe_url.split('/embed/')[-1]
    embed_id = embed_id.split('?')[0]
    embed_id = embed_id.rstrip('/')
    
    if embed_id and embed_id != 'about:blank':
        return embed_id
    
    return None

def process_movie_page_fast(movie_info, base_url):
    url = movie_info['url']
    movie_title = movie_info['title']
    movie_img = movie_info['image']
    
    r = safe_get_fast(url)
    if not r:
        return None
    
    soup = BeautifulSoup(r.content, "lxml")
    
    movie_name = get_movie_title(soup, movie_title)
    cover_url = get_cover_image(soup)
    if not cover_url and movie_img:
        cover_url = movie_img
    audio_info = get_audio_info(soup)
    
    iframe_url = None
    embed_id = None
    
    # ✅ วิธีที่ 1: iframe id="player" (รูปแบบเก่า playermhd.p2phls.xyz)
    iframe = soup.find('iframe', {'id': 'player'})
    if iframe:
        src = iframe.get('src') or iframe.get('data-src') or ''
        if 'playermhd.p2phls.xyz/embed/' in src:
            iframe_url = src
            embed_id = extract_embed_id_from_url(iframe_url)
            if embed_id:
                print(f"      🔍 พบ iframe id='player' (เก่า): {embed_id}")
    
    # ✅ วิธีที่ 2: iframe name="box-player" (รูปแบบใหม่)
    if not embed_id:
        iframe = soup.find('iframe', {'name': 'box-player'})
        if iframe:
            src = iframe.get('src') or iframe.get('data-src') or ''
            if 'player77hdfree.xyz/embed/' in src:
                iframe_url = src
                embed_id = extract_embed_id_from_url_v2(iframe_url)
                if embed_id:
                    print(f"      🔍 พบ iframe name='box-player' (ใหม่): {embed_id}")
    
    # ✅ วิธีที่ 3: iframe ใน div id="box-player"
    if not embed_id:
        box_player = soup.find('div', {'id': 'box-player'})
        if box_player:
            iframe = box_player.find('iframe')
            if iframe:
                src = iframe.get('src') or iframe.get('data-src') or ''
                if 'player77hdfree.xyz/embed/' in src:
                    iframe_url = src
                    embed_id = extract_embed_id_from_url_v2(iframe_url)
                    if embed_id:
                        print(f"      🔍 พบ iframe ใน div#box-player (ใหม่): {embed_id}")
                elif 'playermhd.p2phls.xyz/embed/' in src:
                    iframe_url = src
                    embed_id = extract_embed_id_from_url(iframe_url)
                    if embed_id:
                        print(f"      🔍 พบ iframe ใน div#box-player (เก่า): {embed_id}")
    
    # ✅ วิธีที่ 4: iframe ทั่วไป
    if not embed_id:
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src') or iframe.get('data-src') or ''
            if 'player77hdfree.xyz/embed/' in src:
                iframe_url = src
                embed_id = extract_embed_id_from_url_v2(iframe_url)
                if embed_id:
                    print(f"      🔍 พบ iframe player77hdfree (ใหม่): {embed_id}")
                    break
            elif 'playermhd.p2phls.xyz/embed/' in src:
                iframe_url = src
                embed_id = extract_embed_id_from_url(iframe_url)
                if embed_id:
                    print(f"      🔍 พบ iframe playermhd (เก่า): {embed_id}")
                    break
    
    # ✅ วิธีที่ 5: a tag ที่มีลิงก์
    if not embed_id:
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            if 'player77hdfree.xyz/embed/' in href:
                iframe_url = href
                embed_id = extract_embed_id_from_url_v2(iframe_url)
                if embed_id:
                    print(f"      🔍 พบลิงก์จาก a tag (ใหม่): {embed_id}")
                    break
            elif 'playermhd.p2phls.xyz/embed/' in href:
                iframe_url = href
                embed_id = extract_embed_id_from_url(iframe_url)
                if embed_id:
                    print(f"      🔍 พบลิงก์จาก a tag (เก่า): {embed_id}")
                    break
    
    # ✅ ถ้าเจอ embed_id
    if embed_id:
        m3u8_url = f"https://vdohls.com/{embed_id}/playlist.m3u8"
        return {
            'name': movie_name,
            'image': cover_url,
            'url': m3u8_url,
            'referer': base_url,
            'info': audio_info
        }
    
    return None

def process_category_pagination_fast(url, sess, base_url, start_page, end_page):
    """ประมวลผลหน้าหมวดหมู่แบบเร็ว - จัดกลุ่มตามหน้า"""
    all_groups = []
    total_found = 0
    
    print("\n📥 กำลังดึงรายการหนัง...")
    
    for page_num in range(start_page, end_page + 1):
        page_url = url if page_num == 1 else f"{url}/page/{page_num}/"
        
        r = safe_get(sess, page_url)
        if not r:
            continue
        
        soup = BeautifulSoup(r.content, 'lxml')
        movie_links = extract_movie_links_from_page(soup, base_url)
        
        if not movie_links:
            print(f"   📄 หน้า {page_num}: ไม่พบรายการ")
            continue
        
        print(f"   📄 หน้า {page_num}: พบ {len(movie_links)} เรื่อง")
        total_found += len(movie_links)
        
        group_stations = []
        group_name = f"หน้า {page_num}"
        
        print(f"\n🚀 กำลังดึงข้อมูลหน้า {page_num} ด้วย {MAX_WORKERS} เธรด...")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_movie = {
                executor.submit(process_movie_page_fast, movie_info, base_url): movie_info
                for movie_info in movie_links
            }
            
            completed = 0
            for future in as_completed(future_to_movie):
                movie_info = future_to_movie[future]
                completed += 1
                
                try:
                    result = future.result(timeout=15)
                    if result:
                        group_stations.append(result)
                        print(f"      ✅ [{completed}/{len(movie_links)}] {result['name'][:40]}")
                    else:
                        print(f"      ❌ [{completed}/{len(movie_links)}] {movie_info['title'][:40]} - ไม่พบลิงก์")
                except Exception as e:
                    print(f"      ⚠️ [{completed}/{len(movie_links)}] {movie_info['title'][:40]} - Error: {str(e)[:30]}")
        
        if group_stations:
            all_groups.append({
                "name": group_name,
                "stations": group_stations
            })
            print(f"   📊 หน้า {page_num}: ดึงสำเร็จ {len(group_stations)} เรื่อง\n")
    
    return all_groups, total_found

def save_files(jseries):
    """บันทึกผลลัพธ์เป็นไฟล์ .w3u (JSON) และ .m3u (เพลย์ลิสต์)"""
    if W_W3U:
        w3u_path = os.path.join(f_path, f_w3u)
        with open(w3u_path, 'w', encoding='utf-8') as f:
            json.dump(jseries, f, indent=1, ensure_ascii=False)
        print(colored.green(f"✅ บันทึก .w3u: {w3u_path}"))
    
    if W_M3U:
        group_name = jseries.get('name', 'Movies')
        
        m3u = "#EXTM3U\n"
        m3u += f"#X-TVGUIDE: {base_url}\n"
        m3u += f"#X-URL: {base_url}\n\n"
        
        for group in jseries.get('groups', []):
            for st in group.get('stations', []):
                name = st.get('name', 'ไม่พบชื่อ')
                info = st.get('info', '')
                url = st.get('url', '')
                image = st.get('image', '')
                
                if url:
                    line = f'#EXTINF:-1 group-title="{group_name}" tvg-logo="{image}"'
                    if info:
                        line += f' ,{name} [{info}]'
                    else:
                        line += f' ,{name}'
                    m3u += f'{line}\n{url}\n\n'
        
        m3u_path = os.path.join(f_path, f_m3u)
        with open(m3u_path, 'w', encoding='utf-8') as f:
            f.write(m3u.strip())
        print(colored.green(f"✅ บันทึก .m3u: {m3u_path}"))

#################################################
# 🚀 เริ่มทำงาน
print("\n" + "="*70)
print(colored.cyan("🚀 24HD Movies Downloader (จัดกลุ่มตามหน้า)"))
print(colored.yellow(f"   🔥 Multi-thread: {MAX_WORKERS} เธรด"))
print("="*70)

start_time = time.time()

jseries = {
    "name": "",
    "author": f" อัพเดต {timeday} {timehour}",
    "info": "24HD Movies Downloader - จัดกลุ่มตามหน้า",
    "image": "",
    "groups": []
}

base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(web_category))
sess = create_session(base_url)

print(f"\n📂 หมวดหมู่: {web_category}")
print(f"📄 หน้า: {start_page} - {end_page}")
print(f"📁 บันทึกที่: {f_path}")
print("\n" + "="*70)

all_groups, total_found = process_category_pagination_fast(web_category, sess, base_url, start_page, end_page)

if not all_groups:
    print(colored.red("\n❌ ไม่พบข้อมูล"))
    exit()

jseries['name'] = f"Movies ({category_name}) หน้า {start_page}-{end_page}"
jseries['groups'] = all_groups

save_files(jseries)

elapsed = time.time() - start_time

print("\n" + "="*70)
print(colored.green("✅ เสร็จสิ้น!"))
print(f"📊 พบทั้งหมด {total_found} เรื่อง")
total_stations = sum(len(g['stations']) for g in all_groups)
print(f"📊 ดึงสำเร็จ {total_stations} เรื่อง")
print(f"📊 แยกเป็น {len(all_groups)} กลุ่ม")
print(f"⏱️ ใช้เวลา {elapsed:.1f} วินาที")
print(f"📂 {os.path.join(f_path, f_w3u)}")
print(f"📂 {os.path.join(f_path, f_m3u)}")
print("="*70)

print("\n📋 สรุปตามหน้า:")
for group in all_groups:
    print(f"   📂 {group['name']}: {len(group['stations'])} เรื่อง")