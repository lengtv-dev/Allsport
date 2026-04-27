// api/proxy.js
export const config = {
  api: {
    responseLimit: false, // ปิดขีดจำกัดขนาดไฟล์สำหรับ streaming
  },
};

export default async function handler(req, res) {
  const { url: target } = req.query;

  // 1. ตรวจสอบว่ามี URL ส่งมาหรือไม่
  if (!target) {
    return res.status(400).json({ error: "กรุณาระบุ url parameter" });
  }

  try {
    // ป้องกันการค้างของ function (Timeout 10 วินาที)
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    const response = await fetch(target, {
      method: "GET",
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://warpdooball.net/",
        "Origin": "https://warpdooball.net",
        "Accept": "*/*"
      },
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (!response.ok) {
      return res.status(response.status).json({ 
        error: `ต้นทางตอบกลับด้วยสถานะ: ${response.status}`,
        target: target 
      });
    }

    const contentType = response.headers.get("content-type") || "";
    
    // ตั้งค่า CORS ให้ Frontend เรียกใช้งานได้
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS");

    // 2. กรณีเป็นไฟล์ Playlist (.m3u8)
    if (contentType.includes("mpegurl") || target.includes(".m3u8")) {
      let text = await response.text();
      const targetUrl = new URL(target);
      
      const lines = text.split('\n');
      const rewrittenLines = lines.map(line => {
        const trimmed = line.trim();
        // ถ้าเป็นบรรทัดว่างหรือ Comment ไม่ต้องแก้
        if (!trimmed || trimmed.startsWith('#')) return line;
        
        try {
          // แปลง Relative Path ให้เป็น Absolute Path
          const absoluteUrl = new URL(trimmed, targetUrl).href;
          // ส่งกลับไปที่ proxy ตัวเองเพื่อหลอก Referer ในขั้นตอนต่อไป
          return `/api/proxy?url=${encodeURIComponent(absoluteUrl)}`;
        } catch (e) {
          return line;
        }
      });

      res.setHeader("Content-Type", "application/vnd.apple.mpegurl; charset=utf-8");
      return res.send(rewrittenLines.join('\n'));
    } 
    
    // 3. กรณีเป็นไฟล์ Segment (.ts, .dts, .mp4)
    const buffer = await response.arrayBuffer();
    res.setHeader("Content-Type", contentType || "video/mp2t");
    res.setHeader("Cache-Control", "public, max-age=3600"); // เก็บ cache ไว้ 1 ชม. เพื่อความเร็ว
    return res.send(Buffer.from(buffer));

  } catch (err) {
    console.error("Proxy Error:", err.message);
    return res.status(500).json({ 
      error: "fetch failed", 
      reason: err.message,
      tip: "ลองตรวจสอบว่า URL ต้นทางยังใช้งานได้ หรือ IP ของ Server โดนบล็อกหรือไม่"
    });
  }
}
