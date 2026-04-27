//category-v2.js

let allMovies = [];
let currentPage = 1;
const ITEMS_PER_PAGE = 48;
let currentGroup = "";

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

    // ✅ ใช้ poster จาก info.poster ถ้ามี
    const poster = movie.logo || movie.image || movie.poster || (movie.info && movie.info.poster);

    // ✅ ใช้ description จาก info.description ถ้ามี
    const description = (movie.info && movie.info.description) ? movie.info.description : (movie.info || "");

    return `
        <div class="flex-shrink-0 w-[150px] bg-gray-800 rounded-xl overflow-hidden shadow-lg hover:shadow-red-500/30 transition duration-300 poster-card group cursor-pointer">
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

function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

function renderPagination(totalItems, totalPages) {
    const paginationContainer = document.getElementById("pagination-container");
    let paginationHtml = "";

    if (totalPages <= 1) {
        paginationContainer.innerHTML = "";
        return;
    }

    paginationHtml += '<nav class="flex justify-center space-x-2">';

    const prevDisabled = currentPage === 1 ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-700";
    paginationHtml += `<button onclick="changePage(${currentPage - 1})" class="py-2 px-4 rounded-lg bg-blue-600 ${prevDisabled}" ${currentPage === 1 ? "disabled" : ""}>« ก่อนหน้า</button>`;

    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        paginationHtml += `<button onclick="changePage(1)" class="py-2 px-4 rounded-lg bg-gray-700 hover:bg-blue-700">1</button>`;
        if (startPage > 2) paginationHtml += `<span class="py-2 px-1 text-gray-400">...</span>`;
    }

    for (let i = startPage; i <= endPage; i++) {
        const activeClass = i === currentPage ? "bg-blue-800" : "bg-gray-700 hover:bg-blue-700";
        paginationHtml += `<button onclick="changePage(${i})" class="py-2 px-4 rounded-lg ${activeClass}">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) paginationHtml += `<span class="py-2 px-1 text-gray-400">...</span>`;
        paginationHtml += `<button onclick="changePage(${totalPages})" class="py-2 px-4 rounded-lg bg-gray-700 hover:bg-blue-700">${totalPages}</button>`;
    }

    const nextDisabled = currentPage === totalPages ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-700";
    paginationHtml += `<button onclick="changePage(${currentPage + 1})" class="py-2 px-4 rounded-lg bg-blue-600 ${nextDisabled}" ${currentPage === totalPages ? "disabled" : ""}>ถัดไป »</button>`;

    paginationHtml += "</nav>";
    paginationContainer.innerHTML = paginationHtml;
}

function displayMovies(moviesToDisplay, title) {
    const listContainer = document.getElementById("movie-list-grid");
    const titleElement = document.getElementById("category-title");

    const totalItems = moviesToDisplay.length;
    const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = Math.min(startIndex + ITEMS_PER_PAGE, totalItems);

    const limitedMovies = moviesToDisplay.slice(startIndex, endIndex);

    if (limitedMovies.length > 0) {
        const cardsHtml = limitedMovies.map(createMovieCard).join("");
        listContainer.innerHTML = cardsHtml;
        titleElement.textContent = `${title} (หน้า ${currentPage}/${totalPages} | รวม ${totalItems} รายการ)`;
    } else {
        listContainer.innerHTML = `<p class="text-blue-500 col-span-full">ไม่พบรายการหนัง!</p>`;
        titleElement.textContent = `${title} (0 รายการ)`;
    }

    renderPagination(totalItems, totalPages);
}

function changePage(newPage) {
    const totalPages = Math.ceil(allMovies.length / ITEMS_PER_PAGE);
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        document.getElementById("search-input").value = "";
        displayMovies(allMovies, currentGroup);
        window.scrollTo({ top: 0, behavior: "smooth" });
    }
}

async function loadCategory(groupName) {
    currentGroup = groupName;
    currentPage = 1;
    const listContainer = document.getElementById("movie-list-grid");
    listContainer.innerHTML = '<p class="text-gray-400 col-span-full">กำลังโหลดรายการ...</p>';
    document.getElementById("pagination-container").innerHTML = "";
    document.getElementById("search-input").value = "";

    try {
        const response = await fetch(`https://parser--zeroarm151.replit.app/xi.php?file=https://raw.githubusercontent.com/Digital1ID/digital1id.github.io/refs/heads/main/m3u/movie/new.txt`);
        if (!response.ok) throw new Error("ไม่สามารถโหลดข้อมูลจาก Parser ได้");
        const movies = await response.json();

        // ✅ กรองเฉพาะ category ที่เลือก
        allMovies = movies.filter(m => (m.category || "อื่นๆ") === groupName);
    } catch (error) {
        console.error("Error loading movies:", error);
        document.getElementById("category-title").textContent = groupName;
        listContainer.innerHTML = `<p class="text-blue-500 col-span-full">❌ เกิดข้อผิดพลาดในการโหลดรายการ ${groupName}</p>`;
        return;
    }

    displayMovies(allMovies, groupName);
}

function searchMovies() {
    const query = document.getElementById("search-input").value.toLowerCase();
    if (!query) {
        currentPage = 1;
        displayMovies(allMovies, currentGroup);
        return;
    }

    const filteredMovies = allMovies.filter(movie => {
        const name = (movie.name || "").toLowerCase();
        const infoText = (movie.info && movie.info.description ? movie.info.description : movie.info || "").toLowerCase();
        return name.includes(query) || infoText.includes(query);
    });

    currentPage = 1;
    displayMovies(filteredMovies, `ผลการค้นหา "${query}" ใน ${currentGroup}`);
}

document.addEventListener("DOMContentLoaded", () => {
    const groupName = getQueryParam("cat");
    if (groupName) {
        loadCategory(groupName);
    } else {
        loadCategory("หนังใหม่"); // ค่าเริ่มต้น
    }
});
