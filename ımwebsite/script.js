document.addEventListener("DOMContentLoaded", () => {

    // --- 1. ZARİF KAYDIRMA (SCROLL REVEAL) - ZAMANLAMASI KUSURSUZ VERSİYON ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            } else {
                entry.target.classList.remove('visible');
            }
        });
    }, {
        threshold: 0.20,
        rootMargin: "0px 0px -25% 0px"
    });

    // Sadece bir kere çağrılması yeterli
    document.querySelectorAll('.project-block, .scroll-reveal').forEach(block => {
        observer.observe(block);
    });

    // --- 2. YAPAY ZEKA (KI) BOOT TERMİNALİ ---
    const terminalText = "[SYSTEM]: KI-Module online... Sensoren aktiv... Gründlichkeit optimiert.";
    const terminalElement = document.getElementById("ai-terminal");
    let i = 0;

    function typeWriter() {
        if (i < terminalText.length) {
            terminalElement.innerHTML = terminalText.substring(0, i+1) + '<span class="terminal-cursor"></span>';
            i++;
            setTimeout(typeWriter, 40);
        } else {
            terminalElement.innerHTML = terminalText + '<span class="terminal-cursor"></span>';
        }
    }
    setTimeout(typeWriter, 1500);

    // --- 3. 3D MEKATRONİK TILT (EĞİLME) EFEKTİ ---
    const imageBoxes = document.querySelectorAll('.project-image-box');

    imageBoxes.forEach(box => {
        box.addEventListener('mousemove', (e) => {
            const rect = box.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -12;
            const rotateY = ((x - centerX) / centerX) * 12;

            box.style.transition = 'none';
            box.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        });

        box.addEventListener('mouseleave', () => {
            box.style.transition = 'transform 0.5s ease-out';
            box.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
        });
    });

});