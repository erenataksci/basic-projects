/**
 * Web Öğreniyorum Projesi - Ana JavaScript Dosyası
 * Bu dosya, sitenin tüm interaktif özelliklerini yönetir.
 * Her bir özellik, kendi fonksiyonu içinde izole edilmiştir.
 */

'use strict'; // Kod kalitesi için katı modu etkinleştirir

// --- ÖZELLİK 1: TEMA DEĞİŞTİRİCİ (KOYU/AÇIK MOD) ---
function initThemeSwitcher() {
    const temaBtn = document.getElementById("temaBtn");
    if (!temaBtn) return; // Buton yoksa fonksiyonu durdur

    let koyuMod = localStorage.getItem("koyuMod") === "true";

    const applyTheme = () => {
        if (koyuMod) {
            document.body.classList.add('dark-mode');
            temaBtn.textContent = "Açık Mod";
        } else {
            document.body.classList.remove('dark-mode');
            temaBtn.textContent = "Koyu Mod";
        }
    };

    temaBtn.addEventListener("click", () => {
        koyuMod = !koyuMod;
        localStorage.setItem("koyuMod", koyuMod);
        applyTheme();
    });

    applyTheme(); // Sayfa yüklendiğinde temayı uygula
}

// --- ÖZELLİK 2: RESİM BÜYÜTME MODALI (Dinamik Olarak Oluşturulan) ---
function initImageModal() {
    // 1. Modal elementlerini JavaScript içinde oluştur
    const modal = document.createElement('div');
    modal.id = 'modal';

    const modalImg = document.createElement('img');
    modalImg.id = 'modalImg';

    modal.appendChild(modalImg);
    document.body.appendChild(modal); // Oluşturulan modal'ı body'ye ekle

    // 2. Tıklanacak resimleri seç
    const allImages = document.querySelectorAll("main img, .card img");

    allImages.forEach(img => {
        img.addEventListener("click", (e) => {
            e.stopPropagation();
            modal.style.display = "flex";
            modalImg.src = img.src;
        });
    });

    // 3. Kapatma olayını ekle
    modal.addEventListener("click", () => {
        modal.style.display = "none";
    });
}

// --- ÖZELLİK 3: EĞİTİM SAYFASI KENAR MENÜSÜ (SIDEBAR) ---
function initSidebarNav() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return; // Sidebar yoksa fonksiyonu durdur

    const topicLinks = sidebar.querySelectorAll('.topic-link');
    const contentSections = document.querySelectorAll('.content-section');
    const mainContent = document.querySelector('.main-content');

    topicLinks.forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault();

            const topicToShow = link.getAttribute('data-topic');

            topicLinks.forEach(l => l.classList.remove('active'));
            contentSections.forEach(s => s.classList.remove('active'));

            link.classList.add('active');
            const sectionToShow = document.querySelector(`.content-section[data-topic="${topicToShow}"]`);

            if (sectionToShow) {
                sectionToShow.classList.add('active');

                // İyileştirme: Yeni bölüme geçildiğinde ana içerik alanının başına scroll yap
                if (mainContent) {
                    mainContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
}

// --- ÖZELLİK 4: KOD BLOKLARINA KOPYALA BUTONU EKLEME ---
function initCopyButtons() {
    const codeBlocks = document.querySelectorAll('pre');
    if (codeBlocks.length === 0) return; // Kod bloğu yoksa durdur

    codeBlocks.forEach(block => {
        const codeElement = block.querySelector('code');
        if (codeElement) {
            const copyButton = document.createElement('button');
            copyButton.className = 'btn-copy';
            copyButton.textContent = 'Kopyala';
            block.appendChild(copyButton);

            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(codeElement.innerText).then(() => {
                    copyButton.textContent = 'Kopyalandı!';
                    setTimeout(() => {
                        copyButton.textContent = 'Kopyala';
                    }, 2000);
                }).catch(err => {
                    console.error('Kopyalama başarısız oldu.', err);
                });
            });
        }
    });
}

// --- ANA BAŞLATMA FONKSİYONU ---
document.addEventListener('DOMContentLoaded', () => {
    initThemeSwitcher();
    initImageModal();
    initSidebarNav();
    initCopyButtons();
});