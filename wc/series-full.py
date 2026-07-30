import requests, re, json, os, time, random
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, urljoin
from clint.textui import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

#####################################################################
# 🔧 ค่าตั้งต้น - ปรับแก้ได้ง่าย
web_category = "https://www.24hd.vip/category/%e0%b8%94%e0%b8%b9%e0%b8%8b%e0%b8%b5%e0%b8%a3%e0%b8%b5%e0%b9%88%e0%b8%a2%e0%b9%8c/"
start_page = 1
end_page = 2
MAX_RETRY = 3
TIMEOUT = 25
MAX_WORKERS = 10
MIN_SLEEP = 0.1
MAX_SLEEP = 0.3
######################################################################
f_path = os.path.join("C:", "24hd", "series")
os.makedirs(f_path, exist_ok=True)
########################################################################
category_name = unquote(urlparse(web_category).path.strip('/').split('/')[-1])
f_w3u = f"24HD_Series_{category_name}_page{start_page}-{end_page}.w3u"
f_m3u = f"24HD_Series_{category_name}_page{start_page}-{end_page}.m3u"

#################################################
W_W3U = 1
W_M3U = 1
#################################################
aseries = """{
    "name": "",
    "author": " อัพเดต ",
    "info": "24HD Series Downloader - เฉพาะซีรี่ส์",
    "image": "",
    "groups": [],
    "stations": []}
"""
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
    """ดึงข้อมูลแบบเร็ว (ใช้ session pool)"""
    sess = get_session()
    try:
        r = sess.get(url, timeout=10, **kwargs)
        r.raise_for_status()
        return r
    except Exception:
        return None

def safe_get(sess, url, **kwargs):
    """ดึงข้อมูลพร้อมระบบลองใหม่อัตโนมัติ"""
    last_err = None
    for attempt in range(1, MAX_RETRY+1):
        try:
            r = sess.get(url, timeout=TIMEOUT, **kwargs)
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as e:
            last_err = e
            wait = round(attempt * 0.5, 1)
            print(colored.yellow(f"   ⏳ ลองใหม่ครั้งที่ {attempt}/{MAX_RETRY} รอ {wait}วินาที..."))
            time.sleep(wait)
    print(colored.red(f"   ❌ ล้มเหลว: {str(last_err)[:80]}"))
    return None

def create_session(referer):
    """สร้าง session พร้อม headers"""
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
    """ดึง URL รูปจาก img element"""
    if not img_element:
        return ""
    return (
        img_element.get("src") or
        img_element.get("data-src") or
        img_element.get("data-lazy-src") or
        ""
    )

def get_cover_image(soup):
    """ดึงรูปปกจากหน้าเรื่อง - รองรับหลายรูปแบบ"""
    
    # ✅ วิธีที่ 1: ดึงจาก og:image (ได้ผลที่สุด)
    og_image = soup.find('meta', property='og:image')
    if og_image:
        url = og_image.get('content', '')
        if url:
            return url
    
    # ✅ วิธีที่ 2: หา img class="attachment-full"
    img = soup.find('img', class_='attachment-full')
    if img:
        url = get_image_url(img)
        if url:
            return url
    
    # ✅ วิธีที่ 3: หา img ที่มี wp-image
    img = soup.find('img', class_=re.compile(r'wp-image'))
    if img:
        url = get_image_url(img)
        if url:
            return url
    
    # ✅ วิธีที่ 4: หา div ที่มี background-image
    for div in soup.find_all('div', style=True):
        style = div.get('style', '')
        match = re.search(r'background-image:\s*url\(["\']?([^"\'\)]+)["\']?\)', style, re.IGNORECASE)
        if match:
            url = match.group(1)
            if '/uploads/' in url and ('.webp' in url or '.jpg' in url):
                if 'cropped-24-HD' not in url and 'logo' not in url:
                    return url
    
    # ✅ วิธีที่ 5: หา img ที่ลงท้ายด้วย .webp
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src and src.endswith('.webp') and 'uploads' in src:
            if 'cropped-24-HD' not in src and 'logo' not in src:
                return src
    
    return ""

def get_audio_info(soup):
    """ดึงข้อมูลเสียงจากหน้าเรื่อง"""
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

def clean_movie_name(title):
    """ทำความสะอาดชื่อเรื่อง: ตัด EP.XX ออก"""
    if not title:
        return title
    
    # ลบ EP.ตัวเลข ท้ายชื่อ
    cleaned = re.sub(r'\s*EP\.?\s*[\d-]+$', '', title, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*ตอนที่\s*[\d-]+$', '', cleaned)
    
    if cleaned == title:
        return title
    
    return cleaned.strip()

def get_category_title(soup):
    """ดึงชื่อหมวดหมู่จากหน้า"""
    # ลองจาก h1
    h1 = soup.find('h1', class_='elementor-heading-title')
    if h1:
        return h1.text.strip()
    
    # ลองจาก title
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip()
    
    # ลองจาก breadcrumb
    breadcrumb = soup.find('nav', class_=re.compile(r'breadcrumb'))
    if breadcrumb:
        last_item = breadcrumb.find_all('li')[-1] if breadcrumb.find_all('li') else None
        if last_item:
            return last_item.text.strip()
    
    return "ไม่พบชื่อหมวดหมู่"

def extract_movie_links_from_page(soup, base_url):
    """ดึงลิงก์หนังทั้งหมดจากหน้าหมวดหมู่ (รองรับ Elementor Loop Grid)"""
    movie_links = []
    
    # ✅ วิธีหลัก: หาจาก Elementor Loop Grid
    loop_container = soup.find('div', class_='elementor-loop-container')
    
    if loop_container:
        for a_tag in loop_container.find_all('a', href=True):
            href = a_tag.get('href', '')
            if href and '/category/' not in href and '#' not in href:
                if href not in [link['url'] for link in movie_links]:
                    # หาชื่อเรื่อง
                    title_elem = a_tag.find('div', class_=re.compile(r'd793f5f|elementor-heading-title'))
                    if title_elem:
                        title = title_elem.text.strip()
                    else:
                        title = a_tag.get('title') or a_tag.text.strip() or 'ไม่พบชื่อ'
                    
                    # หารูปปกจาก background-image
                    img_url = ''
                    bg_div = a_tag.find('div', style=re.compile(r'background-image'))
                    if bg_div:
                        style = bg_div.get('style', '')
                        match = re.search(r'background-image:\s*url\(["\']?([^"\'\)]+)["\']?\)', style, re.IGNORECASE)
                        if match:
                            img_url = match.group(1)
                    
                    # ถ้าหาไม่เจอ ลองจาก img tag
                    if not img_url:
                        img = a_tag.find('img')
                        if img:
                            img_url = get_image_url(img)
                    
                    movie_links.append({
                        'url': urljoin(base_url, href),
                        'title': title,
                        'image': img_url
                    })
    
    # ✅ วิธีสำรอง: หาจาก div ที่มีคลาส e-loop-item
    if not movie_links:
        loop_items = soup.find_all('div', class_=re.compile(r'e-loop-item'))
        for item in loop_items:
            a_tag = item.find('a', href=True)
            if a_tag:
                href = a_tag.get('href', '')
                if href and '/category/' not in href and '#' not in href:
                    title_elem = a_tag.find('div', class_=re.compile(r'd793f5f|elementor-heading-title'))
                    title = title_elem.text.strip() if title_elem else a_tag.get('title', 'ไม่พบชื่อ')
                    
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
    
    # เอา URL ซ้ำออก
    seen = set()
    unique_links = []
    for link in movie_links:
        if link['url'] not in seen:
            seen.add(link['url'])
            unique_links.append(link)
    
    return unique_links

def process_series_page_fast(movie_info, base_url):
    """ประมวลผลหน้า Series แบบเร็ว - เฉพาะซีรี่ส์"""
    url = movie_info['url']
    movie_title = movie_info['title']
    movie_img = movie_info['image']
    
    r = safe_get_fast(url)
    if not r:
        return None
    
    soup = BeautifulSoup(r.content, "lxml")
    
    # ✅ หาชื่อเรื่อง
    movie_name = "ไม่พบชื่อเรื่อง"
    h1_elem = soup.find('h1', class_='elementor-heading-title')
    if h1_elem:
        movie_name = h1_elem.text.strip()
    else:
        h2_elem = soup.find('h2', class_='elementor-heading-title')
        if h2_elem:
            movie_name = h2_elem.text.strip()
        else:
            title_tag = soup.find('title')
            if title_tag:
                movie_name = title_tag.text.strip()
    
    clean_name = clean_movie_name(movie_name)
    
    # ✅ หารูปปก
    cover_url = get_cover_image(soup)
    if not cover_url and movie_img:
        cover_url = movie_img
    
    # ✅ หาเสียง
    audio_info = get_audio_info(soup)
    
    # ✅ ดึง EP (ต้องมีปุ่ม EP)
    ep_buttons = soup.find_all('button', class_='swicth-ep')
    
    if not ep_buttons:
        # ❌ ถ้าไม่มี EP แสดงว่าไม่ใช่ซีรี่ส์
        return None
    
    stations = []
    for btn in ep_buttons:
        ep_name = btn.text.strip()
        embed_url = btn.get('data-link')
        if embed_url:
            m3u8_url = embed_to_m3u8(embed_url)
            if m3u8_url:
                # ✅ ตัดชื่อเรื่องออก เหลือแค่ EP.1, EP.2, ...
                ep_short = re.sub(r'^.*?(EP\.?\s*[\d-]+|ตอนที่\s*[\d-]+)', r'\1', ep_name, flags=re.IGNORECASE)
                if ep_short == ep_name:
                    ep_short = ep_name.replace(clean_name, '').strip()
                    if not ep_short:
                        ep_short = f"EP.{len(stations)+1}"
                
                stations.append({
                    'name': ep_short,
                    'image': cover_url,
                    'url': m3u8_url,
                    'referer': base_url,
                    'info': audio_info
                })
    
    if stations:
        return {
            'name': clean_name if clean_name != 'ไม่พบชื่อเรื่อง' else movie_title,
            'image': cover_url,
            'info': audio_info,
            'stations': stations
        }
    
    return None

def embed_to_m3u8(embed_url):
    """แปลง embed URL เป็น m3u8 URL"""
    if not embed_url:
        return None
    if "/embed/" in embed_url:
        embed_id = embed_url.split("/embed/")[-1]
        embed_id = embed_id.split('?')[0]
        return f"https://vdohls.com/{embed_id}/playlist.m3u8"
    if len(embed_url) == 32 and embed_url.isalnum():
        return f"https://vdohls.com/{embed_url}/playlist.m3u8"
    return None

def process_category_pagination_fast(url, sess, base_url, start_page, end_page):
    """ประมวลผลหน้าหมวดหมู่แบบเร็ว - จัดกลุ่มตามหน้า"""
    all_groups = []
    total_found = 0
    category_title = ""
    
    print("\n📥 กำลังดึงรายการซีรี่ส์...")
    
    for page_num in range(start_page, end_page + 1):
        page_url = url if page_num == 1 else f"{url}/page/{page_num}/"
        
        r = safe_get(sess, page_url)
        if not r:
            continue
        
        soup = BeautifulSoup(r.content, 'lxml')
        
        if page_num == start_page and not category_title:
            category_title = get_category_title(soup)
            print(f"   📂 หมวดหมู่: {category_title}")
        
        movie_links = extract_movie_links_from_page(soup, base_url)
        
        if not movie_links:
            print(f"   📄 หน้า {page_num}: ไม่พบรายการ")
            continue
        
        print(f"   📄 หน้า {page_num}: พบ {len(movie_links)} เรื่อง")
        total_found += len(movie_links)
        
        # ✅ สร้างกลุ่มสำหรับหน้านี้
        group_stations = []
        group_name = f"หน้า {page_num}"
        
        print(f"\n🚀 กำลังตรวจสอบซีรี่ส์หน้า {page_num} ด้วย {MAX_WORKERS} เธรด...")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_movie = {
                executor.submit(process_series_page_fast, movie_info, base_url): movie_info
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
                        ep_count = len(result['stations'])
                        print(f"      ✅ [{completed}/{len(movie_links)}] {result['name'][:40]} → {ep_count} EP [🔊 {result['info']}]")
                    else:
                        print(f"      ❌ [{completed}/{len(movie_links)}] {movie_info['title'][:40]} - ไม่ใช่ซีรี่ส์")
                except Exception as e:
                    print(f"      ⚠️ [{completed}/{len(movie_links)}] {movie_info['title'][:40]} - Error: {str(e)[:30]}")
        
        # ✅ เพิ่มกลุ่มลงใน all_groups
        if group_stations:
            all_groups.append({
                "name": group_name,
                "stations": group_stations
            })
            print(f"   📊 หน้า {page_num}: พบซีรี่ส์ {len(group_stations)} เรื่อง\n")
    
    return all_groups, total_found, category_title

def save_files(jseries):
    """บันทึกผลลัพธ์เป็นไฟล์ .w3u (JSON) และ .m3u (เพลย์ลิสต์)"""
    if W_W3U:
        w3u_path = os.path.join(f_path, f_w3u)
        with open(w3u_path, 'w', encoding='utf-8') as f:
            json.dump(jseries, f, indent=1, ensure_ascii=False)
        print(colored.green(f"✅ บันทึก .w3u: {w3u_path}"))
    
    if W_M3U:
        m3u = "#EXTM3U\n"
        m3u += f"#X-TVGUIDE: {base_url}\n"
        m3u += f"#X-URL: {base_url}\n\n"
        
        # ✅ ดึง stations จากทุกกลุ่ม
        for group in jseries.get('groups', []):
            group_name = group.get('name', 'ไม่พบชื่อหน้า')
            for movie in group.get('stations', []):
                movie_name = movie.get('name', 'ไม่พบชื่อเรื่อง')
                movie_image = movie.get('image', '')
                audio_info = movie.get('info', '')
                
                for st in movie.get('stations', []):
                    station_name = st.get('name', 'ไม่พบชื่อ EP')
                    station_url = st.get('url', '')
                    station_image = st.get('image', '') or movie_image
                    
                    if station_url:
                        # ✅ เพิ่ม group-title, tvg-logo (รูปปก), และ info
                        line = f'#EXTINF:-1 group-title="{movie_name}" tvg-logo="{station_image}"'
                        if audio_info:
                            line += f' ,{station_name} [{audio_info}]'
                        else:
                            line += f' ,{station_name}'
                        m3u += f'{line}\n{station_url}\n\n'
        
        m3u_path = os.path.join(f_path, f_m3u)
        with open(m3u_path, 'w', encoding='utf-8') as f:
            f.write(m3u.strip())
        print(colored.green(f"✅ บันทึก .m3u: {m3u_path}"))

#################################################
# 🚀 เริ่มทำงาน
print("\n" + "="*70)
print(colored.cyan("🚀 24HD Series Downloader (จัดกลุ่มตามหน้า)"))
print(colored.yellow(f"   🔥 Multi-thread: {MAX_WORKERS} เธรด"))
print(colored.yellow("   🔍 ข้ามหนังเดี่ยว"))
print("="*70)

start_time = time.time()

jseries = json.loads(aseries)
base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(web_category))
sess = create_session(base_url)

print(f"\n📂 หมวดหมู่: {web_category}")
print(f"📄 หน้า: {start_page} - {end_page}")
print(f"📁 บันทึกที่: {f_path}")
print("\n" + "="*70)

# ดึงข้อมูลทุกหน้า
all_groups, total_found, category_title = process_category_pagination_fast(web_category, sess, base_url, start_page, end_page)

if not all_groups:
    print(colored.red("\n❌ ไม่พบซีรี่ส์"))
    exit()

# ✅ ใช้ชื่อหมวดหมู่ที่ดึงได้จากหน้าเว็บ
if not category_title:
    category_title = "ไม่พบชื่อหมวดหมู่"

# อัพเดท jseries
jseries['name'] = f"Series ({category_title}) หน้า {start_page}-{end_page}"
jseries['image'] = "https://www.24hd.vip/wp-content/uploads/2024/01/24hd-logo.png"
jseries['author'] += f" {timeday} {timehour}"
jseries['info'] = f"24HD Series Downloader - พบ {len(all_groups)} กลุ่ม จาก {total_found} เรื่อง"
jseries['groups'] = all_groups

# บันทึกไฟล์
save_files(jseries)

elapsed = time.time() - start_time

# สรุปผล
print("\n" + "="*70)
print(colored.green("✅ เสร็จสิ้น!"))
print(f"📊 พบทั้งหมด {total_found} เรื่อง")
total_series = sum(len(g['stations']) for g in all_groups)
print(f"📊 เป็นซีรี่ส์ {total_series} เรื่อง")
print(f"📊 แยกเป็น {len(all_groups)} กลุ่ม (ตามหน้า)")
total_eps = 0
for group in all_groups:
    for movie in group.get('stations', []):
        total_eps += len(movie.get('stations', []))
print(f"📊 รวมทั้งหมด {total_eps} EP")
print(f"⏱️ ใช้เวลา {elapsed:.1f} วินาที")
print(f"\n📂 {os.path.join(f_path, f_w3u)}")
print(f"📂 {os.path.join(f_path, f_m3u)}")
print("="*70)

# แสดงตัวอย่างบางส่วน
print("\n📋 สรุปตามหน้า:")
for group in all_groups:
    print(f"   📂 {group['name']}: {len(group['stations'])} ซีรี่ส์")
    for movie in group['stations'][:3]:
        ep_count = len(movie['stations'])
        audio_info = movie.get('info', 'ไม่พบข้อมูล')
        print(f"      🎬 {movie['name'][:40]} → {ep_count} EP [🔊 {audio_info}]")
    if len(group['stations']) > 3:
        print(f"      ... และอีก {len(group['stations']) - 3} เรื่อง")