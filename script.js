//script-v2.js

let allMovies = [];
let allMoviesByTitle = {};
let originalSectionsHtml = "";

// --- [ COMMON FUNCTIONS ] ---
function createMovieCard(movie) {
  const moviePlayer = movie.player || "watch";
  const movieFile = movie.file || movie.url || movie.video;
  const movieName = movie.name || "";
  const movieSubtitle = movie.subtitle;

  let watchUrl = `${moviePlayer}.html?file=${encodeURIComponent(movieFile || "")}&name=${encodeURIComponent(movieName)}`;
  if (movieSubtitle && movieSubtitle.trim() !== "") {
    watchUrl += `&subtitle=${encodeURIComponent(movieSubtitle)}`;
  }

  // ✅ ดึง poster จาก info.poster ถ้ามี
  const poster = movie.logo || movie.image || movie.poster || (movie.info && movie.info.poster);

  // ✅ ดึง description จาก info.description ถ้ามี
  const description = (movie.info && movie.info.description) ? movie.info.description : (movie.info || "");

  return `
    <div class="flex-shrink-0 w-[150px] bg-gray-800 rounded-xl overflow-hidden shadow-lg hover:shadow-blue-500/30 transition duration-300 poster-card group cursor-pointer">
      <div class="relative">
        <a href="${watchUrl}">
          <img src="${poster || 'https://via.placeholder.com/150x225?text=No+Image'}"
               onerror="this.onerror=null;this.src='https://via.placeholder.com/150x225?text=No+Image';"
               alt="${movieName}"
               class="w-full h-[225px] object-cover transition duration-500">
        </a>
      </div>
      <div class="p-2">
        <p class="text-sm font-semibold truncate" title="${movieName}">${movieName}</p>
        <p class="text-xs text-gray-400">${description}</p>
      </div>
    </div>
  `;
}

function createMovieSection(title, movies) {
  const cardsHtml = movies.map(createMovieCard).join("");
  return `
    <section class="mb-10">
      <h3 class="text-3xl font-bold border-l-4 border-red-600 pl-3 mb-6">${title}</h3>
      <div class="horizontal-scroll-container flex space-x-2 overflow-x-auto pb-4 -mx-4 px-4 sm:mx-0 sm:px-0">
        ${cardsHtml}
      </div>
    </section>
  `;
}

// --- [ SAFE JSON PARSER ] ---
async function fetchMovies(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`โหลดไม่สำเร็จ: ${res.status} ${res.statusText}`);
    }
    const rawText = await res.text();

    const start = rawText.indexOf("[");
    const end = rawText.lastIndexOf("]") + 1;

    if (start >= 0 && end > start) {
      const jsonText = rawText.slice(start, end).trim();
      try {
        return JSON.parse(jsonText);
      } catch (e) {
        console.error("Parse error:", e, "jsonText=", jsonText);
        throw e;
      }
    }

    console.error("Response ไม่ใช่ JSON array:", rawText);
    throw new Error("Response ไม่มี JSON array");
  } catch (err) {
    console.error("FetchMovies Error:", err);
    throw err;
  }
}

// --- [ LOAD MOVIES ] ---
async function loadAllMovies() {
  const container = document.getElementById("movie-sections-container");
  const searchResultContainer = document.getElementById("search-result-container");

  searchResultContainer.innerHTML = "";
  searchResultContainer.style.display = "none";
  container.style.display = "block";

  container.innerHTML = '<p class="text-gray-400">กำลังโหลดรายการหนังทั้งหมด...</p>';
  let allSectionsHtml = "";
  allMoviesByTitle = {};

  try {
    // ✅ โหลดจาก Parser เพียงครั้งเดียว
    const movies = await fetchMovies("https://parser--zeroarm151.replit.app/xi.php?file=https://raw.githubusercontent.com/Digital1ID/digital1id.github.io/refs/heads/main/m3u/movie/new.txt");
    allMovies = movies;

    // ✅ สร้าง section ตาม category
    const groups = [...new Set(allMovies.map(m => m.category || "อื่นๆ"))];
    for (const group of groups) {
      const moviesInGroup = allMovies.filter(m => (m.category || "อื่นๆ") === group);
      if (moviesInGroup.length > 0) {
        allSectionsHtml += createMovieSection(group, moviesInGroup);
        moviesInGroup.forEach(movie => {
          const nameKey = (movie.name || "").toLowerCase();
          if (!allMoviesByTitle[nameKey]) {
            allMoviesByTitle[nameKey] = movie;
          }
        });
      }
    }

    if (allSectionsHtml) {
      container.innerHTML = allSectionsHtml;
      originalSectionsHtml = allSectionsHtml;
    } else {
      container.innerHTML = "<p class='text-blue-500'>ไม่พบรายการหนัง</p>";
      originalSectionsHtml = "";
    }
  } catch (error) {
    console.error("Error loading movies:", error);
    container.innerHTML = "<p class='text-blue-500'>❌ เกิดข้อผิดพลาดในการโหลดข้อมูล</p>";
  }
}

// --- [ SEARCH ] ---
function searchMovies() {
  const query = document.getElementById("search-input").value.toLowerCase();
  const container = document.getElementById("movie-sections-container");
  const searchResultContainer = document.getElementById("search-result-container");

  if (!query || query.length < 2) {
    searchResultContainer.innerHTML = "";
    searchResultContainer.style.display = "none";
    container.style.display = "block";
    container.innerHTML = originalSectionsHtml || "";
    return;
  }

  container.style.display = "none";
  searchResultContainer.style.display = "block";

  const filteredMovies = Object.values(allMoviesByTitle).filter(movie => {
    const name = (movie.name || "").toLowerCase();
    const infoText = (movie.info && movie.info.description ? movie.info.description : movie.info || "").toLowerCase();
    return name.includes(query) || infoText.includes(query);
  });

  if (filteredMovies.length > 0) {
    const searchTitle = `🔍 ผลการค้นหา "${document.getElementById("search-input").value}" (${filteredMovies.length} รายการ)`;
    const searchSection = createMovieSection(searchTitle, filteredMovies);
    searchResultContainer.innerHTML = searchSection;
  } else {
    searchResultContainer.innerHTML = `<p class="text-blue-500 text-2xl mt-8">ไม่พบรายการหนังที่ตรงกับ "${document.getElementById("search-input").value}"</p>`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.title.includes("หน้าหลัก")) {
    loadAllMovies();
  }
});
