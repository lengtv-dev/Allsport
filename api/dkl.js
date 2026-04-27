export default async function handler(req, res) {
  const target = req.query.url;
  const referer = req.query.referer || "https://warpdooball.net/";

  if (!target) {
    res.status(400).json({ error: "Missing url parameter" });
    return;
  }

  try {
    const response = await fetch(target, {
      headers: {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer,
        "Origin": referer
      }
    });

    if (!response.ok) {
      res.status(response.status).send("Fetch error");
      return;
    }

    const contentType = response.headers.get("content-type") || "";

    // ถ้าเป็น m3u8 ต้อง rewrite URL
    if (contentType.includes("application/vnd.apple.mpegurl") || target.includes(".m3u8")) {

      let text = await response.text();
      const base = target.substring(0, target.lastIndexOf("/") + 1);

      text = text
        .split("\n")
        .map(line => {
          if (
            line &&
            !line.startsWith("#") &&
            !line.startsWith("http")
          ) {
            const absolute = base + line;
            return `/api/proxy?url=${encodeURIComponent(absolute)}&referer=${encodeURIComponent(referer)}`;
          }

          if (line.startsWith("http")) {
            return `/api/proxy?url=${encodeURIComponent(line)}&referer=${encodeURIComponent(referer)}`;
          }

          return line;
        })
        .join("\n");

      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Content-Type", "application/vnd.apple.mpegurl");

      res.status(200).send(text);
      return;
    }

    // ถ้าเป็น segment video
    const buffer = await response.arrayBuffer();

    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Content-Type", contentType);

    res.status(200).send(Buffer.from(buffer));

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
